"""伺服器用的 uv（ADR 0027 的 D7）：第一次用到時從套件來源下載固定的版本，不用重裝伺服器。

版本與每個平台的 wheel（路徑與 sha256，2026-11-27 從 PyPI 取得）寫在這裡；下載後核對 sha256，
從 wheel 的 ``uv-<版本>.data/scripts/`` 取出執行檔，放在資料目錄的 ``python-packages/tools/``。
環境變數 ``RPA_UV`` 指定一個 uv 時直接用它（開發與測試）。
"""

import os
import shutil
import stat
import sys
import uuid
import zipfile
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Final

from rpa_runner.pyruntime import platform_tag
from rpa_server.pypackages.sources import Http, Source, candidates, download

__all__ = ["ENV_UV", "UV_VERSION", "UV_WHEELS", "UvUnavailableError", "ensure_uv"]

ENV_UV: Final = "RPA_UV"
UV_VERSION: Final = "0.11.32"
_FILES: Final = "https://files.pythonhosted.org/packages/"
UV_WHEELS: Final = {
    "linux-x86_64": (
        "90/b0/114463d056b6b328d45557001e848b8ab15539bd8f4fa7a457ccb83e2b5d/"
        "uv-0.11.32-py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
        "3da76cd4e2697de30928b8a8524bd39183ac1e08cb7e72833807c022b7cba6c4",
    ),
    "linux-aarch64": (
        "5d/61/0d6a8ee5066385fce65a5ef57939b1f63e9ff955afa07fa423c3e7e0abdb/"
        "uv-0.11.32-py3-none-manylinux_2_17_aarch64.manylinux2014_aarch64.musllinux_1_1_aarch64.whl",
        "125c142363d0842c8506a057da56bae182e2aa3957344f57dd9ef20ea10f06b0",
    ),
    "macos-arm64": (
        "60/43/ec2de11ef008e76a8d01c34d573c939c565694f72c0d008d200aa3a5eac3/"
        "uv-0.11.32-py3-none-macosx_11_0_arm64.whl",
        "2a56d1abf16337350e878b2c869b256b8448ecc4a722b98f8d41e1b3680a587b",
    ),
    "macos-x86_64": (
        "12/85/ef4d0f02f469cfad1d73c11bf31ac0a8f24da3c62d7f3305c50a5e51e814/"
        "uv-0.11.32-py3-none-macosx_10_12_x86_64.whl",
        "c82954b1bd507e767b1d996c2865ea3eb7d464a479ec0e4d60f0b8e2e07dee45",
    ),
    "windows-x86_64": (
        "57/60/a645cca710448004268b7731c4dc6fc7d084a7c620fc73ecc2127cb61661/"
        "uv-0.11.32-py3-none-win_amd64.whl",
        "855632ee1d2a8491986efa54c562b806cd32477761889a1e13624b519d98a45e",
    ),
}
"""平台代號 → (files.pythonhosted.org/packages/ 之後的路徑, sha256)。"""


class UvUnavailableError(Exception):
    """取得不了 uv；訊息是技術細節。"""


def _name() -> str:
    return "uv.exe" if sys.platform == "win32" else "uv"


def ensure_uv(
    tools: Path,
    http: Http,
    sources: Sequence[Source],
    *,
    environ: Mapping[str, str] | None = None,
    platform: str | None = None,
    progress: Callable[[int], None] = lambda count: None,
) -> Path:
    """回傳 uv 的執行檔：RPA_UV、已經下載的固定版本，或現在下載。"""
    env = os.environ if environ is None else environ
    override = env.get(ENV_UV)
    if override:
        path = Path(override)
        if not path.is_file():
            raise UvUnavailableError(f"{ENV_UV}={override}: not found")
        return path
    folder = tools / f"uv-{UV_VERSION}"
    binary = folder / _name()
    if binary.is_file():
        return binary
    tag = platform or platform_tag()
    entry = UV_WHEELS.get(tag)
    if entry is None:
        found = shutil.which("uv")
        if found:
            return Path(found)
        raise UvUnavailableError(f"no uv {UV_VERSION} for {tag}")
    path, sha256 = entry
    wheel = tools / f".uv-{UV_VERSION}-{tag}.whl"
    try:
        download(http, candidates(_FILES + path, sources), wheel, sha256, progress=progress)
    except Exception as error:
        raise UvUnavailableError(f"download uv {UV_VERSION}: {error}") from error
    temp = tools / f".tmp-uv-{uuid.uuid4().hex[:8]}"
    try:
        temp.mkdir(parents=True)
        with zipfile.ZipFile(wheel) as archive:
            member = f"uv-{UV_VERSION}.data/scripts/{_name()}"
            try:
                info = archive.getinfo(member)
            except KeyError as error:
                raise UvUnavailableError(f"{wheel.name}: {member} missing") from error
            target = temp / _name()
            with archive.open(info) as source, target.open("wb") as handle:
                shutil.copyfileobj(source, handle)
        target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        if folder.exists():
            shutil.rmtree(folder, ignore_errors=True)
        temp.rename(folder)
    except (OSError, zipfile.BadZipFile) as error:
        raise UvUnavailableError(f"uv {UV_VERSION}: {error}") from error
    finally:
        shutil.rmtree(temp, ignore_errors=True)
        wheel.unlink(missing_ok=True)
    return binary
