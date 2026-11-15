"""Secrets 的值：管理 Portal 保存在資料目錄的 secrets.json（M4），M8 起加密存放（ADR 0025）。

- 每個值用 AES-256-GCM 加密（``cryptography``）：隨機 12 位元組 nonce，名稱當成附加資料（換了
  名稱就解不開），存成 ``{"cipher": base64(nonce + 密文), "updatedAt": …}``。
- 金鑰：環境變數 ``RPA_SECRETS_KEY``（base64 的 32 位元組）優先；沒有時用資料目錄的
  ``secrets.key``，第一次需要時自動產生（只有本人能讀寫 0600）。**備份資料目錄時金鑰要一起備份**，
  金鑰不見了值就解不開（名稱還在，重新設定即可）。
- 舊的明文（M8 之前的 ``{"value": …}``）在啟動時（:meth:`SecretStore.migrate`）換成密文。
- 檔案本身仍只有本人能讀寫（0600）；頁面與 API 只看得到名稱與更新時間，永遠不回傳值。
- 執行時把場景與登入角色用到的值交給 rpa-runner；沒有保存的名稱再從同名的環境變數找。
"""

import base64
import binascii
import json
import logging
import os
import re
import secrets
import threading
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Final, cast

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from rpa_server.domain import now

__all__ = ["KEY_ENV", "SECRET_NAME", "SecretInfo", "SecretKeyError", "SecretStore"]

SECRET_NAME: Final = re.compile(r"[A-Z][A-Z0-9_]{0,63}")
"""Secrets 名稱的規則（與 DSL 相同）：大寫英文字母、數字與 _，例如 ERP_PASSWORD。"""
KEY_ENV: Final = "RPA_SECRETS_KEY"
"""金鑰的環境變數：base64（標準或網址安全）的 32 位元組。"""
_NONCE: Final = 12
_KEY_PROBLEM: Final = f"{KEY_ENV}（或 secrets.key）要是 base64 的 32 位元組"

logger = logging.getLogger("rpa_server.secrets")


class SecretKeyError(ValueError):
    """金鑰的環境變數寫錯（不是 base64 的 32 位元組）。"""


@dataclass(frozen=True, slots=True)
class SecretInfo:
    name: str
    updated_at: datetime
    readable: bool = True
    """金鑰對得上、解得開；False 時要重新設定（例如金鑰檔不見了）。"""

    def to_json(self) -> dict[str, object]:
        return {
            "name": self.name,
            "updatedAt": self.updated_at.isoformat(timespec="seconds"),
            "readable": self.readable,
        }


def _decode_key(text: str) -> bytes:
    cleaned = text.strip()
    padded = cleaned + "=" * (-len(cleaned) % 4)
    try:
        key = base64.b64decode(padded.replace("-", "+").replace("_", "/"), validate=True)
    except (binascii.Error, ValueError) as error:
        raise SecretKeyError(_KEY_PROBLEM) from error
    if len(key) != 32:
        raise SecretKeyError(_KEY_PROBLEM)
    return key


class SecretStore:
    def __init__(
        self, path: Path, key_path: Path | None = None, environ: Mapping[str, str] | None = None
    ) -> None:
        self.path = path
        self.key_path = key_path or path.with_name("secrets.key")
        self._environ = os.environ if environ is None else environ
        self._lock = threading.Lock()
        self._key: bytes | None = None

    # ------------------------------------------------------------ 金鑰

    def _cipher(self) -> AESGCM:
        if self._key is None:
            self._key = self._load_key()
        return AESGCM(self._key)

    def _load_key(self) -> bytes:
        given = self._environ.get(KEY_ENV, "").strip()
        if given:
            return _decode_key(given)
        try:
            return _decode_key(self.key_path.read_text(encoding="ascii"))
        except FileNotFoundError:
            pass
        key = secrets.token_bytes(32)
        self.key_path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(self.key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="ascii") as handle:
            handle.write(base64.urlsafe_b64encode(key).decode("ascii") + "\n")
        if os.name != "nt":
            self.key_path.chmod(0o600)
        return key

    def _seal(self, name: str, value: str) -> str:
        nonce = secrets.token_bytes(_NONCE)
        sealed = self._cipher().encrypt(nonce, value.encode("utf-8"), name.encode("utf-8"))
        return base64.b64encode(nonce + sealed).decode("ascii")

    def _open(self, name: str, item: Mapping[str, str]) -> str | None:
        """解開一個值；舊的明文照樣回傳；解不開（金鑰不對）時是 None。"""
        cipher = item.get("cipher")
        if cipher is None:
            return item.get("value", "")
        try:
            raw = base64.b64decode(cipher, validate=True)
            plain = self._cipher().decrypt(raw[:_NONCE], raw[_NONCE:], name.encode("utf-8"))
        except (binascii.Error, ValueError, InvalidTag):
            return None
        return plain.decode("utf-8")

    # ------------------------------------------------------------ 檔案

    def _read(self) -> dict[str, dict[str, str]]:
        try:
            data: object = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}
        return cast("dict[str, dict[str, str]]", data) if isinstance(data, dict) else {}

    def _write(self, data: Mapping[str, Mapping[str, str]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_name(f".{self.path.name}.tmp")
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
        if os.name != "nt":
            temporary.chmod(0o600)
        temporary.replace(self.path)

    def migrate(self) -> int:
        """把舊的明文換成密文（啟動時呼叫；也先讀好金鑰，寫錯時馬上知道）；回傳換了幾個。"""
        with self._lock:
            self._cipher()
            data = self._read()
            plain = [name for name, item in data.items() if "cipher" not in item]
            if not plain:
                return 0
            for name in plain:
                item = data[name]
                data[name] = {
                    "cipher": self._seal(name, item.get("value", "")),
                    "updatedAt": item.get("updatedAt") or now().isoformat(timespec="seconds"),
                }
            self._write(data)
        return len(plain)

    def names(self) -> list[SecretInfo]:
        with self._lock:
            data = self._read()
            return [
                SecretInfo(
                    name,
                    datetime.fromisoformat(item.get("updatedAt") or now().isoformat()),
                    readable=self._open(name, item) is not None,
                )
                for name, item in sorted(data.items())
            ]

    def has(self, name: str) -> bool:
        with self._lock:
            return name in self._read()

    def set(self, name: str, value: str) -> SecretInfo:
        moment = now()
        with self._lock:
            data = self._read()
            data[name] = {
                "cipher": self._seal(name, value),
                "updatedAt": moment.isoformat(timespec="seconds"),
            }
            self._write(data)
        return SecretInfo(name, moment.replace(microsecond=0))

    def delete(self, name: str) -> bool:
        with self._lock:
            data = self._read()
            if name not in data:
                return False
            del data[name]
            self._write(data)
            return True

    def values(self) -> dict[str, str]:
        """全部解得開的值：只交給執行用，不要顯示或寫進日誌。解不開的不給（執行時當成沒設定）。"""
        found: dict[str, str] = {}
        with self._lock:
            for name, item in self._read().items():
                value = self._open(name, item)
                if value is None:
                    logger.warning("Secret %s 用目前的金鑰解不開，執行時當成沒有設定", name)
                    continue
                found[name] = value
        return found
