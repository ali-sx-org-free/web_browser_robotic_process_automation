"""Secrets 加密存放（M8，ADR 0025）：不需要 FastAPI 與 SQLAlchemy。"""

import base64
import json
import os
from pathlib import Path

import pytest

from rpa_server.secret_store import KEY_ENV, SecretKeyError, SecretStore


def test_values_are_encrypted_with_an_auto_generated_key(tmp_path: Path) -> None:
    store = SecretStore(tmp_path / "secrets.json", environ={})
    store.set("ERP_PASSWORD", "很秘密的值")
    raw = (tmp_path / "secrets.json").read_text(encoding="utf-8")
    assert "很秘密的值" not in raw
    assert "ERP_PASSWORD" in raw
    item = json.loads(raw)["ERP_PASSWORD"]
    assert set(item) == {"cipher", "updatedAt"}
    key = tmp_path / "secrets.key"
    assert len(base64.urlsafe_b64decode(key.read_text(encoding="ascii").strip())) == 32
    if os.name != "nt":
        assert key.stat().st_mode & 0o777 == 0o600
        assert (tmp_path / "secrets.json").stat().st_mode & 0o777 == 0o600
    # 另一個實例（重新啟動）用同一個金鑰檔解得開
    again = SecretStore(tmp_path / "secrets.json", environ={})
    assert again.values() == {"ERP_PASSWORD": "很秘密的值"}
    assert [info.readable for info in again.names()] == [True]


def test_ciphertext_is_bound_to_the_name(tmp_path: Path) -> None:
    store = SecretStore(tmp_path / "secrets.json", environ={})
    store.set("A_KEY", "one")
    data = json.loads((tmp_path / "secrets.json").read_text(encoding="utf-8"))
    data["B_KEY"] = data["A_KEY"]  # 把密文搬到別的名稱下：解不開
    (tmp_path / "secrets.json").write_text(json.dumps(data), encoding="utf-8")
    assert store.values() == {"A_KEY": "one"}
    assert {info.name: info.readable for info in store.names()} == {"A_KEY": True, "B_KEY": False}


def test_plain_values_are_migrated(tmp_path: Path) -> None:
    path = tmp_path / "secrets.json"
    path.write_text(
        json.dumps({"OLD": {"value": "明文", "updatedAt": "2026-10-01T00:00:00+00:00"}}),
        encoding="utf-8",
    )
    store = SecretStore(path, environ={})
    assert store.values() == {"OLD": "明文"}  # 遷移前照樣讀得到
    assert store.migrate() == 1
    assert "明文" not in path.read_text(encoding="utf-8")
    assert store.values() == {"OLD": "明文"}
    assert store.names()[0].updated_at.isoformat() == "2026-10-01T00:00:00+00:00"
    assert store.migrate() == 0


def test_key_from_the_environment(tmp_path: Path) -> None:
    key = base64.b64encode(bytes(range(32))).decode()
    store = SecretStore(tmp_path / "secrets.json", environ={KEY_ENV: key})
    store.set("TOKEN", "x")
    assert not (tmp_path / "secrets.key").exists()
    # 換了金鑰：名稱還在，值解不開（執行時當成沒設定）
    other = SecretStore(tmp_path / "secrets.json", environ={})
    assert other.values() == {}
    assert [info.readable for info in other.names()] == [False]
    with pytest.raises(SecretKeyError, match=KEY_ENV):
        SecretStore(tmp_path / "secrets.json", environ={KEY_ENV: "短"}).migrate()
