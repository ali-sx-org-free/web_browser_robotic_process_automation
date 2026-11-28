"""用 uv 解析套件清單（ADR 0027）：所有平台的鎖定檔，再逐平台確認每個套件都有 wheel。

1. ``uv pip compile --universal --only-binary :all: --python-version 3.13``，輸出 PEP 751 的
   pylock.toml。上一版的鎖定檔放在輸出的位置當成偏好：新增、移除套件時其他套件的版本不變，
   ``upgrade`` 時才升級。冷卻期用 ``--exclude-newer``；上一版已經鎖定、上架時間在冷卻期內的套件
   （例如內附的預設套件）以 ``--exclude-newer-package`` 放寬到它的上架時間，不會被降版。
2. 同一份要求以第一步的版本為 constraints，對四個平台各解析一次（``--python-platform``），
   每個套件在 uv 列出的 wheel 裡選這個平台最合適的一個。某個平台沒有 wheel 時，uv 的說明原樣
   回給管理員（可以改成只在某些平台安裝）。
3. 同一份要求再以 requirements.txt 的格式輸出一次，只為了取得「被誰需要」（``# via``）。
"""

import os
import re
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Final

from rpa_server.pypackages.locks import (
    PLATFORM_TARGETS,
    PYTHON_MINOR,
    PYTHON_VERSION,
    LockedPackage,
    Requirement,
    best_wheel,
    parse_lock,
    requirement_line,
)
from rpa_server.pypackages.sources import Http, Source

__all__ = ["ResolveError", "Resolved", "platform_manifest", "resolve_platform", "resolve_universal"]

TIMEOUT: Final = 600.0
_KEEP_ENV: Final = ("UV_NATIVE_TLS", "UV_SYSTEM_CERTS")
"""uv 的環境變數只留 TLS 的信任設定；索引、冷卻期之類一律由這裡的參數決定。"""


class ResolveError(Exception):
    """解析失敗；``detail`` 是 uv 的說明（給管理員看，不翻譯）。"""

    def __init__(self, code: str, detail: str, platform: str | None = None) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail
        self.platform = platform


@dataclass(frozen=True, slots=True)
class Resolved:
    lock: str
    """pylock.toml 的內容。"""
    packages: tuple[LockedPackage, ...]
    via: Mapping[str, tuple[str, ...]]
    """正規化的名稱 → 被哪些套件需要（直接加的是 requirements.in 自己）。"""


def uv_environment(
    http: Http, cache: Path, environ: Mapping[str, str] | None = None
) -> dict[str, str]:
    """執行 uv 的環境變數：不讀使用者的 uv、pip 設定；代理與根憑證用管理頁的設定。"""
    env = {
        key: value
        for key, value in (os.environ if environ is None else environ).items()
        if not key.upper().startswith(("UV_", "PIP_", "PYTHON", "VIRTUAL_ENV", "CONDA_"))
        or key.upper() in _KEEP_ENV
    }
    env["UV_CACHE_DIR"] = str(cache)
    env["UV_PYTHON_DOWNLOADS"] = "never"
    env["UV_NO_PROGRESS"] = "1"
    if http.proxy:
        for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
            env[key] = http.proxy
    if http.ca_file:
        env["SSL_CERT_FILE"] = http.ca_file
    return env


def _run(uv: Path, args: Sequence[str], work: Path, env: Mapping[str, str]) -> str:
    command = [str(uv), *args]
    try:
        completed = subprocess.run(
            command,
            cwd=work,
            env=dict(env),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=TIMEOUT,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ResolveError("uv_failed", str(error)) from error
    if completed.returncode != 0:
        raise ResolveError("resolve_failed", _tail(completed.stderr or completed.stdout))
    return completed.stdout


def _tail(text: str, lines: int = 30) -> str:
    kept = [line.rstrip() for line in text.strip().splitlines() if line.strip()]
    return "\n".join(kept[-lines:])


def _write_requirements(work: Path, requirements: Sequence[Requirement]) -> None:
    work.mkdir(parents=True, exist_ok=True)
    lines = [requirement_line(item) for item in requirements]
    (work / "requirements.in").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _common(source: Source) -> list[str]:
    return [
        "pip",
        "compile",
        "requirements.in",
        "--only-binary",
        ":all:",
        "--default-index",
        source.simple,
        "--no-config",
        "--python",
        sys.executable,
        "--quiet",
    ]


def _stamp(value: datetime) -> str:
    return value.astimezone().isoformat(timespec="seconds")


def cooldown_overrides(
    previous: Sequence[LockedPackage],
    requirements: Sequence[Requirement],
    cutoff: datetime,
    now: datetime,
) -> dict[str, str]:
    """冷卻期的例外：上一版鎖定的、上架在冷卻期內的套件放寬到它自己的上架時間；管理員確認過
    可以用新版本的套件不限。"""
    found: dict[str, str] = {}
    for package in previous:
        uploaded = package.upload_time
        if uploaded is None:
            continue
        try:
            moment = datetime.fromisoformat(uploaded.replace("Z", "+00:00"))
        except ValueError:
            continue
        if moment >= cutoff:
            found[package.key] = _stamp(moment + timedelta(seconds=1))
    for item in requirements:
        if item.allow_new:
            found[item.key] = _stamp(now + timedelta(days=1))
    return found


def resolve_universal(
    uv: Path,
    requirements: Sequence[Requirement],
    source: Source,
    work: Path,
    env: Mapping[str, str],
    *,
    previous: str | None = None,
    cutoff: datetime | None = None,
    overrides: Mapping[str, str] | None = None,
    upgrade: bool = False,
    upgrade_packages: Sequence[str] = (),
) -> Resolved:
    """第一步與第三步（見模組說明）；``upgrade_packages`` 是管理員改了條件的套件，不沿用上一版。"""
    _write_requirements(work, requirements)
    output = work / "pylock.toml"
    if previous and not upgrade:
        output.write_text(previous, encoding="utf-8")
    else:
        output.unlink(missing_ok=True)
    args = [*_common(source), "--universal", "--python-version", PYTHON_MINOR]
    args += ["--format", "pylock.toml", "--no-header", "--output-file", output.name]
    if cutoff is not None:
        args += ["--exclude-newer", _stamp(cutoff)]
        for name, stamp in sorted((overrides or {}).items()):
            args += ["--exclude-newer-package", f"{name}={stamp}"]
    if upgrade:
        args.append("--upgrade")
    else:
        for name in sorted(set(upgrade_packages)):
            args += ["--upgrade-package", name]
    _run(uv, args, work, env)
    lock = output.read_text(encoding="utf-8")
    packages = tuple(parse_lock(lock))
    pins = work / "pins.txt"
    pins.write_text("".join(f"{p.name}=={p.version}\n" for p in packages), encoding="utf-8")
    annotated = work / "requirements.txt"
    _run(
        uv,
        [
            *_common(source),
            "--universal",
            "--python-version",
            PYTHON_MINOR,
            "--constraint",
            pins.name,
            "--annotation-style",
            "line",
            "--no-header",
            "--output-file",
            annotated.name,
        ],
        work,
        env,
    )
    return Resolved(lock, packages, _via(annotated.read_text(encoding="utf-8")))


def _via(text: str) -> dict[str, tuple[str, ...]]:
    found: dict[str, tuple[str, ...]] = {}
    for line in text.splitlines():
        match = re.match(r"^([A-Za-z0-9][A-Za-z0-9._-]*)==\S+.*?#\s*via\s+(.*)$", line)
        if match:
            names = [part.strip() for part in match.group(2).split(",")]
            key = re.sub(r"[-_.]+", "-", match.group(1)).lower()
            found[key] = tuple(
                "requirements.in" if name.startswith("-r ") else name
                for name in names
                if name and not name.startswith("-c ")
            )
    return found


def resolve_platform(
    uv: Path,
    requirements: Sequence[Requirement],
    packages: Sequence[LockedPackage],
    source: Source,
    platform: str,
    work: Path,
    env: Mapping[str, str],
) -> list[LockedPackage]:
    """第二步：這個平台用得到的套件（版本照通用的鎖定檔）；沒有 wheel 時拋出 ResolveError。"""
    folder = work / platform
    _write_requirements(folder, requirements)
    (folder / "pins.txt").write_text(
        "".join(f"{p.name}=={p.version}\n" for p in packages), encoding="utf-8"
    )
    args = [*_common(source), "--python-platform", PLATFORM_TARGETS[platform]]
    args += ["--python-version", PYTHON_VERSION, "--constraint", "pins.txt"]
    args += ["--format", "pylock.toml", "--no-header", "--output-file", "pylock.toml"]
    try:
        _run(uv, args, folder, env)
    except ResolveError as error:
        raise ResolveError("platform_failed", error.detail, platform) from error
    return parse_lock((folder / "pylock.toml").read_text(encoding="utf-8"))


def platform_manifest(packages: Sequence[LockedPackage], platform: str) -> list[dict[str, object]]:
    """這個平台的 wheel 清單：每個套件一個（:func:`rpa_server.pypackages.locks.best_wheel`）。"""
    found: list[dict[str, object]] = []
    for package in packages:
        wheel = best_wheel(package.wheels, platform)
        if wheel is None:
            raise ResolveError("no_wheel", f"{package.name} {package.version}", platform)
        found.append(
            {
                "name": package.name,
                "version": package.version,
                "filename": wheel.filename,
                "url": wheel.url,
                "size": wheel.size,
                "sha256": wheel.sha256,
                "uploadTime": wheel.upload_time,
            }
        )
    return sorted(found, key=lambda item: str(item["name"]).lower())
