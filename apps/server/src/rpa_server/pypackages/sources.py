"""套件來源（ADR 0027 的下載速度）：內建的 PyPI 與鏡像、測速、換來源下載與續傳。

- 內建來源和 ``scripts/setup-linux.sh`` 相同：名稱、simple 索引、檔案網址的開頭（取代
  ``https://files.pythonhosted.org/``）。一般的鏡像（bandersnatch、Nexus、Artifactory）把檔案放在
  simple 上一層的 ``packages/``，公司鏡像照這個規則推算。
- 測速：每個來源同時下載同一個已知 sha256 的檔案，內容相符而且最快的優先，其他依速度排成備援。
- 下載：同一個檔案依序試「每個來源的同一路徑」，最後才用鎖定檔裡的原始網址；寫到 ``.part``，
  中斷後用 HTTP Range 從斷點續傳；下載完核對 sha256，不符就丟掉、換下一個來源。
"""

import contextlib
import hashlib
import json
import ssl
import threading
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Iterable, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from http.client import HTTPException, HTTPResponse
from pathlib import Path
from typing import Final, cast

__all__ = [
    "PRESETS",
    "PYPI_FILES",
    "DownloadError",
    "Http",
    "Source",
    "SpeedResult",
    "candidates",
    "custom_source",
    "download",
    "speed_test",
]

PYPI_FILES: Final = "https://files.pythonhosted.org/"
SIMPLE_JSON: Final = "application/vnd.pypi.simple.v1+json"
USER_AGENT: Final = "rpa-server (python packages)"
CHUNK: Final = 1 << 20


@dataclass(frozen=True, slots=True)
class Source:
    id: str
    simple: str
    """simple 索引，例如 https://pypi.org/simple。"""
    files: str
    """檔案網址的開頭（以 / 結尾），取代 https://files.pythonhosted.org/。"""

    def to_json(self) -> dict[str, object]:
        return {"id": self.id, "simple": self.simple, "files": self.files}


PRESETS: Final = (
    Source("pypi", "https://pypi.org/simple", PYPI_FILES),
    Source(
        "tuna", "https://pypi.tuna.tsinghua.edu.cn/simple", "https://pypi.tuna.tsinghua.edu.cn/"
    ),
    Source("ustc", "https://mirrors.ustc.edu.cn/pypi/simple", "https://mirrors.ustc.edu.cn/pypi/"),
    Source("aliyun", "https://mirrors.aliyun.com/pypi/simple", "https://mirrors.aliyun.com/pypi/"),
    Source(
        "tencent",
        "https://mirrors.cloud.tencent.com/pypi/simple",
        "https://mirrors.cloud.tencent.com/pypi/",
    ),
    Source(
        "huawei",
        "https://repo.huaweicloud.com/repository/pypi/simple",
        "https://repo.huaweicloud.com/repository/pypi/",
    ),
)


def custom_source(url: str) -> Source:
    """公司的鏡像（simple 網址）：檔案在 simple 上一層的 packages/。"""
    simple = url.strip().rstrip("/")
    base = simple.removesuffix("/simple")
    return Source("custom", simple, base + "/")


class DownloadError(Exception):
    """所有來源都下載失敗；訊息列出每個來源的原因。"""


class Http:
    """HTTP 用戶端：管理頁設定的代理與公司的根憑證；沒設定代理時照系統（環境變數）的。"""

    def __init__(self, proxy: str = "", ca_file: str = "") -> None:
        handlers: list[urllib.request.BaseHandler] = []
        if proxy:
            handlers.append(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
        context = ssl.create_default_context()
        if ca_file:
            context.load_verify_locations(cafile=ca_file)
        handlers.append(urllib.request.HTTPSHandler(context=context))
        self._opener = urllib.request.build_opener(*handlers)
        self.proxy = proxy
        self.ca_file = ca_file

    def open(
        self, url: str, *, headers: Mapping[str, str] | None = None, timeout: float = 30.0
    ) -> HTTPResponse:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
        return cast("HTTPResponse", self._opener.open(request, timeout=timeout))

    def read(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        limit: int = 32 << 20,
        timeout: float = 30.0,
    ) -> bytes:
        with self.open(url, headers=headers, timeout=timeout) as response:
            data = response.read(limit + 1)
        if len(data) > limit:
            raise DownloadError(f"{url}: larger than {limit} bytes")
        return data

    def json(self, url: str, *, accept: str = "application/json", timeout: float = 30.0) -> object:
        return json.loads(self.read(url, headers={"Accept": accept}, timeout=timeout))


def file_path(url: str, sources: Iterable[Source] = PRESETS) -> str | None:
    """檔案網址在來源底下的路徑（packages/…）；不是認得的來源時回傳 None。"""
    for prefix in (PYPI_FILES, *(source.files for source in sources)):
        if url.startswith(prefix):
            rest = url[len(prefix) :].split("#", 1)[0]
            if rest.startswith("packages/"):
                return rest
    return None


def candidates(url: str, ranked: Sequence[Source], known: Iterable[Source] = PRESETS) -> list[str]:
    """下載一個檔案要依序試的網址：每個來源的同一路徑（依速度），最後是原始網址。"""
    path = file_path(url, [*known, *ranked])
    found = [source.files + path for source in ranked] if path else []
    found.append(url.split("#", 1)[0])
    return list(dict.fromkeys(found))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fetch_once(
    http: Http,
    url: str,
    part: Path,
    progress: Callable[[int], None],
    timeout: float,
    cancel: threading.Event | None,
) -> None:
    """從 url 下載到 part；part 已經有一部分時用 Range 接著下載（伺服器不支援時重來）。"""
    have = part.stat().st_size if part.is_file() else 0
    headers = {"Range": f"bytes={have}-"} if have else {}
    try:
        response = http.open(url, headers=headers, timeout=timeout)
    except urllib.error.HTTPError as error:
        if error.code == 416 and have:  # 已經下載完了（或檔案變了）：交給 sha256 判斷
            return
        raise
    with response:
        status = getattr(response, "status", 200)
        mode = "ab" if have and status == 206 else "wb"
        if mode == "wb" and have:
            progress(-have)
        length = response.headers.get("Content-Length")
        expected = int(length) if length and length.isdigit() else None
        received = 0
        with part.open(mode) as handle:
            while chunk := response.read(CHUNK):
                if cancel is not None and cancel.is_set():
                    raise DownloadError("cancelled")
                handle.write(chunk)
                received += len(chunk)
                progress(len(chunk))
    if expected is not None and received < expected:
        # 讀 n 個位元組時連線提早斷掉不會拋出錯誤：當成中斷，下一次從斷點續傳
        raise ConnectionError(f"incomplete: {received} of {expected} bytes")


def download(
    http: Http,
    urls: Sequence[str],
    target: Path,
    sha256: str,
    *,
    progress: Callable[[int], None] = lambda count: None,
    timeout: float = 60.0,
    retries: int = 2,
    cancel: threading.Event | None = None,
) -> str:
    """依序試 urls 下載到 target（核對 sha256），回傳成功的網址；都失敗時拋出 DownloadError。"""
    target.parent.mkdir(parents=True, exist_ok=True)
    part = target.with_name(f".{target.name}.part")
    reasons: list[str] = []
    for url in urls:
        for _attempt in range(retries + 1):
            try:
                _fetch_once(http, url, part, progress, timeout, cancel)
            except DownloadError:
                raise
            except (OSError, HTTPException, TimeoutError, ValueError) as error:
                reasons.append(f"{url}: {getattr(error, 'reason', None) or error}")
                if isinstance(error, urllib.error.HTTPError) and error.code < 500:
                    break  # 404 之類：換下一個來源
                continue  # 中斷：同一個來源續傳
            if part.is_file() and _sha256(part) == sha256:
                part.replace(target)
                return url
            reasons.append(f"{url}: sha256 mismatch")
            if part.is_file():
                progress(-part.stat().st_size)
            part.unlink(missing_ok=True)
            break
    part.unlink(missing_ok=True)
    raise DownloadError("; ".join(reasons[-6:]) or "no source")


@dataclass(frozen=True, slots=True)
class SpeedResult:
    source: str
    ok: bool
    speed: float = 0.0
    """位元組／秒。"""
    error: str = ""
    upload_times: bool | None = None
    """simple 索引有沒有上架時間（PEP 700）：沒有時冷卻期改向 pypi.org 核對。"""

    def to_json(self) -> dict[str, object]:
        return {
            "source": self.source,
            "ok": self.ok,
            "speed": round(self.speed),
            "error": self.error,
            "uploadTimes": self.upload_times,
        }


def has_upload_times(
    http: Http, source: Source, project: str, timeout: float = 15.0
) -> bool | None:
    """來源的 simple 索引（JSON）有沒有上架時間；連不上或不是 JSON 時回傳 None。"""
    try:
        data = http.json(f"{source.simple}/{project}/", accept=SIMPLE_JSON, timeout=timeout)
    except (OSError, urllib.error.URLError, ValueError, DownloadError):
        return None
    files = cast("dict[str, object]", data).get("files") if isinstance(data, dict) else None
    if not isinstance(files, list) or not files:
        return None
    return any(
        isinstance(item, dict) and cast("dict[str, object]", item).get("upload-time")
        for item in cast("list[object]", files)
    )


def speed_test(
    http: Http,
    sources: Sequence[Source],
    probe_path: str,
    probe_sha256: str,
    probe_project: str,
    work: Path,
    *,
    timeout: float = 20.0,
) -> list[SpeedResult]:
    """每個來源同時下載同一個檔案（probe_path 相對於檔案網址的開頭），依速度排序（失敗的最後）。"""
    work.mkdir(parents=True, exist_ok=True)

    def one(source: Source) -> SpeedResult:
        target = work / f"probe-{source.id}.whl"
        target.unlink(missing_ok=True)
        started = time.monotonic()
        try:
            download(
                http,
                [source.files + probe_path],
                target,
                probe_sha256,
                timeout=timeout,
                retries=0,
            )
        except DownloadError as error:
            return SpeedResult(source.id, False, error=str(error)[:300])
        finally:
            elapsed = max(time.monotonic() - started, 0.001)
        size = target.stat().st_size
        with contextlib.suppress(OSError):
            target.unlink()
        return SpeedResult(
            source.id,
            True,
            speed=size / elapsed,
            upload_times=has_upload_times(http, source, probe_project, timeout=timeout),
        )

    with ThreadPoolExecutor(max_workers=max(1, len(sources))) as pool:
        results = list(pool.map(one, sources))
    return sorted(results, key=lambda item: (not item.ok, -item.speed))
