"""套件清單與鎖定檔（ADR 0027）：要求的格式、PEP 751 pylock.toml 的讀取、每個平台選 wheel、差異。

只用標準函式庫（tomllib）；wheel 的相容與優先順序用簡化的規則（只處理 CPython 3.13 與四個平台），
真正的相容檢查由 uv 的逐平台解析（``--python-platform``）負責，這裡只在 uv 列出的 wheel 裡挑一個。
"""

import hashlib
import re
import tomllib
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Final, cast

from rpa_runner.pypackages import normalize

__all__ = [
    "PLATFORMS",
    "PLATFORM_FAMILIES",
    "PLATFORM_TARGETS",
    "PYTHON_MINOR",
    "PYTHON_VERSION",
    "LockedPackage",
    "Requirement",
    "RequirementError",
    "Wheel",
    "best_wheel",
    "compatible",
    "diff_versions",
    "lock_digest",
    "parse_lock",
    "parse_requirements_in",
    "requirement_line",
    "version_key",
    "wheel_version",
]

PYTHON_VERSION: Final = "3.13.14"
"""RPA Python 運行環境 1 的 Python（runtimes/python/runtime.toml；測試確認兩邊一致）。"""
PYTHON_MINOR: Final = "3.13"
PLATFORMS: Final = ("windows-x86_64", "macos-arm64", "linux-x86_64", "linux-aarch64")
"""運行環境的平台代號（和 rpa_runner.pyruntime.platform_tag 相同）。"""
PLATFORM_TARGETS: Final = {
    "windows-x86_64": "x86_64-pc-windows-msvc",
    "macos-arm64": "aarch64-apple-darwin",
    "linux-x86_64": "x86_64-manylinux_2_28",
    "linux-aarch64": "aarch64-manylinux_2_28",
}
"""uv 的 ``--python-platform``（runtime.toml 的 wheels；Linux 是公司的 RHEL 8，glibc 2.28）。"""
PLATFORM_FAMILIES: Final = ("windows", "macos", "linux")
_MARKERS: Final = {
    "windows": 'sys_platform == "win32"',
    "macos": 'sys_platform == "darwin"',
    "linux": 'sys_platform == "linux"',
}
_NAME: Final = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9._-]{0,98}[A-Za-z0-9])?")
_SPEC: Final = re.compile(
    r"(?:===|==|!=|<=|>=|~=|<|>)\s*[A-Za-z0-9][A-Za-z0-9.*+!_-]{0,60}"
    r"(?:\s*,\s*(?:===|==|!=|<=|>=|~=|<|>)\s*[A-Za-z0-9][A-Za-z0-9.*+!_-]{0,60})*"
)


class RequirementError(ValueError):
    """套件名稱或版本條件的格式不對；訊息是錯誤代碼（介面翻譯）。"""


@dataclass(frozen=True, slots=True)
class Requirement:
    """套件清單裡的一項（直接加的套件）。"""

    name: str
    spec: str = ""
    """版本條件，例如 ``>=3,<4``；空字串是不限。"""
    platforms: tuple[str, ...] = ()
    """只在這些系統安裝（windows、macos、linux）；空的是全部。"""
    default: bool = False
    """內附的預設套件（runtimes/python/requirements.in）。"""
    note: str = ""
    added_by: str | None = None
    added_at: str | None = None
    allow_new: bool = False
    """管理員確認過：這個套件可以用冷卻期內的版本（ADR 0027 的安全）。"""

    @property
    def key(self) -> str:
        return normalize(self.name)

    def validated(self) -> "Requirement":
        name = self.name.strip()
        spec = re.sub(r"\s+", "", self.spec.strip())
        if not _NAME.fullmatch(name):
            raise RequirementError("invalid_name")
        if spec and not _SPEC.fullmatch(spec):
            raise RequirementError("invalid_spec")
        platforms = tuple(sorted(set(self.platforms)))
        if any(item not in PLATFORM_FAMILIES for item in platforms):
            raise RequirementError("invalid_platform")
        if len(platforms) == len(PLATFORM_FAMILIES):
            platforms = ()
        return Requirement(
            name,
            spec,
            platforms,
            self.default,
            self.note.strip()[:300],
            self.added_by,
            self.added_at,
            self.allow_new,
        )

    def to_json(self) -> dict[str, object]:
        return {
            "name": self.name,
            "spec": self.spec,
            "platforms": list(self.platforms),
            "default": self.default,
            "note": self.note,
            "addedBy": self.added_by,
            "addedAt": self.added_at,
            "allowNew": self.allow_new,
        }

    @classmethod
    def from_json(cls, data: Mapping[str, object]) -> "Requirement":
        platforms = data.get("platforms")
        return cls(
            name=str(data.get("name") or ""),
            spec=str(data.get("spec") or ""),
            platforms=tuple(str(item) for item in cast("list[object]", platforms))
            if isinstance(platforms, list)
            else (),
            default=data.get("default") is True,
            note=str(data.get("note") or ""),
            added_by=str(data["addedBy"]) if isinstance(data.get("addedBy"), str) else None,
            added_at=str(data["addedAt"]) if isinstance(data.get("addedAt"), str) else None,
            allow_new=data.get("allowNew") is True,
        )


def requirement_line(item: Requirement) -> str:
    """requirements.in 的一行：``名稱 條件 ; 平台條件``。"""
    line = f"{item.name}{item.spec}"
    if item.platforms:
        line += " ; " + " or ".join(_MARKERS[family] for family in item.platforms)
    return line


def parse_requirements_in(text: str) -> list[Requirement]:
    """內附預設套件的 requirements.in：緊接在套件前面的註解是那幾個套件的說明。"""
    found: list[Requirement] = []
    comment: list[str] = []
    note = ""
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            comment, note = [], ""
            continue
        if line.startswith("#"):
            comment.append(line.lstrip("#").strip())
            continue
        if comment:
            note, comment = " ".join(comment), []
        body = line.split("#", 1)[0].split(";", 1)[0].strip()
        match = re.fullmatch(r"([A-Za-z0-9][A-Za-z0-9._-]*)\s*(.*)", body)
        if match:
            found.append(
                Requirement(
                    match.group(1), re.sub(r"\s+", "", match.group(2)), default=True, note=note
                )
            )
    return found


@dataclass(frozen=True, slots=True)
class Wheel:
    filename: str
    url: str
    sha256: str
    size: int | None = None
    upload_time: str | None = None

    def to_json(self) -> dict[str, object]:
        return {
            "filename": self.filename,
            "url": self.url,
            "sha256": self.sha256,
            "size": self.size,
            "uploadTime": self.upload_time,
        }


@dataclass(frozen=True, slots=True)
class LockedPackage:
    name: str
    version: str
    marker: str | None = None
    wheels: tuple[Wheel, ...] = field(default=())

    @property
    def key(self) -> str:
        return normalize(self.name)

    @property
    def upload_time(self) -> str | None:
        """最晚上架的 wheel 的時間（冷卻期看的時間）。"""
        times = [wheel.upload_time for wheel in self.wheels if wheel.upload_time]
        return max(times) if times else None


def parse_lock(text: str) -> list[LockedPackage]:
    """讀 PEP 751 的 pylock.toml（uv 產生的）：套件、版本、平台條件、wheel。"""
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise ValueError(f"pylock.toml: {error}") from error
    packages: list[LockedPackage] = []
    for raw in cast("list[dict[str, object]]", data.get("packages") or []):
        wheels: list[Wheel] = []
        for item in cast("list[dict[str, object]]", raw.get("wheels") or []):
            url = str(item.get("url") or item.get("path") or "")
            hashes = cast("dict[str, object]", item.get("hashes") or {})
            sha256 = str(hashes.get("sha256") or "")
            size = item.get("size")
            uploaded = item.get("upload-time")
            filename = str(item.get("name") or url.rsplit("/", 1)[-1].split("#", 1)[0])
            if not sha256 or not filename.endswith(".whl"):
                continue
            wheels.append(
                Wheel(
                    filename=filename,
                    url=url,
                    sha256=sha256,
                    size=size if isinstance(size, int) else None,
                    upload_time=_iso(uploaded),
                )
            )
        marker = raw.get("marker")
        packages.append(
            LockedPackage(
                name=str(raw.get("name") or ""),
                version=str(raw.get("version") or ""),
                marker=str(marker) if isinstance(marker, str) else None,
                wheels=tuple(wheels),
            )
        )
    return [package for package in packages if package.name and package.version]


def _iso(value: object) -> str | None:
    if value is None:
        return None
    isoformat = getattr(value, "isoformat", None)
    text = str(isoformat()) if callable(isoformat) else str(value)
    return text.replace("+00:00", "Z")


def lock_digest(packages: Iterable[LockedPackage]) -> str:
    """鎖定檔的雜湊：套件、版本、平台條件與每個 wheel 的 sha256（不含註解與網址，換來源也相同）。"""
    lines = sorted(
        f"{package.key}=={package.version};{package.marker or ''};"
        + ",".join(sorted(wheel.sha256 for wheel in package.wheels))
        for package in packages
    )
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def versions(packages: Iterable[LockedPackage]) -> dict[str, str]:
    """正規化的名稱 → 版本。"""
    return {package.key: package.version for package in packages}


def diff_versions(old: Mapping[str, str], new: Mapping[str, str]) -> dict[str, list[list[str]]]:
    """兩個版本的差異（含依賴）：新增、移除、改版本。"""
    return {
        "added": [[name, new[name]] for name in sorted(set(new) - set(old))],
        "removed": [[name, old[name]] for name in sorted(set(old) - set(new))],
        "changed": [
            [name, old[name], new[name]]
            for name in sorted(set(old) & set(new))
            if old[name] != new[name]
        ],
    }


# ---------------------------------------------------------------- 版本


_VERSION: Final = re.compile(
    r"v?(?:(\d+)!)?(\d+(?:\.\d+)*)(?:[-_.]?(a|b|c|rc|alpha|beta|pre|preview)[-_.]?(\d*))?"
    r"(?:-(\d+)|[-_.]?(?:post|rev|r)[-_.]?(\d*))?(?:[-_.]?dev[-_.]?(\d*))?(?:\+.*)?",
    re.IGNORECASE,
)


def version_key(version: str) -> tuple[object, ...]:
    """版本的排序鍵（PEP 440 的常見寫法）；認不得的排最前面。"""
    match = _VERSION.fullmatch(version.strip())
    if match is None:
        return (-1,)
    epoch, release, pre, pre_n, post_a, post_b, dev = match.groups()
    numbers = [int(part) for part in release.split(".")]
    while len(numbers) > 1 and numbers[-1] == 0:
        numbers.pop()
    order = {"a": 0, "alpha": 0, "b": 1, "beta": 1, "c": 2, "rc": 2, "pre": 2, "preview": 2}
    pre_key = (order[pre.lower()], int(pre_n or 0)) if pre else (9, 0)
    post = post_a or post_b
    post_key = int(post) if post is not None and (post_a is not None or post_b is not None) else -1
    if pre is None and post is None and dev is not None:
        pre_key = (-1, 0)  # 1.0.dev1 在 1.0a1 之前
    dev_key = int(dev or 0) if dev is not None else 10**9
    return (int(epoch or 0), tuple(numbers), pre_key, post_key, dev_key)


def is_prerelease(version: str) -> bool:
    match = _VERSION.fullmatch(version.strip())
    return match is not None and (match.group(3) is not None or match.group(7) is not None)


def wheel_version(filename: str) -> tuple[str, str] | None:
    """wheel 檔名的（名稱, 版本）。"""
    parts = filename.removesuffix(".whl").split("-")
    if not filename.endswith(".whl") or len(parts) < 5:
        return None
    return parts[0], parts[1]


# ---------------------------------------------------------------- wheel 的平台


def _tags(filename: str) -> list[tuple[str, str, str]]:
    parts = filename.removesuffix(".whl").split("-")
    if len(parts) < 5:
        return []
    python, abi, platform = parts[-3], parts[-2], parts[-1]
    return [
        (py, ab, plat)
        for py in python.split(".")
        for ab in abi.split(".")
        for plat in platform.split(".")
    ]


def _python_rank(python: str, abi: str) -> float | None:
    """CPython 3.13 用不用得了這個 python 與 abi 標記；越小越優先。"""
    if python == "cp313" and abi == "cp313":
        return 0
    cp = re.fullmatch(r"cp3(\d+)", python)
    if cp and abi == "abi3" and int(cp.group(1)) <= 13:
        return 1 + (13 - int(cp.group(1))) / 100
    if python == "cp313" and abi == "none":
        return 2
    py = re.fullmatch(r"py3(\d*)", python)
    if py and abi == "none" and (not py.group(1) or int(py.group(1)) <= 13):
        return 3 + (13 - int(py.group(1) or 0)) / 100
    return None


_MANYLINUX_ALIASES: Final = {
    "manylinux1": (2, 5),
    "manylinux2010": (2, 12),
    "manylinux2014": (2, 17),
}
_GLIBC: Final = (2, 28)
_MACOS: Final = (14, 99)
"""判斷 macOS 的 wheel 能不能用時，接受到這一版（顯示用；實際由 uv 的逐平台解析確認）。"""


def _platform_rank(platform: str, target: str) -> tuple[int, int, int] | None:
    """這個平台標記在 target（運行環境的平台代號）上能不能用；越小越優先，any 最後。"""
    if platform == "any":
        return (1, 0, 0)
    if target == "windows-x86_64":
        return (0, 0, 0) if platform == "win_amd64" else None
    if target == "macos-arm64":
        match = re.fullmatch(r"macosx_(\d+)_(\d+)_(arm64|universal2)", platform)
        if match is None:
            return None
        version = (int(match.group(1)), int(match.group(2)))
        if version > _MACOS:
            return None
        # 新的 macOS 版本、只有 arm64 的優先（和 pip 的順序相同）
        return (0, -(version[0] * 100 + version[1]), int(match.group(3) == "universal2"))
    arch = "x86_64" if target == "linux-x86_64" else "aarch64"
    match = re.fullmatch(rf"manylinux_(\d+)_(\d+)_{arch}", platform)
    glibc: tuple[int, int] | None = None
    if match:
        glibc = (int(match.group(1)), int(match.group(2)))
    else:
        legacy = re.fullmatch(rf"(manylinux1|manylinux2010|manylinux2014)_{arch}", platform)
        if legacy:
            glibc = _MANYLINUX_ALIASES[legacy.group(1)]
    if glibc is None or glibc > _GLIBC:
        return None
    return (0, -(glibc[0] * 100 + glibc[1]), 0)


def compatible(filename: str, target: str) -> tuple[int, float, int, int] | None:
    """wheel 在這個平台的 CPython 3.13 能不能用；能用時回傳優先順序（越小越好）。"""
    best: tuple[int, float, int, int] | None = None
    for python, abi, platform in _tags(filename):
        python_rank = _python_rank(python, abi)
        platform_rank = _platform_rank(platform, target)
        if python_rank is None or platform_rank is None:
            continue
        key = (platform_rank[0], python_rank, platform_rank[1], platform_rank[2])
        if best is None or key < best:
            best = key
    return best


def best_wheel(wheels: Sequence[Wheel], target: str) -> Wheel | None:
    """這個平台最合適的 wheel：有平台的優先於 any，cp313 優先於 abi3、py3。"""
    ranked: list[tuple[tuple[int, float, int, int], Wheel]] = []
    for wheel in wheels:
        rank = compatible(wheel.filename, target)
        if rank is not None:
            ranked.append((rank, wheel))
    if not ranked:
        return None
    return min(ranked, key=lambda item: (item[0], item[1].filename))[1]
