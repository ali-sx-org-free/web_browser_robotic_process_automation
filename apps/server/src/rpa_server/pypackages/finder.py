"""找到需要的套件（ADR 0027）：名稱查詢、import 名稱對照、常用套件清單、場景用到的模組。

PyPI 沒有給程式用的搜尋（2020 年起關閉），所以從這幾個方向找到名稱，最後都用名稱查詢確認：

- 名稱查詢：套件來源的 simple API（PEP 691 的 JSON；鏡像只有 HTML 時讀 HTML）取得版本與每個
  檔案的平台、大小、上架時間，再取那一版 wheel 的 METADATA（PEP 658）看簡介、授權、首頁與依賴。
- import 名稱：很多套件的名稱和 import 不同（:data:`IMPORT_NAMES`）。
- 常用套件清單：依 RPA 用途分類的建議（:data:`COMMON`），說明在介面的翻譯檔。
- 場景用到的模組：用 ast 讀運行環境模式的場景的 .py 檔（:func:`imported_modules`）。
"""

import ast
import contextlib
import json
import re
import sys
import urllib.error
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from html.parser import HTMLParser
from typing import Final, cast
from urllib.parse import urljoin

from rpa_runner.pypackages import normalize
from rpa_server.pypackages.locks import (
    PLATFORMS,
    Wheel,
    best_wheel,
    is_prerelease,
    version_key,
    wheel_version,
)
from rpa_server.pypackages.sources import SIMPLE_JSON, DownloadError, Http, Source

__all__ = [
    "BLOCKED",
    "COMMON",
    "IMPORT_NAMES",
    "CommonPackage",
    "PackageLookupError",
    "SceneSource",
    "blocked_reason",
    "imported_modules",
    "local_modules",
    "lookup",
    "parse_metadata",
]

IMPORT_NAMES: Final = {
    "docx": "python-docx",
    "pptx": "python-pptx",
    "cv2": "opencv-python-headless",
    "yaml": "PyYAML",
    "PIL": "pillow",
    "fitz": "PyMuPDF",
    "pymupdf": "PyMuPDF",
    "dateutil": "python-dateutil",
    "bs4": "beautifulsoup4",
    "sklearn": "scikit-learn",
    "win32api": "pywin32",
    "win32com": "pywin32",
    "win32con": "pywin32",
    "win32gui": "pywin32",
    "win32print": "pywin32",
    "pythoncom": "pywin32",
    "pywintypes": "pywin32",
    "Crypto": "pycryptodome",
    "jwt": "PyJWT",
    "dotenv": "python-dotenv",
    "serial": "pyserial",
    "OpenSSL": "pyOpenSSL",
    "MySQLdb": "mysqlclient",
    "pymysql": "PyMySQL",
    "psycopg2": "psycopg2-binary",
    "barcode": "python-barcode",
    "opencc": "opencc-python-reimplemented",
    "smbclient": "smbprotocol",
    "attr": "attrs",
    "magic": "python-magic",
    "zmq": "pyzmq",
    "Levenshtein": "levenshtein",
    "google": "protobuf",
}
"""import 的名稱 → 套件名稱（不一樣的常見例子；一樣的不用列）。"""

BLOCKED: Final = frozenset(
    {"pip", "setuptools", "wheel", "uv", "distribute", "virtualenv", "pip-tools", "playwright"}
)
"""不能加的套件：安裝工具（Worker 上不現場安裝）、playwright（運行環境模式不開瀏覽器）。"""


def blocked_reason(name: str) -> str | None:
    """不能加的原因（錯誤代碼）；可以加時回傳 None。"""
    key = normalize(name)
    if key in BLOCKED:
        return "blocked_tool"
    if key.startswith(("rpa-", "rpa_")) or key == "rpa":
        return "blocked_rpa"
    if key.replace("-", "_") in sys.stdlib_module_names:
        return "blocked_stdlib"
    return None


@dataclass(frozen=True, slots=True)
class CommonPackage:
    name: str
    category: str
    platforms: tuple[str, ...] = ()
    """只有這些系統有（建議加的時候限定平台）。"""


COMMON: Final = (
    CommonPackage("python-pptx", "office"),
    CommonPackage("xlwings", "office", ("windows", "macos")),
    CommonPackage("tabulate", "office"),
    CommonPackage("pdfplumber", "pdf"),
    CommonPackage("PyMuPDF", "pdf"),
    CommonPackage("reportlab", "pdf"),
    CommonPackage("pillow", "image"),
    CommonPackage("opencv-python-headless", "image"),
    CommonPackage("qrcode", "image"),
    CommonPackage("python-barcode", "image"),
    CommonPackage("PyMySQL", "database"),
    CommonPackage("psycopg2-binary", "database"),
    CommonPackage("oracledb", "database"),
    CommonPackage("pyodbc", "database"),
    CommonPackage("paramiko", "transfer"),
    CommonPackage("smbprotocol", "transfer"),
    CommonPackage("exchangelib", "transfer"),
    CommonPackage("py7zr", "archive"),
    CommonPackage("pyzipper", "archive"),
    CommonPackage("rarfile", "archive"),
    CommonPackage("jieba", "chinese"),
    CommonPackage("opencc-python-reimplemented", "chinese"),
    CommonPackage("pypinyin", "chinese"),
    CommonPackage("pywin32", "windows", ("windows",)),
    CommonPackage("pywinauto", "windows", ("windows",)),
    CommonPackage("uiautomation", "windows", ("windows",)),
)
"""常用套件（ADR 0027 的「找到需要的套件」）；每項的用途與限制在翻譯檔的
``pypackages.common_<正規化名稱>``。"""
COMMON_CATEGORIES: Final = (
    "office",
    "pdf",
    "image",
    "database",
    "transfer",
    "archive",
    "chinese",
    "windows",
)


# ---------------------------------------------------------------- 場景用到的模組


@dataclass(frozen=True, slots=True)
class SceneSource:
    """一個運行環境模式的場景版本的 Python 檔（掃描 import 用）。"""

    scene_id: str
    name: str
    domain_id: str | None
    number: int
    published: bool
    files: Mapping[str, str]
    """相對路徑 → 內容（只有 .py 與其他文字檔）。"""


def imported_modules(source: str) -> set[str]:
    """一個 .py 檔 import 的最上層模組（相對 import 不算）；語法錯誤時是空的。"""
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
        return set()
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            found.add(node.module.split(".", 1)[0])
    return found


def local_modules(files: Iterable[str]) -> set[str]:
    """場景自己的模組：最上層的 .py 檔與資料夾的名稱。"""
    found: set[str] = set()
    for path in files:
        parts = path.split("/")
        if len(parts) == 1 and path.endswith(".py"):
            found.add(path.removesuffix(".py"))
        elif len(parts) > 1:
            found.add(parts[0])
    return found


def scene_imports(scene: SceneSource) -> set[str]:
    """場景 import 的第三方模組：不含標準函式庫、rpa_script 與場景自己的模組。"""
    found: set[str] = set()
    for path, content in scene.files.items():
        if path.endswith(".py"):
            found |= imported_modules(content)
    own = local_modules(scene.files)
    return {
        name
        for name in found
        if name not in sys.stdlib_module_names
        and name not in own
        and name not in ("rpa_script", "__future__")
    }


# ---------------------------------------------------------------- 名稱查詢


class PackageLookupError(Exception):
    """查不到這個套件；``code`` 是錯誤代碼（not_found、unreachable）。"""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(detail or code)
        self.code = code
        self.detail = detail


@dataclass(frozen=True, slots=True)
class _File:
    filename: str
    url: str
    sha256: str
    size: int | None
    upload_time: str | None
    yanked: bool
    metadata: bool
    """有 PEP 658 的 METADATA 檔。"""


class _Links(HTMLParser):
    """PEP 503 的 HTML simple 頁面：每個 <a> 的 href 與 data-* 屬性。"""

    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self.links.append({key: value or "" for key, value in attrs})


def _files(http: Http, source: Source, key: str) -> tuple[str, list[_File]]:
    url = f"{source.simple}/{key}/"
    try:
        with http.open(url, headers={"Accept": f"{SIMPLE_JSON}, text/html;q=0.1"}) as response:
            content_type = str(response.headers.get("Content-Type", ""))
            body = response.read(16 << 20)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            raise PackageLookupError("not_found") from error
        raise PackageLookupError("unreachable", f"{url}: {error}") from error
    except (OSError, urllib.error.URLError, TimeoutError) as error:
        raise PackageLookupError("unreachable", f"{url}: {error}") from error
    files: list[_File] = []
    name = key
    if "json" in content_type:
        data = cast("dict[str, object]", json.loads(body))
        name = str(data.get("name") or key)
        for raw in cast("list[dict[str, object]]", data.get("files") or []):
            hashes = cast("dict[str, object]", raw.get("hashes") or {})
            size = raw.get("size")
            metadata = raw.get("core-metadata", raw.get("dist-info-metadata"))
            files.append(
                _File(
                    filename=str(raw.get("filename") or ""),
                    url=urljoin(url, str(raw.get("url") or "")),
                    sha256=str(hashes.get("sha256") or ""),
                    size=size if isinstance(size, int) else None,
                    upload_time=str(raw["upload-time"]) if raw.get("upload-time") else None,
                    yanked=bool(raw.get("yanked")),
                    metadata=bool(metadata),
                )
            )
        return name, files
    parser = _Links()
    parser.feed(body.decode("utf-8", errors="replace"))
    for link in parser.links:
        href = link.get("href", "")
        filename = href.split("#", 1)[0].rsplit("/", 1)[-1]
        digest = re.search(r"sha256=([0-9a-f]{64})", href)
        files.append(
            _File(
                filename=filename,
                url=urljoin(url, href.split("#", 1)[0]),
                sha256=digest.group(1) if digest else "",
                size=None,
                upload_time=None,
                yanked="data-yanked" in link,
                metadata=bool(
                    link.get("data-core-metadata") or link.get("data-dist-info-metadata")
                ),
            )
        )
    return name, files


def parse_metadata(text: str) -> dict[str, object]:
    """wheel 的 METADATA（只看開頭的欄位）：簡介、授權、首頁、依賴、Python 版本。"""
    summary = license_text = home = requires_python = ""
    urls: list[str] = []
    requires: list[str] = []
    classifiers: list[str] = []
    for line in text.splitlines():
        if not line.strip():
            break
        key, _, value = line.partition(":")
        value = value.strip()
        lower = key.lower()
        if lower == "summary":
            summary = value
        elif lower == "license-expression" or (lower == "license" and not license_text):
            license_text = value.splitlines()[0][:200] if value else license_text
        elif lower == "home-page":
            home = value
        elif lower == "project-url":
            urls.append(value)
        elif lower == "requires-dist" and "extra ==" not in value:
            requires.append(value.split(";", 1)[0].strip())
        elif lower == "requires-python":
            requires_python = value
        elif lower == "classifier" and value.startswith("License ::"):
            classifiers.append(value.rsplit("::", 1)[-1].strip())
    if not home:
        for item in urls:
            label, _, link = item.partition(",")
            if label.strip().lower() in ("homepage", "home", "source", "repository"):
                home = link.strip()
                break
    if not license_text and classifiers:
        license_text = ", ".join(classifiers)
    return {
        "summary": summary,
        "license": license_text,
        "homepage": home if home.startswith(("https://", "http://")) else "",
        "requires": requires,
        "requiresPython": requires_python,
    }


def _days_since(stamp: str | None, now: datetime) -> float | None:
    if not stamp:
        return None
    with contextlib.suppress(ValueError):
        moment = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        if moment.tzinfo is None:
            moment = moment.replace(tzinfo=UTC)
        return (now - moment).total_seconds() / 86400
    return None


def lookup(
    http: Http,
    source: Source,
    query: str,
    *,
    cooldown_days: int = 7,
    now: datetime | None = None,
) -> dict[str, object]:
    """查一個套件：最新版本、冷卻期外的版本、每個平台的 wheel 與大小、METADATA。"""
    moment = now or datetime.now(UTC)
    key = normalize(query.strip())
    if not key:
        raise PackageLookupError("not_found")
    name, files = _files(http, source, key)
    by_version: dict[str, list[_File]] = {}
    for item in files:
        parsed = wheel_version(item.filename)
        if parsed is not None and not item.yanked:  # 原始碼包不收（ADR 0027：只收 wheel）
            by_version.setdefault(parsed[1], []).append(item)
    if not by_version:
        raise PackageLookupError("no_wheels" if files else "not_found")
    ordered = sorted(by_version, key=version_key, reverse=True)
    stable = [version for version in ordered if not is_prerelease(version)] or ordered
    latest = stable[0]

    def uploaded(version: str) -> str | None:
        times = [item.upload_time for item in by_version[version] if item.upload_time]
        return max(times) if times else None

    allowed = next(
        (
            version
            for version in stable
            if (age := _days_since(uploaded(version), moment)) is None or age >= cooldown_days
        ),
        None,
    )
    wheels = [
        Wheel(item.filename, item.url, item.sha256, item.size, item.upload_time)
        for item in by_version[latest]
    ]
    platforms: dict[str, object] = {}
    for target in PLATFORMS:
        best = best_wheel(wheels, target)
        platforms[target] = (
            {"filename": best.filename, "size": best.size} if best is not None else None
        )
    metadata: dict[str, object] = {}
    with_metadata = next(
        (item for item in by_version[latest] if item.metadata),
        None,
    )
    if with_metadata is not None:
        with contextlib.suppress(OSError, urllib.error.URLError, DownloadError, ValueError):
            text = http.read(with_metadata.url + ".metadata", limit=2 << 20).decode(
                "utf-8", errors="replace"
            )
            metadata = parse_metadata(text)
    age = _days_since(uploaded(latest), moment)
    return {
        "name": name,
        "key": key,
        "latest": latest,
        "uploaded": uploaded(latest),
        "cooldown": age is not None and age < cooldown_days,
        "allowed": allowed,
        "versions": [
            {"version": version, "uploaded": uploaded(version)} for version in ordered[:15]
        ],
        "platforms": platforms,
        "metadata": metadata,
        "uploadTimes": any(item.upload_time for item in files),
    }
