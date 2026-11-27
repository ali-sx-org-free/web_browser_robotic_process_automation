"""RPA Python 運行環境的套件環境（ADR 0027）：伺服器管理的套件版本在這台電腦上的 venv。

伺服器的管理後台管理 Python 節點能用的套件；每次發布是一個「套件 #N」，以一份鎖定檔（每個套件的
確切版本與每個 wheel 的 sha256）表示。任務帶著這台電腦平台的清單（:class:`PackageSet`），
執行運行環境模式的 Python 節點前用 :func:`prepare_packages` 準備：

1. 清單和內附運行環境（:mod:`rpa_runner.pyruntime`）裡的套件完全相同（預設的 #1）時，直接用
   內附的運行環境，不建環境、不下載。
2. 否則用內附的直譯器以標準函式庫的 venv 建立環境（不裝 pip、不含內附的 site-packages），放在
   快取的 ``python/envs/<雜湊>-<平台>/``：內附運行環境裡同名同版的套件依 dist-info 的 RECORD
   複製（同一個磁碟用硬連結），其他的 wheel 由 ``fetch``（Worker 向伺服器下載）取得、核對
   sha256，存在 ``python/wheels/<sha256>.whl``，再用標準函式庫解開（照 wheel 格式放 purelib、
   platlib、data，不產生命令列程式，不執行套件的程式）。
3. compileall 編譯，用新的環境 import 每個直接加的套件，寫 ``.ready``，改名成正式的資料夾。
   同一份同時只有一個程序在做（和運行環境的解壓共用鎖檔的做法）；失敗就丟掉，下次重來。

保留最近用過的 :data:`KEEP_ENVS` 個環境，其他刪除；``wheels/`` 裡不再被保留的環境用到、超過
一天的檔案一起刪。環境的資料夾名稱是鎖定檔的雜湊加上內附運行環境的版本：App 換了新的內附
運行環境（直譯器）時重建。
"""

import contextlib
import csv
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import time
import uuid
import zipfile
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Final, cast

from rpa_runner.commands import no_window_flags
from rpa_runner.profiles import cache_dir
from rpa_runner.pyruntime import (
    PreparedRuntime,
    acquire_lock,
    clean_environment,
    python_path,
)

__all__ = [
    "ENVS",
    "KEEP_ENVS",
    "WHEELS",
    "Fetch",
    "PackageFile",
    "PackageRequest",
    "PackageSet",
    "PackagesUnavailableError",
    "PreparedPackages",
    "base_packages",
    "env_status",
    "install_wheel",
    "normalize",
    "prepare_packages",
    "prune",
    "site_packages",
]

ENVS: Final = "envs"
"""快取的 ``python/`` 底下放套件環境的資料夾。"""
WHEELS: Final = "wheels"
"""快取的 ``python/`` 底下放下載的 wheel 的資料夾（依 sha256 命名，各版本共用）。"""
KEEP_ENVS: Final = 3
"""保留最近用過的幾個套件環境（ADR 0027：回到前一版幾乎不用下載）。"""
READY: Final = ".ready"
INFO: Final = "rpa-packages.json"
"""套件環境裡的說明檔：套件版本、鎖定檔、用到的 wheel（清理 wheels/ 時看它）。"""
WHEEL_DAYS: Final = 1.0
"""沒有被保留的環境用到的 wheel，超過這麼多天才刪（別的程序可能正要用它）。"""
_HASH: Final = re.compile(r"[0-9a-f]{64}")
_FILENAME: Final = re.compile(r"[A-Za-z0-9_.+!-]+\.whl")


class PackagesUnavailableError(Exception):
    """套件環境準備不了；訊息給人看（技術細節）。"""


def normalize(name: str) -> str:
    """套件名稱的正規化（PEP 503）：不分大小寫，``-``、``_``、``.`` 視為相同。"""
    return re.sub(r"[-_.]+", "-", name).lower()


@dataclass(frozen=True, slots=True)
class PackageFile:
    """清單裡的一個 wheel。"""

    name: str
    version: str
    filename: str
    sha256: str
    size: int | None = None

    def to_json(self) -> dict[str, object]:
        return {
            "name": self.name,
            "version": self.version,
            "filename": self.filename,
            "sha256": self.sha256,
            "size": self.size,
        }

    @classmethod
    def from_json(cls, data: Mapping[str, object]) -> "PackageFile":
        name, version = data.get("name"), data.get("version")
        filename, sha256, size = data.get("filename"), data.get("sha256"), data.get("size")
        if not isinstance(name, str) or not isinstance(version, str) or not name or not version:
            raise PackagesUnavailableError(f"invalid package entry: {data!r}")
        if not isinstance(filename, str) or not _FILENAME.fullmatch(filename):
            raise PackagesUnavailableError(f"invalid wheel file name: {filename!r}")
        if not isinstance(sha256, str) or not _HASH.fullmatch(sha256):
            raise PackagesUnavailableError(f"invalid sha256 for {filename}")
        return cls(
            name=name,
            version=version,
            filename=filename,
            sha256=sha256,
            size=size if isinstance(size, int) and not isinstance(size, bool) else None,
        )


@dataclass(frozen=True, slots=True)
class PackageSet:
    """一個套件版本（套件 #N）在一個平台上的清單：伺服器放在任務裡給 Worker。"""

    revision: int
    lock: str
    """鎖定檔的 sha256（跨伺服器比較用）。"""
    platform: str
    files: tuple[PackageFile, ...]
    direct: tuple[str, ...] = ()
    """直接加的套件（正規化的名稱）：組好環境後 import 它們確認能用。"""

    def to_json(self) -> dict[str, object]:
        return {
            "revision": self.revision,
            "lock": self.lock,
            "platform": self.platform,
            "files": [item.to_json() for item in self.files],
            "direct": list(self.direct),
        }

    @classmethod
    def from_json(cls, data: Mapping[str, object]) -> "PackageSet":
        revision, lock, platform = data.get("revision"), data.get("lock"), data.get("platform")
        files, direct = data.get("files"), data.get("direct", [])
        if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
            raise PackagesUnavailableError(f"invalid package revision: {revision!r}")
        if not isinstance(lock, str) or not _HASH.fullmatch(lock):
            raise PackagesUnavailableError("invalid lock hash")
        if not isinstance(platform, str) or not platform:
            raise PackagesUnavailableError("invalid platform")
        if not isinstance(files, list) or not isinstance(direct, list):
            raise PackagesUnavailableError("invalid package list")
        entries = cast("list[object]", files)
        return cls(
            revision=revision,
            lock=lock,
            platform=platform,
            files=tuple(
                PackageFile.from_json(cast("dict[str, object]", item))
                for item in entries
                if isinstance(item, dict)
            ),
            direct=tuple(normalize(str(name)) for name in cast("list[object]", direct)),
        )

    def key(self, runtime_version: str) -> str:
        """套件環境的資料夾名稱裡的雜湊：鎖定檔加上內附運行環境的版本（直譯器換了就重建）。"""
        return hashlib.sha256(f"{self.lock}\0{runtime_version}".encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class PreparedPackages:
    """準備好的套件環境。"""

    root: Path
    python: Path
    revision: int
    lock: str
    bundled: bool
    """清單和內附運行環境的套件相同，直接用內附的運行環境（沒有另外建環境）。"""
    reused: bool
    prepared_ms: int
    downloaded: int = 0
    """這次下載了幾個 wheel。"""
    downloaded_bytes: int = 0
    copied: int = 0
    """從內附運行環境複製了幾個套件。"""

    def to_json(self) -> dict[str, object]:
        return {
            "revision": self.revision,
            "lock": self.lock,
            "bundled": self.bundled,
            "reused": self.reused,
            "preparedMs": self.prepared_ms,
            "downloaded": self.downloaded,
            "downloadedBytes": self.downloaded_bytes,
            "copied": self.copied,
        }


Progress = Callable[[int], None]
"""下載進度：這次多收到的位元組數。"""
Fetch = Callable[[PackageFile, Path, Progress], None]
"""把 wheel 下載到指定的路徑（可以接著已經有的部分續傳）；核對 sha256 由呼叫的這邊做。"""


@dataclass(frozen=True, slots=True)
class PackageRequest:
    """一次執行要用的套件版本與取得 wheel 的方法（:func:`rpa_runner.run.execute`）。"""

    packages: PackageSet
    fetch: Fetch
    on_progress: Callable[[int, int], None] | None = None


@dataclass(frozen=True, slots=True)
class _BaseDist:
    name: str
    version: str
    dist_info: Path
    files: tuple[str, ...]
    """RECORD 列的檔案（相對於 site-packages，不含 site-packages 以外的）。"""


def site_packages(root: Path) -> Path | None:
    """Python 根目錄（運行環境或 venv）的 site-packages：Windows 是 Lib/，其他是 lib/python3.x/。"""
    windows = root / "Lib" / "site-packages"
    if windows.is_dir():
        return windows
    found = sorted(root.glob("lib/python3*/site-packages"))
    return found[0] if found else None


def _metadata(dist_info: Path) -> tuple[str, str] | None:
    """dist-info 的 METADATA 開頭的 Name 與 Version。"""
    try:
        text = (dist_info / "METADATA").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    name = version = None
    for line in text.splitlines():
        if not line.strip():
            break
        key, _, value = line.partition(":")
        if key.lower() == "name":
            name = value.strip()
        elif key.lower() == "version":
            version = value.strip()
    return (name, version) if name and version else None


def _record(dist_info: Path) -> tuple[str, ...]:
    try:
        text = (dist_info / "RECORD").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ()
    paths: list[str] = []
    for row in csv.reader(io.StringIO(text)):
        if not row or not row[0]:
            continue
        path = PurePosixPath(row[0].replace("\\", "/"))
        if path.is_absolute() or ".." in path.parts or ":" in path.parts[0]:
            continue  # 命令列程式（../../bin/…）之類 site-packages 以外的檔案不複製
        paths.append(path.as_posix())
    return tuple(paths)


def base_packages(root: Path) -> dict[tuple[str, str], _BaseDist]:
    """內附運行環境裡的套件：(正規化的名稱, 版本) → dist-info 與 RECORD。"""
    site = site_packages(root)
    found: dict[tuple[str, str], _BaseDist] = {}
    if site is None:
        return found
    for dist_info in sorted(site.glob("*.dist-info")):
        meta = _metadata(dist_info)
        if meta is None:
            continue
        name, version = meta
        found[(normalize(name), version)] = _BaseDist(name, version, dist_info, _record(dist_info))
    return found


def _same_as_base(packages: PackageSet, base: Mapping[tuple[str, str], _BaseDist]) -> bool:
    wanted = {(normalize(item.name), item.version) for item in packages.files}
    return bool(base) and wanted == set(base)


def _link(source: Path, target: Path) -> None:
    """硬連結（同一個磁碟、不佔空間），不行就複製（保留修改時間：既有的 .pyc 照樣有效）。"""
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(source, target)
    except OSError:
        shutil.copy2(source, target)


def _copy_base(dist: _BaseDist, base_site: Path, site: Path) -> None:
    """依 RECORD 把內附運行環境的一個套件複製進環境，連同編譯好的 __pycache__。"""
    for relative in dist.files:
        source = base_site / relative
        if not source.is_file():
            continue
        _link(source, site / relative)
        if source.suffix == ".py":
            cache = source.parent / "__pycache__"
            for compiled in cache.glob(f"{source.stem}.*.pyc") if cache.is_dir() else ():
                _link(
                    compiled, site / PurePosixPath(relative).parent / "__pycache__" / compiled.name
                )
    # RECORD 自己與 INSTALLER 之類沒列在 RECORD 的 dist-info 檔案
    for path in dist.dist_info.iterdir():
        target = site / dist.dist_info.name / path.name
        if path.is_file() and not target.exists():
            _link(path, target)


def _safe_parts(name: str) -> tuple[str, ...] | None:
    path = PurePosixPath(name)
    if not name or "\\" in name or path.is_absolute() or ".." in path.parts:
        return None
    if ":" in path.parts[0]:
        return None
    return path.parts


def install_wheel(wheel: Path, site: Path, prefix: Path) -> str:
    """用標準函式庫解開 wheel 到 site-packages，回傳 dist-info 的名稱。

    照 wheel 格式：最上層與 ``.data/purelib``、``.data/platlib`` 放 site-packages，``.data/data``
    放環境的根目錄；``scripts``、``headers`` 不放（不產生命令列程式）。不執行套件的任何程式。
    """
    try:
        archive = zipfile.ZipFile(wheel)
    except (OSError, zipfile.BadZipFile) as error:
        raise PackagesUnavailableError(f"{wheel.name}: {error}") from error
    with archive:
        tops = {name.split("/", 1)[0] for name in archive.namelist()}
        dist_info = next(
            (
                top
                for top in sorted(tops)
                if top.endswith(".dist-info") and f"{top}/WHEEL" in archive.namelist()
            ),
            None,
        )
        if dist_info is None:
            raise PackagesUnavailableError(f"{wheel.name}: no .dist-info/WHEEL")
        data_dir = dist_info.removesuffix(".dist-info") + ".data"
        for info in archive.infolist():
            if info.is_dir():
                continue
            parts = _safe_parts(info.filename)
            if parts is None:
                raise PackagesUnavailableError(f"{wheel.name}: unsafe path {info.filename!r}")
            if parts[0] == data_dir:
                if len(parts) < 3:
                    continue
                scheme, rest = parts[1], parts[2:]
                if scheme in ("purelib", "platlib"):
                    base = site
                elif scheme == "data":
                    base = prefix
                else:
                    continue
            else:
                base, rest = site, parts
            target = base.joinpath(*rest)
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as source, target.open("wb") as handle:
                shutil.copyfileobj(source, handle)
            mode = (info.external_attr >> 16) & 0o777
            if os.name != "nt" and mode & 0o111:
                target.chmod(target.stat().st_mode | 0o111)
    (site / dist_info / "INSTALLER").write_text("rpa\n", encoding="utf-8")
    return dist_info


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _run(command: Sequence[str], timeout: float, what: str) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(
            command,
            capture_output=True,
            timeout=timeout,
            check=False,
            env=clean_environment(os.environ),
            creationflags=no_window_flags(),
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise PackagesUnavailableError(f"{what}: {error}") from error


def _last_line(data: bytes) -> str:
    lines = data.decode("utf-8", errors="replace").strip().splitlines()
    return lines[-1] if lines else ""


_IMPORT_CHECK: Final = r"""
import importlib, importlib.metadata as m, json, sys
result = {}
for name in json.loads(sys.argv[1]):
    try:
        dist = m.distribution(name)
    except m.PackageNotFoundError:
        result[name] = "not installed"
        continue
    listed = (dist.read_text("top_level.txt") or "").splitlines()
    tops = [line.strip() for line in listed if line.strip()]
    if not tops:
        for item in dist.files or []:
            parts = item.parts
            if len(parts) > 2 and parts[0].endswith(".data") and parts[1] in ("purelib", "platlib"):
                parts = parts[2:]
            if not parts or parts[0].endswith((".dist-info", ".data")):
                continue
            if parts[0] in ("..", "__pycache__"):
                continue
            top = parts[0]
            if len(parts) == 1:
                if not top.endswith((".py", ".pyd", ".so")):
                    continue
                top = top.split(".")[0]
            if top not in tops:
                tops.append(top)
    tops = [top for top in tops if top.isidentifier() and not top.startswith("_")] or [
        top for top in tops if top.isidentifier()
    ]
    error = None
    for top in tops:
        try:
            importlib.import_module(top)
        except BaseException as exc:
            error = error or f"import {top}: {type(exc).__name__}: {exc}"
        else:
            error = None
            break
    result[name] = error
print(json.dumps(result))
"""
"""在新的環境 import 每個直接加的套件：每個套件的最上層模組（top_level.txt 或 RECORD）有一個
import 得了就算通過（有些套件的部分模組要另外的套件或系統，例如 pywin32 的部分模組）。"""


def _import_check(python: Path, names: Sequence[str]) -> None:
    if not names:
        return
    command = [
        str(python),
        "-E",
        "-s",
        "-B",
        "-X",
        "utf8",
        "-c",
        _IMPORT_CHECK,
        json.dumps(list(names)),
    ]
    completed = _run(command, 300.0, "import check")
    if completed.returncode != 0:
        raise PackagesUnavailableError(f"import check failed: {_last_line(completed.stderr)}")
    try:
        result = cast("dict[str, str | None]", json.loads(_last_line(completed.stdout)))
    except ValueError as error:
        raise PackagesUnavailableError(f"import check: {error}") from error
    failed = [f"{name}（{error}）" for name, error in sorted(result.items()) if error]
    if failed:
        raise PackagesUnavailableError("import check failed: " + "；".join(failed))


def _create_venv(runtime: PreparedRuntime, target: Path) -> Path:
    """用內附的直譯器建立標準 venv（不裝 pip、不含內附的 site-packages），回傳它的直譯器。"""
    command = [str(runtime.python), "-E", "-s", "-m", "venv", "--without-pip", str(target)]
    completed = _run(command, 120.0, "venv")
    if completed.returncode != 0:
        raise PackagesUnavailableError(f"venv failed: {_last_line(completed.stderr)}")
    python = python_path(target)
    if not python.exists():
        raise PackagesUnavailableError(f"venv: {python} missing")
    return python


def _compile(python: Path, site: Path) -> None:
    """編譯 site-packages 的 .py（Python 節點以 -B 執行，不會自己寫 .pyc）；個別檔案編譯失敗
    （例如套件附的範例用了別的語法）不影響。已經有 .pyc 的（從內附運行環境複製的）略過。"""
    _run(
        [str(python), "-E", "-s", "-m", "compileall", "-q", "-j", "0", str(site)],
        900.0,
        "compileall",
    )


def _expected(packages: PackageSet, runtime: PreparedRuntime) -> str:
    return packages.key(runtime.version)


def _usable(folder: Path, expected: str) -> bool:
    try:
        ready = (folder / READY).read_text(encoding="utf-8").strip()
    except OSError:
        return False
    return ready == expected and python_path(folder).exists()


def env_status(
    packages: PackageSet, runtime: PreparedRuntime, environ: Mapping[str, str] | None = None
) -> bool:
    """這一版的套件環境在這台電腦上已經準備好了嗎（或清單和內附運行環境相同）。"""
    if _same_as_base(packages, base_packages(runtime.root)):
        return True
    env = os.environ if environ is None else environ
    folder = (
        cache_dir(env) / "python" / ENVS / f"{_expected(packages, runtime)[:16]}-{runtime.platform}"
    )
    return _usable(folder, _expected(packages, runtime))


def _wheel_path(wheels: Path, item: PackageFile) -> Path:
    return wheels / f"{item.sha256}.whl"


def _ensure_wheel(item: PackageFile, wheels: Path, fetch: Fetch, progress: Progress) -> int:
    """wheel 已經在 wheels/ 就沿用，否則下載並核對 sha256；回傳這次下載的位元組數。"""
    final = _wheel_path(wheels, item)
    if final.is_file():
        return 0
    wheels.mkdir(parents=True, exist_ok=True)
    part = wheels / f".{item.sha256}.part"
    before = part.stat().st_size if part.is_file() else 0
    try:
        fetch(item, part, progress)
    except PackagesUnavailableError:
        raise
    except Exception as error:  # 下載的錯誤（網路、伺服器）
        raise PackagesUnavailableError(f"{item.filename}: {error}") from error
    if not part.is_file():
        raise PackagesUnavailableError(f"{item.filename}: not downloaded")
    if _sha256(part) != item.sha256:
        part.unlink(missing_ok=True)
        raise PackagesUnavailableError(f"{item.filename}: sha256 mismatch")
    size = part.stat().st_size
    part.replace(final)
    return max(0, size - before)


def _build(
    packages: PackageSet,
    runtime: PreparedRuntime,
    base: Mapping[tuple[str, str], _BaseDist],
    temp: Path,
    wheels: Path,
    fetch: Fetch,
    progress: Progress,
    check: bool,
) -> tuple[int, int, int]:
    """在 temp 建好環境；回傳 (下載的檔案數, 下載的位元組數, 從內附複製的套件數)。"""
    python = _create_venv(runtime, temp)
    site = site_packages(temp)
    base_site = site_packages(runtime.root)
    if site is None:
        raise PackagesUnavailableError(f"{temp}: site-packages missing")
    downloaded = downloaded_bytes = copied = 0
    for item in packages.files:
        dist = base.get((normalize(item.name), item.version))
        if dist is not None and base_site is not None:
            _copy_base(dist, base_site, site)
            copied += 1
            continue
        existed = _wheel_path(wheels, item).is_file()
        got = _ensure_wheel(item, wheels, fetch, progress)
        if not existed:
            downloaded += 1
            downloaded_bytes += got
        install_wheel(_wheel_path(wheels, item), site, temp)
    _compile(python, site)
    if check:
        _import_check(python, packages.direct)
    info = {
        "revision": packages.revision,
        "lock": packages.lock,
        "runtime": runtime.version,
        "platform": runtime.platform,
        "wheels": sorted(item.sha256 for item in packages.files),
        "direct": list(packages.direct),
    }
    (temp / INFO).write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
    return downloaded, downloaded_bytes, copied


def prepare_packages(
    runtime: PreparedRuntime,
    packages: PackageSet,
    *,
    fetch: Fetch,
    environ: Mapping[str, str] | None = None,
    wait_seconds: float = 900.0,
    clock: Callable[[], float] = time.monotonic,
    on_progress: Callable[[int, int], None] | None = None,
    check: bool = True,
) -> PreparedPackages:
    """準備這個套件版本的環境（見模組說明），失敗時拋出 PackagesUnavailableError。

    ``on_progress(已下載, 要下載的總量)`` 回報下載進度（Worker 回報給伺服器）；``check`` 是組好
    之後要不要 import 直接加的套件。
    """
    started = clock()
    if packages.platform != runtime.platform:
        raise PackagesUnavailableError(
            f"package list for {packages.platform}, runtime is {runtime.platform}"
        )
    base = base_packages(runtime.root)

    def elapsed() -> int:
        return int((clock() - started) * 1000)

    if _same_as_base(packages, base):
        return PreparedPackages(
            root=runtime.root,
            python=runtime.python,
            revision=packages.revision,
            lock=packages.lock,
            bundled=True,
            reused=True,
            prepared_ms=elapsed(),
        )
    env = os.environ if environ is None else environ
    cache = cache_dir(env) / "python"
    envs, wheels = cache / ENVS, cache / WHEELS
    expected = _expected(packages, runtime)
    target = envs / f"{expected[:16]}-{runtime.platform}"

    def done(reused: bool, counts: tuple[int, int, int] = (0, 0, 0)) -> PreparedPackages:
        with contextlib.suppress(OSError):
            os.utime(target / READY)  # 最近用過：清理時保留
        return PreparedPackages(
            root=target,
            python=python_path(target),
            revision=packages.revision,
            lock=packages.lock,
            bundled=False,
            reused=reused,
            prepared_ms=elapsed(),
            downloaded=counts[0],
            downloaded_bytes=counts[1],
            copied=counts[2],
        )

    if _usable(target, expected):
        return done(reused=True)
    total = sum(
        item.size or 0
        for item in packages.files
        if (normalize(item.name), item.version) not in base
        and not _wheel_path(wheels, item).is_file()
    )
    received = 0

    def progress(count: int) -> None:
        nonlocal received
        received += count
        if on_progress is not None:
            on_progress(received, total)

    lock = envs / f".{target.name}.lock"
    try:
        acquire_lock(lock, wait_seconds)
    except Exception as error:
        raise PackagesUnavailableError(str(error)) from error
    try:
        if _usable(target, expected):  # 等鎖的時候別人已經準備好了
            return done(reused=True)
        temp = envs / f".tmp-{target.name}-{uuid.uuid4().hex[:8]}"
        try:
            counts = _build(packages, runtime, base, temp, wheels, fetch, progress, check)
            (temp / READY).write_text(expected, encoding="utf-8")
            if target.exists():
                shutil.rmtree(target, ignore_errors=True)
            temp.rename(target)
        except BaseException:
            shutil.rmtree(temp, ignore_errors=True)
            raise
    finally:
        lock.unlink(missing_ok=True)
    prune(cache, keep=(target,))
    return done(reused=False, counts=counts)


def _env_dirs(envs: Path) -> list[Path]:
    try:
        return [path for path in envs.iterdir() if path.is_dir() and not path.name.startswith(".")]
    except OSError:
        return []


def _ready_time(folder: Path) -> float:
    try:
        return (folder / READY).stat().st_mtime
    except OSError:
        return 0.0


def _used_wheels(folders: Iterable[Path]) -> set[str]:
    used: set[str] = set()
    for folder in folders:
        try:
            data = json.loads((folder / INFO).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(data, dict):
            wheels = cast("dict[str, object]", data).get("wheels")
            if isinstance(wheels, list):
                used.update(str(item) for item in cast("list[object]", wheels))
    return used


def prune(cache: Path, keep: Sequence[Path] = (), *, now: float | None = None) -> list[Path]:
    """保留最近用過的 KEEP_ENVS 個環境（加上 keep），其他刪除；不再用到的 wheel 一起刪。

    回傳刪掉的環境。正在別的程序使用的環境刪不掉（Windows）就留著，下次再試。
    """
    envs, wheels = cache / ENVS, cache / WHEELS
    current = now if now is not None else time.time()
    folders = sorted(_env_dirs(envs), key=_ready_time, reverse=True)
    kept = list(dict.fromkeys([*keep, *folders[:KEEP_ENVS]]))
    removed: list[Path] = []
    for folder in folders:
        if folder in kept:
            continue
        shutil.rmtree(folder, ignore_errors=True)
        if not folder.exists():
            removed.append(folder)
    # 中斷留下的暫存資料夾與下載到一半的檔案
    for leftover in [*envs.glob(".tmp-*"), *wheels.glob(".*.part")]:
        with contextlib.suppress(OSError):
            if current - leftover.stat().st_mtime > 86400 * WHEEL_DAYS:
                if leftover.is_dir():
                    shutil.rmtree(leftover, ignore_errors=True)
                else:
                    leftover.unlink()
    used = _used_wheels(kept)
    for wheel in wheels.glob("*.whl") if wheels.is_dir() else ():
        if wheel.stem in used:
            continue
        with contextlib.suppress(OSError):
            if current - wheel.stat().st_mtime > 86400 * WHEEL_DAYS:
                wheel.unlink()
    return removed
