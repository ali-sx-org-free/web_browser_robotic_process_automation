"""RPA Python 運行環境的套件由伺服器管理（ADR 0027）：草稿、檢查、發布、回退、wheel 庫與設定。

- 套件版本存在 ``python_package_sets``：發布的「套件 #N」不再改變；同一個運行環境主版本最多一份
  草稿。第一次用到時用程式內附的預設（``defaults/``，和內附的運行環境相同）建立 #1。
- 新增、移除只改草稿；「檢查」在背景執行：解析（uv）、每個平台確認有 wheel、和目前版本的差異與
  下載量、從最快的來源下載新的檔案、核對雜湊與冷卻期、在伺服器的平台組成套件環境並 import。
  通過後才能發布（D5）。回到某一版是用那一版的鎖定檔建一份草稿（不重新解析），檢查後發布。
- wheel 依 sha256 存在資料目錄的 ``python-packages/wheels/``，各版本共用；Worker 從 Worker API
  取（:meth:`PackageService.wheel_file`）。內附運行環境裡同名同版的套件 Worker 自己複製，不下載。
- 設定（settings 表的 ``python_packages``）：套件來源（自動測速、指定或公司的鏡像）、代理、根憑證、
  冷卻天數、同時下載的檔案數與 Worker 數、保留幾個版本。
"""

import contextlib
import logging
import shutil
import sys
import threading
import time
import zipfile
from collections.abc import Callable, Iterable, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from pathlib import Path
from typing import Final, cast

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from rpa_runner.pypackages import (
    PackageFile,
    PackageRequest,
    PackageSet,
    PackagesUnavailableError,
    normalize,
    prepare_packages,
)
from rpa_runner.pyruntime import PreparedRuntime, RuntimeUnavailableError, platform_tag
from rpa_server.domain import now
from rpa_server.errors import ServiceError, conflict, invalid, not_found
from rpa_server.i18n import t
from rpa_server.models import PythonPackageSet, Setting
from rpa_server.pypackages.finder import (
    IMPORT_NAMES,
    PackageLookupError,
    SceneSource,
    blocked_reason,
    lookup,
    scene_imports,
)
from rpa_server.pypackages.locks import (
    PLATFORMS,
    LockedPackage,
    Requirement,
    RequirementError,
    diff_versions,
    lock_digest,
    parse_lock,
    parse_requirements_in,
)
from rpa_server.pypackages.resolve import (
    ResolveError,
    cooldown_overrides,
    platform_manifest,
    resolve_platform,
    resolve_universal,
    uv_environment,
)
from rpa_server.pypackages.sources import (
    PRESETS,
    DownloadError,
    Http,
    Source,
    SpeedResult,
    candidates,
    custom_source,
    download,
    file_path,
    has_upload_times,
    speed_test,
)
from rpa_server.pypackages.uvtool import UvUnavailableError, ensure_uv

__all__ = ["DEFAULTS", "PackageService", "PackageSettings", "Revision"]

logger = logging.getLogger("rpa_server.pypackages")

DEFAULTS: Final = Path(__file__).with_name("defaults")
RUNTIME: Final = "1"
SETTING_KEY: Final = "python_packages"
DRAFT_STATES: Final = ("draft", "checking", "checked", "failed")
LARGE_BYTES: Final = 100 * 1024 * 1024
"""單一套件超過這麼大要再確認（ADR 0027 的大套件先提醒）。"""
SPEED_SECONDS: Final = 86400.0
"""測速的結果沿用多久。"""
WHEEL_GRACE_DAYS: Final = 1.0
PYPI_API: Final = "https://pypi.org/pypi"


@dataclass(frozen=True, slots=True)
class PackageSettings:
    source: str = "auto"
    """auto（測速後選最快的）、內建來源的代號（pypi、tuna…），或 custom（公司的鏡像）。"""
    custom_url: str = ""
    proxy: str = ""
    ca_file: str = ""
    cooldown_days: int = 7
    parallel: int = 4
    """伺服器同時下載幾個檔案。"""
    worker_downloads: int = 4
    """同時從伺服器下載的 Worker 數。"""
    keep_versions: int = 10
    """伺服器保留最近幾個版本用到的檔案。"""

    def to_json(self) -> dict[str, object]:
        return {
            "source": self.source,
            "customUrl": self.custom_url,
            "proxy": self.proxy,
            "caFile": self.ca_file,
            "cooldownDays": self.cooldown_days,
            "parallel": self.parallel,
            "workerDownloads": self.worker_downloads,
            "keepVersions": self.keep_versions,
        }

    @classmethod
    def from_json(cls, data: Mapping[str, object]) -> "PackageSettings":
        base = cls()

        def number(key: str, default: int, low: int, high: int) -> int:
            value = data.get(key)
            if isinstance(value, int) and not isinstance(value, bool) and low <= value <= high:
                return value
            return default

        source = str(data.get("source") or base.source)
        if source not in ("auto", "custom", *(item.id for item in PRESETS)):
            source = base.source
        return cls(
            source=source,
            custom_url=str(data.get("customUrl") or "").strip(),
            proxy=str(data.get("proxy") or "").strip(),
            ca_file=str(data.get("caFile") or "").strip(),
            cooldown_days=number("cooldownDays", base.cooldown_days, 0, 365),
            parallel=number("parallel", base.parallel, 1, 16),
            worker_downloads=number("workerDownloads", base.worker_downloads, 1, 100),
            keep_versions=number("keepVersions", base.keep_versions, 1, 1000),
        )


@dataclass(frozen=True, slots=True)
class Revision:
    """一個套件版本（發布的或草稿）。"""

    id: int
    number: int | None
    status: str
    requirements: tuple[Requirement, ...]
    lock: str | None
    lock_hash: str | None
    manifests: Mapping[str, object]
    check: Mapping[str, object] | None
    note: str | None
    base_number: int | None
    restored_from: int | None
    created_by: str | None
    created_at: datetime
    published_by: str | None
    published_at: datetime | None

    @property
    def platforms(self) -> Mapping[str, list[dict[str, object]]]:
        found = self.manifests.get("platforms")
        return cast("dict[str, list[dict[str, object]]]", found) if isinstance(found, dict) else {}

    @property
    def packages(self) -> Mapping[str, dict[str, object]]:
        """正規化的名稱 → 名稱、版本、被誰需要、上架時間。"""
        found = self.manifests.get("packages")
        return cast("dict[str, dict[str, object]]", found) if isinstance(found, dict) else {}

    def versions(self) -> dict[str, str]:
        return {key: str(item.get("version")) for key, item in self.packages.items()}

    def direct(self) -> set[str]:
        return {item.key for item in self.requirements}

    def sizes(self) -> dict[str, int]:
        """每個平台的 wheel 合計大小（不知道大小的不算）。"""
        return {
            platform: sum(int(cast("int", item.get("size") or 0)) for item in entries)
            for platform, entries in self.platforms.items()
        }

    def to_json(self) -> dict[str, object]:
        return {
            "id": self.id,
            "number": self.number,
            "status": self.status,
            "requirements": [item.to_json() for item in self.requirements],
            "lockHash": self.lock_hash,
            "packages": dict(self.packages),
            "sizes": self.sizes(),
            "check": dict(self.check) if self.check is not None else None,
            "note": self.note,
            "baseNumber": self.base_number,
            "restoredFrom": self.restored_from,
            "createdBy": self.created_by,
            "createdAt": _iso(self.created_at),
            "publishedBy": self.published_by,
            "publishedAt": _iso(self.published_at),
        }


def _iso(value: datetime | None) -> str | None:
    return value.isoformat(timespec="seconds") if value is not None else None


def _revision(row: PythonPackageSet) -> Revision:
    return Revision(
        id=row.id,
        number=row.number,
        status=row.status,
        requirements=tuple(Requirement.from_json(item) for item in row.requirements or []),
        lock=row.lock,
        lock_hash=row.lock_hash,
        manifests=row.manifests or {},
        check=row.check,
        note=row.note,
        base_number=row.base_number,
        restored_from=row.restored_from,
        created_by=row.created_by,
        created_at=row.created_at,
        published_by=row.published_by,
        published_at=row.published_at,
    )


def _via_from_requirements_lock(text: str) -> dict[str, list[str]]:
    """uv 產生的 requirements.lock 的 ``# via`` 註解（一行或多行）。"""
    found: dict[str, list[str]] = {}
    current: str | None = None
    collecting = False
    for line in text.splitlines():
        stripped = line.strip()
        if line and not line.startswith((" ", "#")):
            current = normalize(stripped.split("==", 1)[0].split(" ", 1)[0])
            collecting = False
            continue
        if current is None or not stripped.startswith("#"):
            continue
        body = stripped.lstrip("#").strip()
        if body.startswith("via"):
            rest = body[3:].strip()
            collecting = not rest
            if rest:
                found.setdefault(current, []).append(rest)
        elif collecting and body:
            found.setdefault(current, []).append(body)
    return {
        key: ["requirements.in" if item.startswith("-r ") else item for item in items]
        for key, items in found.items()
    }


def package_info(
    packages: Iterable[LockedPackage],
    via: Mapping[str, Sequence[str]],
    direct: Iterable[str],
) -> dict[str, dict[str, object]]:
    wanted = set(direct)
    return {
        package.key: {
            "name": package.name,
            "version": package.version,
            "marker": package.marker,
            "uploadTime": package.upload_time,
            "via": [item for item in via.get(package.key, ()) if item != "requirements.in"],
            "direct": package.key in wanted,
        }
        for package in packages
    }


def load_defaults(folder: Path = DEFAULTS) -> tuple[list[Requirement], str, dict[str, object]]:
    """程式內附的預設套件 #1：要求、通用的鎖定檔、每個平台的 wheel 與套件資訊。"""
    requirements = parse_requirements_in((folder / "requirements.in").read_text(encoding="utf-8"))
    lock = (folder / "pylock.toml").read_text(encoding="utf-8")
    packages = parse_lock(lock)
    via = _via_from_requirements_lock((folder / "requirements.lock").read_text(encoding="utf-8"))
    platforms = {
        tag: platform_manifest(
            parse_lock((folder / f"pylock.{tag}.toml").read_text(encoding="utf-8")), tag
        )
        for tag in PLATFORMS
    }
    manifests: dict[str, object] = {
        "platforms": platforms,
        "packages": package_info(packages, via, (item.key for item in requirements)),
    }
    return requirements, lock, manifests


def _probe(lock: str) -> tuple[str, str, str] | None:
    """測速用的檔案：預設鎖定檔裡 100 KB～4 MB 最大的純 Python wheel →（路徑、sha256、套件）。"""
    best: tuple[int, str, str, str] | None = None
    for package in parse_lock(lock):
        for wheel in package.wheels:
            path = file_path(wheel.url)
            size = wheel.size or 0
            pure = wheel.filename.endswith("-none-any.whl")
            if path and pure and 100_000 <= size <= 4_000_000 and (best is None or size > best[0]):
                best = (size, path, wheel.sha256, package.key)
    return best[1:] if best is not None else None


def _wheel_tops(path: Path) -> tuple[set[str], bool]:
    """wheel 裡的最上層模組與有沒有 .pth（Python 啟動時會執行的檔案）。"""
    tops: set[str] = set()
    pth = False
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        listed = next((name for name in names if name.endswith(".dist-info/top_level.txt")), None)
        if listed is not None:
            text = archive.read(listed).decode("utf-8", errors="replace")
            tops = {line.strip().split("/", 1)[0] for line in text.splitlines() if line.strip()}
        for name in names:
            parts = name.split("/")
            if len(parts) > 2 and parts[0].endswith(".data") and parts[1] in ("purelib", "platlib"):
                parts = parts[2:]
            if parts[0].endswith((".dist-info", ".data")):
                continue
            if len(parts) == 1:
                if parts[0].endswith(".pth"):
                    pth = True
                    continue
                if parts[0].endswith((".py", ".pyd", ".so")):
                    tops.add(parts[0].split(".", 1)[0])
                continue
            if listed is None and parts[0] != "__pycache__":
                tops.add(parts[0])
    return {top for top in tops if top.isidentifier()}, pth


@dataclass(slots=True)
class _Progress:
    """檢查進行中的狀態（只在記憶體，頁面輪詢）。"""

    step: str = "resolve"
    files: int = 0
    done_files: int = 0
    bytes: int = 0
    done_bytes: int = 0
    current: list[str] = field(default_factory=list[str])
    started: float = field(default_factory=time.monotonic)

    def to_json(self) -> dict[str, object]:
        elapsed = max(time.monotonic() - self.started, 0.001)
        return {
            "step": self.step,
            "files": self.files,
            "doneFiles": self.done_files,
            "bytes": self.bytes,
            "doneBytes": self.done_bytes,
            "current": list(self.current),
            "speed": round(self.done_bytes / elapsed),
        }


class PackageService:
    """伺服器管理的套件版本（ADR 0027）。"""

    def __init__(
        self,
        sessions: sessionmaker[Session],
        data_dir: Path,
        *,
        scenes: Callable[[], Sequence[SceneSource]] = lambda: (),
        devices: Callable[[], Mapping[str, str]] = lambda: {},
        runtime: Callable[[], PreparedRuntime] | None = None,
        environ: Mapping[str, str] | None = None,
        platform: str | None = None,
        defaults: Path = DEFAULTS,
        pypi_api: str = PYPI_API,
    ) -> None:
        self.sessions = sessions
        self.root = data_dir / "python-packages"
        self.wheels = self.root / "wheels"
        self.tools = self.root / "tools"
        self.work = self.root / "work"
        self.scenes = scenes
        """運行環境模式的場景的 Python 檔（移除的影響、場景缺的模組）。"""
        self.devices = devices
        """裝置代號 → 平台代號（只下載有裝置的平台）。"""
        self.runtime = runtime
        """伺服器自己的 RPA Python 運行環境（檢查時在這個平台組成環境並 import）。"""
        self.environ = environ
        self.platform = platform or platform_tag()
        self.defaults = defaults
        self.pypi_api = pypi_api.rstrip("/")
        """另外核對雜湊與上架時間用的 PyPI JSON API。"""
        self._lock = threading.RLock()
        self._threads: dict[int, threading.Thread] = {}
        self._progress: dict[int, _Progress] = {}
        self._speed: tuple[float, list[SpeedResult]] | None = None
        self._statuses: dict[str, dict[str, object]] = {}
        self._downloading: set[str] = set()
        self._fetch_locks: dict[str, threading.Lock] = {}
        self._tops: dict[tuple[str, str], set[str]] = {}
        self._closing = threading.Event()
        self._defaults_data: tuple[list[Requirement], str, dict[str, object]] | None = None

    # ------------------------------------------------------------ 版本

    def ensure_defaults(self) -> Revision:
        """還沒有任何發布的版本時，用程式內附的預設建立套件 #1（和內附的運行環境相同）。"""
        with self._lock, self.sessions() as session:
            row = self._current_row(session)
            if row is None:
                requirements, lock, manifests = load_defaults(self.defaults)
                moment = now()
                row = PythonPackageSet(
                    runtime=RUNTIME,
                    number=1,
                    status="published",
                    requirements=[item.to_json() for item in requirements],
                    lock=lock,
                    lock_hash=lock_digest(parse_lock(lock)),
                    manifests=manifests,
                    note=None,
                    created_at=moment,
                    updated_at=moment,
                    published_at=moment,
                )
                session.add(row)
                session.commit()
            return _revision(row)

    @staticmethod
    def _current_row(session: Session) -> PythonPackageSet | None:
        return session.scalars(
            select(PythonPackageSet)
            .where(PythonPackageSet.runtime == RUNTIME, PythonPackageSet.status == "published")
            .order_by(PythonPackageSet.number.desc())
            .limit(1)
        ).first()

    @staticmethod
    def _draft_row(session: Session) -> PythonPackageSet | None:
        return session.scalars(
            select(PythonPackageSet).where(
                PythonPackageSet.runtime == RUNTIME, PythonPackageSet.status.in_(DRAFT_STATES)
            )
        ).first()

    def current(self) -> Revision:
        """目前發布的版本（沒有時建立 #1）。"""
        with self.sessions() as session:
            row = self._current_row(session)
            if row is not None:
                return _revision(row)
        return self.ensure_defaults()

    def current_number(self) -> int:
        return self.current().number or 1

    def revision(self, number: int) -> Revision:
        with self.sessions() as session:
            row = session.scalars(
                select(PythonPackageSet).where(
                    PythonPackageSet.runtime == RUNTIME, PythonPackageSet.number == number
                )
            ).first()
            if row is None:
                raise not_found(
                    "package_revision_not_found", t("pypackages.error_revision", number=number)
                )
            return _revision(row)

    def history(self) -> list[Revision]:
        self.ensure_defaults()
        with self.sessions() as session:
            rows = session.scalars(
                select(PythonPackageSet)
                .where(PythonPackageSet.runtime == RUNTIME, PythonPackageSet.status == "published")
                .order_by(PythonPackageSet.number.desc())
            )
            return [_revision(row) for row in rows]

    def draft(self) -> Revision | None:
        with self.sessions() as session:
            row = self._draft_row(session)
            return _revision(row) if row is not None else None

    def status(self) -> dict[str, object]:
        """管理頁輪詢：草稿的狀態與檢查的進度。"""
        draft = self.draft()
        data: dict[str, object] = {"current": self.current_number(), "draft": None}
        if draft is not None:
            data["draft"] = draft.to_json()
            progress = self._progress.get(draft.id)
            if progress is not None:
                data["progress"] = progress.to_json()
        return data

    # ------------------------------------------------------------ 草稿

    def _ensure_draft(self, session: Session, actor: str | None) -> PythonPackageSet:
        row = self._draft_row(session)
        if row is not None:
            if row.status == "checking":
                raise conflict("package_checking", t("pypackages.error_checking"))
            return row
        current = self._current_row(session)
        if current is None:
            raise conflict("package_no_current", t("pypackages.error_no_current"))
        moment = now()
        row = PythonPackageSet(
            runtime=RUNTIME,
            number=None,
            status="draft",
            requirements=list(current.requirements),
            lock=current.lock,
            lock_hash=current.lock_hash,
            manifests=current.manifests,
            base_number=current.number,
            created_by=actor,
            created_at=moment,
            updated_at=moment,
        )
        session.add(row)
        session.flush()
        return row

    @staticmethod
    def _touch(row: PythonPackageSet) -> None:
        """草稿改了：之前的檢查不算數，要重新檢查。"""
        row.status = "draft"
        row.check = None
        row.restored_from = None
        row.updated_at = now()

    def add(
        self,
        name: str,
        spec: str = "",
        platforms: Sequence[str] = (),
        *,
        note: str = "",
        allow_new: bool = False,
        actor: str | None = None,
    ) -> Revision:
        """草稿加入（或修改）一個套件。"""
        try:
            item = Requirement(
                name, spec, tuple(platforms), note=note, allow_new=allow_new
            ).validated()
        except RequirementError as error:
            raise invalid(f"package_{error}", t(f"pypackages.error_{error}")) from error
        reason = blocked_reason(item.name)
        if reason is not None:
            raise invalid(f"package_{reason}", t(f"pypackages.error_{reason}", name=item.name))
        with self._lock, self.sessions() as session:
            self.ensure_defaults()
            row = self._ensure_draft(session, actor)
            items = [Requirement.from_json(entry) for entry in row.requirements]
            existing = next((entry for entry in items if entry.key == item.key), None)
            stamp = _iso(now())
            if existing is not None:
                item = replace(
                    item,
                    default=existing.default,
                    note=item.note or existing.note,
                    added_by=existing.added_by,
                    added_at=existing.added_at,
                )
                items = [item if entry.key == item.key else entry for entry in items]
            else:
                items.append(replace(item, added_by=actor, added_at=stamp))
            row.requirements = [entry.to_json() for entry in items]
            self._touch(row)
            session.commit()
            return _revision(row)

    def remove(self, name: str, *, reason: str = "", actor: str | None = None) -> Revision:
        """草稿拿掉一個直接加的套件；有已發布的場景用到時要寫原因（D2）。"""
        key = normalize(name)
        users = [scene for scene in self.impact(key) if scene["published"]]
        if users and not reason.strip():
            raise conflict(
                "package_in_use",
                t("pypackages.error_in_use", name=name, count=len(users)),
                scenes=users,
            )
        with self._lock, self.sessions() as session:
            self.ensure_defaults()
            row = self._ensure_draft(session, actor)
            items = [Requirement.from_json(entry) for entry in row.requirements]
            kept = [entry for entry in items if entry.key != key]
            if len(kept) == len(items):
                raise not_found("package_not_in_list", t("pypackages.error_not_in_list", name=name))
            row.requirements = [entry.to_json() for entry in kept]
            if reason.strip():
                line = t("pypackages.forced_note", name=name, reason=reason.strip()[:500])
                row.note = f"{row.note}\n{line}" if row.note else line
            self._touch(row)
            session.commit()
            return _revision(row)

    def discard(self) -> None:
        with self._lock, self.sessions() as session:
            row = self._draft_row(session)
            if row is None:
                return
            if row.status == "checking":
                raise conflict("package_checking", t("pypackages.error_checking"))
            session.delete(row)
            session.commit()

    def restore(self, number: int, *, actor: str | None = None) -> Revision:
        """回到某一版：用那一版的要求與鎖定檔建草稿並開始檢查（不重新解析，檔案多半都還在）。"""
        source = self.revision(number)
        with self._lock, self.sessions() as session:
            if self._draft_row(session) is not None:
                raise conflict("package_draft_exists", t("pypackages.error_draft_exists"))
            current = self._current_row(session)
            moment = now()
            row = PythonPackageSet(
                runtime=RUNTIME,
                number=None,
                status="draft",
                requirements=[item.to_json() for item in source.requirements],
                lock=source.lock,
                lock_hash=source.lock_hash,
                manifests=dict(source.manifests),
                base_number=current.number if current is not None else None,
                restored_from=number,
                created_by=actor,
                created_at=moment,
                updated_at=moment,
            )
            session.add(row)
            session.commit()
        return self.start_check(actor=actor)

    # ------------------------------------------------------------ 檢查

    def start_check(self, *, upgrade: bool = False, actor: str | None = None) -> Revision:
        """在背景檢查草稿（沒有草稿時，``upgrade`` 從目前的版本建一份檢查更新）。"""
        with self._lock, self.sessions() as session:
            row = self._draft_row(session)
            if row is None:
                if not upgrade:
                    raise not_found("package_no_draft", t("pypackages.error_no_draft"))
                self.ensure_defaults()
                row = self._ensure_draft(session, actor)
            if row.status == "checking":
                raise conflict("package_checking", t("pypackages.error_checking"))
            row.status = "checking"
            row.check = {"state": "running", "startedAt": _iso(now()), "upgrade": upgrade}
            row.updated_at = now()
            session.commit()
            draft_id = row.id
            revision = _revision(row)
        self._progress[draft_id] = _Progress()
        thread = threading.Thread(
            target=self._run_check,
            args=(draft_id, upgrade),
            name=f"python-packages-check-{draft_id}",
            daemon=True,
        )
        self._threads[draft_id] = thread
        thread.start()
        return revision

    def wait(self, timeout: float | None = None) -> None:
        """等背景的檢查做完（測試用）。"""
        for thread in list(self._threads.values()):
            thread.join(timeout)

    def close(self) -> None:
        self._closing.set()

    def _run_check(self, draft_id: int, upgrade: bool) -> None:
        result: dict[str, object] = {"steps": [], "errors": [], "warnings": []}
        state = "failed"
        try:
            state = self._check(draft_id, upgrade, result)
        except Exception as error:  # 檢查程式本身的錯誤：記下來，草稿照樣可以再檢查
            logger.exception("檢查套件草稿失敗")
            cast("list[dict[str, object]]", result["errors"]).append(
                {"code": "crashed", "detail": f"{type(error).__name__}: {error}"}
            )
        finally:
            with self._lock, self.sessions() as session:
                row = session.get(PythonPackageSet, draft_id)
                if row is not None and row.status == "checking":
                    row.status = "checked" if state == "passed" else "failed"
                    previous = dict(row.check or {})
                    row.check = {
                        **previous,
                        **result,
                        "state": state,
                        "finishedAt": _iso(now()),
                    }
                    row.updated_at = now()
                    session.commit()
            self._progress.pop(draft_id, None)
            self._threads.pop(draft_id, None)

    def _step(self, result: dict[str, object], step: str, status: str, **details: object) -> None:
        steps = cast("list[dict[str, object]]", result["steps"])
        steps.append({"id": step, "status": status, **details})

    def _check(self, draft_id: int, upgrade: bool, result: dict[str, object]) -> str:
        errors = cast("list[dict[str, object]]", result["errors"])
        warnings = cast("list[dict[str, object]]", result["warnings"])
        progress = self._progress.setdefault(draft_id, _Progress())
        settings = self.settings()
        http = self._http(settings)
        ranked = self._ranked(settings, http)
        source = ranked[0]
        result["source"] = source.id
        with self.sessions() as session:
            row = session.get(PythonPackageSet, draft_id)
            if row is None:
                return "failed"
            draft = _revision(row)
            current_row = self._current_row(session)
            current = _revision(current_row) if current_row is not None else None
        requirements = list(draft.requirements)
        moment = now()
        upload_times = self._upload_times(settings, http, source)
        manifests: dict[str, object]
        if draft.restored_from is not None and draft.lock:
            # 回到某一版：鎖定檔與每個平台的 wheel 照那一版
            lock, manifests = draft.lock, dict(draft.manifests)
            packages = parse_lock(lock)
            self._step(result, "resolve", "skipped", restoredFrom=draft.restored_from)
        else:
            progress.step = "resolve"
            work = self.work / f"draft-{draft_id}"
            shutil.rmtree(work, ignore_errors=True)
            try:
                uv = ensure_uv(self.tools, http, ranked, environ=self.environ)
            except UvUnavailableError as error:
                errors.append({"code": "uv_unavailable", "detail": str(error)})
                self._step(result, "resolve", "failed")
                return "failed"
            env = uv_environment(http, self.root / "uv-cache", self.environ)
            previous = current.lock if current is not None else None
            cutoff: datetime | None = None
            overrides: dict[str, str] = {}
            if settings.cooldown_days > 0 and upload_times:
                cutoff = moment - timedelta(days=settings.cooldown_days)
                overrides = cooldown_overrides(
                    parse_lock(previous) if previous else [], requirements, cutoff, moment
                )
            elif settings.cooldown_days > 0:
                warnings.append({"code": "no_upload_times", "source": source.id})
            try:
                resolved = resolve_universal(
                    uv,
                    requirements,
                    source,
                    work,
                    env,
                    previous=previous,
                    cutoff=cutoff,
                    overrides=overrides,
                    upgrade=upgrade,
                    upgrade_packages=_changed(current, requirements),
                )
            except ResolveError as error:
                errors.append({"code": error.code, "detail": error.detail})
                self._step(result, "resolve", "failed")
                return "failed"
            self._step(result, "resolve", "passed", packages=len(resolved.packages))
            progress.step = "platforms"
            platforms: dict[str, object] = {}
            failed = False
            for tag in PLATFORMS:
                try:
                    found = resolve_platform(
                        uv, requirements, resolved.packages, source, tag, work, env
                    )
                    platforms[tag] = platform_manifest(found, tag)
                except ResolveError as error:
                    failed = True
                    errors.append({"code": error.code, "platform": tag, "detail": error.detail})
            if failed:
                self._step(result, "platforms", "failed")
                return "failed"
            self._step(result, "platforms", "passed")
            lock, packages = resolved.lock, list(resolved.packages)
            manifests = {
                "platforms": platforms,
                "packages": package_info(
                    packages, resolved.via, (item.key for item in requirements)
                ),
            }
            shutil.rmtree(work, ignore_errors=True)
        lock_hash = lock_digest(packages)
        candidate = replace(draft, lock=lock, lock_hash=lock_hash, manifests=manifests)
        # 差異與每個平台的下載量
        before = current.versions() if current is not None else {}
        result["diff"] = diff_versions(before, candidate.versions())
        known = self._known_hashes(exclude=draft_id)
        sizes: dict[str, dict[str, int]] = {}
        for tag, entries in candidate.platforms.items():
            fresh = [item for item in entries if str(item.get("sha256")) not in known]
            sizes[tag] = {
                "total": sum(int(cast("int", item.get("size") or 0)) for item in entries),
                "new": sum(int(cast("int", item.get("size") or 0)) for item in fresh),
                "newFiles": len(fresh),
            }
        result["sizes"] = sizes
        still = sorted(
            key
            for key in (current.direct() if current is not None else set[str]())
            - candidate.direct()
            if key in candidate.packages
        )
        if still:
            warnings.append({"code": "still_needed", "packages": still})
        large = sorted(
            {
                str(item.get("name"))
                for entries in candidate.platforms.values()
                for item in entries
                if int(cast("int", item.get("size") or 0)) > LARGE_BYTES
            }
        )
        if large:
            warnings.append({"code": "large_package", "packages": large})
        with self._lock, self.sessions() as session:
            row = session.get(PythonPackageSet, draft_id)
            if row is None or row.status != "checking":
                return "failed"
            row.lock, row.lock_hash, row.manifests = lock, lock_hash, manifests
            row.check = {**(row.check or {}), **result, "state": "running"}
            session.commit()
        # 下載：只下載有裝置的平台，內附的預設套件（Worker 自己複製）不下載
        progress.step = "download"
        bundled = self._bundled_pairs()
        wanted: dict[str, dict[str, object]] = {}
        for tag in self.platforms_in_use():
            for item in candidate.platforms.get(tag, []):
                pair = (normalize(str(item.get("name"))), str(item.get("version")), tag)
                sha = str(item.get("sha256"))
                if pair not in bundled and not self._wheel_path(sha).is_file():
                    wanted[sha] = item
        try:
            self._download_all(list(wanted.values()), ranked, http, settings, progress)
        except DownloadError as error:
            errors.append({"code": "download_failed", "detail": str(error)})
            self._step(result, "download", "failed")
            return "failed"
        self._step(result, "download", "passed", files=len(wanted))
        # 雜湊另外核對、冷卻期（來源沒有上架時間時）、wheel 的內容
        progress.step = "verify"
        new_files = list(
            {
                str(item.get("sha256")): item
                for entries in candidate.platforms.values()
                for item in entries
                if str(item.get("sha256")) not in known
            }.values()
        )
        verify_ok = self._verify(
            new_files, source, http, settings, moment, upload_times, requirements, errors, warnings
        )
        if not verify_ok:
            self._step(result, "verify", "failed")
            return "failed"
        self._step(result, "verify", "passed")
        # 在伺服器的平台組成環境並 import 直接加的套件
        progress.step = "import"
        if self.platform not in candidate.platforms:
            warnings.append({"code": "import_skipped", "platform": self.platform})
            self._step(result, "import", "skipped")
            return "passed"
        runtime = self._server_runtime()
        if runtime is None:
            warnings.append({"code": "import_skipped", "platform": self.platform})
            self._step(result, "import", "skipped")
            return "passed"
        package_set = self._package_set(
            candidate, self.platform, number=(draft.base_number or 0) + 1
        )
        try:
            prepared = prepare_packages(
                runtime,
                package_set,
                fetch=self._fetch_local(ranked, http),
                environ=self.environ,
            )
        except PackagesUnavailableError as error:
            errors.append(
                {"code": "import_failed", "platform": self.platform, "detail": str(error)}
            )
            self._step(result, "import", "failed")
            return "failed"
        self._step(
            result, "import", "passed", platform=self.platform, preparedMs=prepared.prepared_ms
        )
        return "passed"

    def _verify(
        self,
        files: Sequence[Mapping[str, object]],
        source: Source,
        http: Http,
        settings: PackageSettings,
        moment: datetime,
        upload_times: bool,
        requirements: Sequence[Requirement],
        errors: list[dict[str, object]],
        warnings: list[dict[str, object]],
    ) -> bool:
        ok = True
        allow_new = {item.key for item in requirements if item.allow_new}
        unverified: list[str] = []
        young: set[str] = set()
        for item in files:
            name, version = str(item.get("name")), str(item.get("version"))
            sha, filename = str(item.get("sha256")), str(item.get("filename"))
            if source.id != "pypi" or not upload_times:
                info = self._pypi_file(http, name, version, filename)
                if info is None:
                    unverified.append(filename)
                else:
                    digest, uploaded = info
                    if digest != sha:
                        ok = False
                        errors.append({"code": "hash_mismatch", "file": filename})
                    if (
                        not upload_times
                        and uploaded is not None
                        and settings.cooldown_days > 0
                        and normalize(name) not in allow_new
                        and moment - uploaded < timedelta(days=settings.cooldown_days)
                    ):
                        young.add(f"{name} {version}")
            path = self._wheel_path(sha)
            if path.is_file():
                try:
                    tops, pth = _wheel_tops(path)
                except (OSError, zipfile.BadZipFile) as error:
                    ok = False
                    errors.append({"code": "bad_wheel", "file": filename, "detail": str(error)})
                    continue
                clash = sorted(
                    top
                    for top in tops
                    if top in sys.stdlib_module_names
                    or top == "rpa_script"
                    or top.startswith("rpa_")
                )
                if clash:
                    ok = False
                    errors.append({"code": "module_conflict", "file": filename, "modules": clash})
                if pth:
                    warnings.append({"code": "pth_file", "file": filename})
        if unverified:
            warnings.append(
                {"code": "hash_unverified", "files": sorted(unverified)[:20], "source": source.id}
            )
        if young:
            ok = False
            errors.append(
                {"code": "cooldown", "packages": sorted(young), "days": settings.cooldown_days}
            )
        return ok

    def _pypi_file(
        self, http: Http, name: str, version: str, filename: str
    ) -> tuple[str, datetime | None] | None:
        """pypi.org 的 JSON API 記的 sha256 與上架時間；連不上時回傳 None。"""
        try:
            data = http.json(f"{self.pypi_api}/{normalize(name)}/{version}/json", timeout=20)
        except Exception:
            return None
        urls = cast("dict[str, object]", data).get("urls") if isinstance(data, dict) else None
        for raw in cast("list[dict[str, object]]", urls if isinstance(urls, list) else []):
            if raw.get("filename") == filename:
                digests = cast("dict[str, object]", raw.get("digests") or {})
                stamp = raw.get("upload_time_iso_8601")
                uploaded = None
                if isinstance(stamp, str):
                    with contextlib.suppress(ValueError):
                        uploaded = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
                return str(digests.get("sha256") or ""), uploaded
        return None

    # ------------------------------------------------------------ 發布

    def publish(self, *, note: str = "", actor: str | None = None) -> Revision:
        """草稿檢查通過才能發布成下一個號碼（D5）。"""
        with self._lock, self.sessions() as session:
            row = self._draft_row(session)
            if row is None:
                raise not_found("package_no_draft", t("pypackages.error_no_draft"))
            if row.status != "checked":
                raise conflict("package_not_checked", t("pypackages.error_not_checked"))
            highest = session.scalar(
                select(func.max(PythonPackageSet.number)).where(PythonPackageSet.runtime == RUNTIME)
            )
            row.number = int(highest or 0) + 1
            row.status = "published"
            row.published_by = actor
            row.published_at = now()
            if note.strip():
                row.note = f"{row.note}\n{note.strip()}" if row.note else note.strip()[:2000]
            row.updated_at = now()
            session.commit()
            revision = _revision(row)
        self.sweep()
        return revision

    # ------------------------------------------------------------ 給 Worker

    def _package_set(
        self, revision: Revision, platform: str, *, number: int | None = None
    ) -> PackageSet:
        entries = revision.platforms.get(platform, [])
        files = tuple(
            PackageFile(
                name=str(item.get("name")),
                version=str(item.get("version")),
                filename=str(item.get("filename")),
                sha256=str(item.get("sha256")),
                size=cast("int | None", item.get("size")),
            )
            for item in entries
        )
        present = {normalize(file.name) for file in files}
        return PackageSet(
            revision=number or revision.number or 1,
            lock=revision.lock_hash or "0" * 64,
            platform=platform,
            files=files,
            direct=tuple(sorted(key for key in revision.direct() if key in present)),
        )

    def package_set(self, platform: str, number: int | None = None) -> PackageSet | None:
        """這個平台的清單（任務帶著它）；平台不在清單裡時回傳 None。"""
        revision = self.revision(number) if number is not None else self.current()
        if platform not in revision.platforms:
            return None
        return self._package_set(revision, platform)

    def request(self, platform: str, number: int | None = None) -> PackageRequest | None:
        """本機 worker 用的：這個平台的清單與從 wheel 庫取檔案的方法。"""
        packages = self.package_set(platform, number)
        if packages is None:
            return None
        settings = self.settings()
        http = self._http(settings)
        return PackageRequest(
            packages, self._fetch_local(self._ranked(settings, http, test=False), http)
        )

    def _wheel_path(self, sha256: str) -> Path:
        return self.wheels / f"{sha256}.whl"

    def wheel_file(self, sha256: str) -> Path | None:
        """Worker API 的檔案：在 wheel 庫裡就直接給；是某個發布版本用到的、還沒下載的，現在下載。"""
        if len(sha256) != 64 or any(char not in "0123456789abcdef" for char in sha256):
            return None
        path = self._wheel_path(sha256)
        if path.is_file():
            return path
        entry = self._published_entry(sha256)
        if entry is None:
            return None
        settings = self.settings()
        http = self._http(settings)
        self._download_one(entry, self._ranked(settings, http, test=False), http)
        return path if path.is_file() else None

    def _published_entry(self, sha256: str) -> dict[str, object] | None:
        for revision in self.history():
            for entries in revision.platforms.values():
                for item in entries:
                    if item.get("sha256") == sha256:
                        return item
        return None

    def begin_download(self, worker_id: str) -> bool:
        """Worker 要下載檔案：同時下載的 Worker 數超過設定時回傳 False（請它稍後再來）。"""
        with self._lock:
            if worker_id in self._downloading:
                return True
            if len(self._downloading) >= self.settings().worker_downloads:
                return False
            self._downloading.add(worker_id)
            return True

    def end_download(self, worker_id: str) -> None:
        with self._lock:
            self._downloading.discard(worker_id)

    def report(self, worker_id: str, data: Mapping[str, object]) -> None:
        """Worker 回報這一版的準備狀態（ready、preparing、failed）。"""
        state = data.get("state")
        if state not in ("ready", "preparing", "failed"):
            return
        revision = data.get("revision")
        progress = data.get("progress")
        self._statuses[worker_id] = {
            "revision": revision if isinstance(revision, int) else None,
            "state": state,
            "progress": progress if isinstance(progress, int | float) else None,
            "error": str(data.get("error") or "")[:500] or None,
            "at": _iso(now()),
        }

    def device_status(self, worker_id: str) -> dict[str, object] | None:
        return self._statuses.get(worker_id)

    def is_ready(self, worker_id: str, number: int) -> bool:
        status = self._statuses.get(worker_id)
        return (
            status is not None
            and status.get("revision") == number
            and status.get("state") == "ready"
        )

    def platforms_in_use(self) -> list[str]:
        """有裝置的平台：伺服器自己與已配對的 Worker 回報的。"""
        found = {self.platform, *self.devices().values()}
        return [tag for tag in PLATFORMS if tag in found]

    # ------------------------------------------------------------ 下載

    def _http(self, settings: PackageSettings) -> Http:
        return Http(settings.proxy, settings.ca_file)

    def _sources(self, settings: PackageSettings) -> list[Source]:
        if settings.source == "custom" and settings.custom_url:
            return [custom_source(settings.custom_url)]
        if settings.source not in ("auto", "custom"):
            return [item for item in PRESETS if item.id == settings.source] or [PRESETS[0]]
        return list(PRESETS)

    def _ranked(self, settings: PackageSettings, http: Http, *, test: bool = True) -> list[Source]:
        """依速度排好的來源；自動時 24 小時內沿用測速的結果（``test`` 時沒有結果就現在測）。"""
        sources = self._sources(settings)
        if settings.source != "auto":
            return sources
        cached = self._speed
        if cached is None or time.time() - cached[0] > SPEED_SECONDS:
            if not test:
                return sources
            self.speed_test()
            cached = self._speed
        if cached is None:
            return sources
        order = {result.source: index for index, result in enumerate(cached[1]) if result.ok}
        ranked = sorted(
            (item for item in sources if item.id in order), key=lambda item: order[item.id]
        )
        return ranked or sources

    def speed_test(self) -> list[SpeedResult]:
        settings = self.settings()
        http = self._http(settings)
        _, lock, _ = self._defaults_cached()
        probe = _probe(lock)
        if probe is None:
            return []
        path, sha, project = probe
        results = speed_test(http, self._sources(settings), path, sha, project, self.work / "speed")
        self._speed = (time.time(), results)
        return results

    def speed_results(self) -> dict[str, object] | None:
        if self._speed is None:
            return None
        moment, results = self._speed
        return {
            "at": datetime.fromtimestamp(moment).astimezone().isoformat(timespec="seconds"),
            "results": [item.to_json() for item in results],
        }

    def _upload_times(self, settings: PackageSettings, http: Http, source: Source) -> bool:
        """來源的 simple 索引有沒有上架時間；不知道時當成沒有（冷卻期改向 PyPI 核對，比較保險）。"""
        if source.id == "pypi":
            return True
        if self._speed is not None:
            for result in self._speed[1]:
                if result.source == source.id and result.upload_times is not None:
                    return result.upload_times
        project = next((item.key for item in self.current().requirements), "certifi")
        return has_upload_times(http, source, project) is True

    def _download_one(
        self,
        item: Mapping[str, object],
        ranked: Sequence[Source],
        http: Http,
        progress: _Progress | None = None,
    ) -> None:
        sha = str(item.get("sha256"))
        with self._lock:
            lock = self._fetch_locks.setdefault(sha, threading.Lock())
        with lock:
            target = self._wheel_path(sha)
            if target.is_file():
                return
            url = str(item.get("url") or "")
            urls = candidates(url, ranked) if url else [source.files for source in ranked]

            def count(amount: int) -> None:
                if progress is not None:
                    with self._lock:
                        progress.done_bytes += amount

            download(http, urls, target, sha, progress=count, cancel=self._closing)

    def _download_all(
        self,
        items: Sequence[Mapping[str, object]],
        ranked: Sequence[Source],
        http: Http,
        settings: PackageSettings,
        progress: _Progress,
    ) -> None:
        progress.files = len(items)
        progress.bytes = sum(int(cast("int", item.get("size") or 0)) for item in items)
        if not items:
            return

        def one(item: Mapping[str, object]) -> None:
            name = str(item.get("filename"))
            with self._lock:
                progress.current.append(name)
            try:
                self._download_one(item, ranked, http, progress)
            finally:
                with self._lock:
                    progress.current.remove(name)
                    progress.done_files += 1

        with ThreadPoolExecutor(max_workers=settings.parallel) as pool:
            for future in [pool.submit(one, item) for item in items]:
                future.result()

    def _fetch_local(
        self, ranked: Sequence[Source], http: Http
    ) -> Callable[[PackageFile, Path, Callable[[int], None]], None]:
        """套件環境（伺服器的檢查、本機 worker）取 wheel：從 wheel 庫複製，沒有就先下載。"""

        def fetch(item: PackageFile, target: Path, progress: Callable[[int], None]) -> None:
            path = self._wheel_path(item.sha256)
            if not path.is_file():
                entry = self._published_entry(item.sha256) or self._draft_entry(item.sha256)
                if entry is None:
                    raise PackagesUnavailableError(f"{item.filename}: not in any package list")
                self._download_one(entry, ranked, http)
            shutil.copyfile(path, target)
            progress(target.stat().st_size)

        return fetch

    def _draft_entry(self, sha256: str) -> dict[str, object] | None:
        draft = self.draft()
        if draft is None:
            return None
        for entries in draft.platforms.values():
            for item in entries:
                if item.get("sha256") == sha256:
                    return item
        return None

    def _known_hashes(self, *, exclude: int | None = None) -> set[str]:
        """已經在發布的版本裡的檔案（差異的「新增下載量」不算它們）。"""
        found: set[str] = set()
        for revision in self.history():
            if revision.id == exclude:
                continue
            for entries in revision.platforms.values():
                found.update(str(item.get("sha256")) for item in entries)
        return found

    def _defaults_cached(self) -> tuple[list[Requirement], str, dict[str, object]]:
        with self._lock:
            cached = self._defaults_data
            if cached is None:
                cached = load_defaults(self.defaults)
                self._defaults_data = cached
            return cached

    def _bundled_pairs(self) -> set[tuple[str, str, str]]:
        """內附運行環境裡的套件（每個平台的 名稱、版本）：Worker 自己複製，伺服器不下載。"""
        _, _, manifests = self._defaults_cached()
        platforms = cast("dict[str, list[dict[str, object]]]", manifests["platforms"])
        return {
            (normalize(str(item.get("name"))), str(item.get("version")), tag)
            for tag, entries in platforms.items()
            for item in entries
        }

    def _server_runtime(self) -> PreparedRuntime | None:
        if self.runtime is None:
            return None
        try:
            return self.runtime()
        except RuntimeUnavailableError:
            return None

    def sweep(self, now_seconds: float | None = None) -> int:
        """刪掉不再被保留的版本用到的 wheel（最近 keep_versions 個發布的版本與草稿）。"""
        settings = self.settings()
        keep: set[str] = set()
        for revision in self.history()[: settings.keep_versions]:
            for entries in revision.platforms.values():
                keep.update(str(item.get("sha256")) for item in entries)
        draft = self.draft()
        if draft is not None:
            for entries in draft.platforms.values():
                keep.update(str(item.get("sha256")) for item in entries)
        moment = time.time() if now_seconds is None else now_seconds
        removed = 0
        for path in self.wheels.glob("*.whl") if self.wheels.is_dir() else ():
            if path.stem in keep:
                continue
            with contextlib.suppress(OSError):
                if moment - path.stat().st_mtime > WHEEL_GRACE_DAYS * 86400:
                    path.unlink()
                    removed += 1
        return removed

    # ------------------------------------------------------------ 設定

    def settings(self) -> PackageSettings:
        with self.sessions() as session:
            row = session.get(Setting, SETTING_KEY)
            return PackageSettings.from_json(row.value) if row is not None else PackageSettings()

    def save_settings(self, data: Mapping[str, object]) -> PackageSettings:
        merged = {**self.settings().to_json(), **data}
        settings = PackageSettings.from_json(merged)
        if settings.source == "custom" and not settings.custom_url.startswith(
            ("https://", "http://")
        ):
            raise invalid("package_custom_url", t("pypackages.error_custom_url"))
        if settings.proxy and not settings.proxy.startswith(("https://", "http://")):
            raise invalid("package_proxy", t("pypackages.error_proxy"))
        if settings.ca_file and not Path(settings.ca_file).is_file():
            raise invalid("package_ca_file", t("pypackages.error_ca_file"))
        with self.sessions() as session:
            row = session.get(Setting, SETTING_KEY)
            if row is None:
                session.add(Setting(key=SETTING_KEY, value=settings.to_json()))
            else:
                row.value = settings.to_json()
            session.commit()
        self._speed = None
        return settings

    # ------------------------------------------------------------ 找套件、影響

    def lookup(self, query: str) -> dict[str, object]:
        """名稱查詢；輸入的是 import 名稱時換成套件名稱（:data:`IMPORT_NAMES`）。"""
        text = query.strip()
        if not text:
            raise invalid("package_invalid_name", t("pypackages.error_invalid_name"))
        name = IMPORT_NAMES.get(text, IMPORT_NAMES.get(text.split(".", 1)[0], text))
        for key, tops in self._current_tops().items():
            if text in tops:
                name = key
                break
        settings = self.settings()
        http = self._http(settings)
        ranked = self._ranked(settings, http, test=False)
        try:
            found = lookup(http, ranked[0], name, cooldown_days=settings.cooldown_days)
        except PackageLookupError as error:
            if error.code == "not_found":
                raise not_found(
                    "package_not_found", t("pypackages.error_not_found", name=name)
                ) from error
            raise ServiceError(
                502,
                f"package_{error.code}",
                t(f"pypackages.error_{error.code}", name=name),
                detail=error.detail,
            ) from error
        key = str(found["key"])
        current = self.current()
        found["import"] = text if name != text else None
        found["inList"] = key in current.direct()
        found["installed"] = current.packages.get(key, {}).get("version")
        found["blocked"] = blocked_reason(key)
        found["source"] = ranked[0].id
        return found

    def _current_tops(self) -> dict[str, set[str]]:
        current = self.current()
        return {
            key: self.top_levels(key, str(item.get("version")))
            for key, item in current.packages.items()
        }

    def top_levels(self, key: str, version: str) -> set[str]:
        """套件的最上層模組：wheel 庫裡的 wheel、伺服器的內附運行環境，都沒有時用名稱推測。"""
        cached = self._tops.get((key, version))
        if cached is not None:
            return cached
        found: set[str] = set()
        for revision in self.history()[:3]:
            for entries in revision.platforms.values():
                for item in entries:
                    if (
                        normalize(str(item.get("name"))) == key
                        and str(item.get("version")) == version
                    ):
                        path = self._wheel_path(str(item.get("sha256")))
                        if path.is_file():
                            with contextlib.suppress(OSError, zipfile.BadZipFile):
                                found = _wheel_tops(path)[0]
                    if found:
                        break
        if not found:
            runtime = self._server_runtime()
            if runtime is not None:
                found = _runtime_tops(runtime.root, key)
        if not found:
            found = {
                module for module, package in IMPORT_NAMES.items() if normalize(package) == key
            }
            found.add(key.replace("-", "_"))
        self._tops[(key, version)] = found
        return found

    def impact(self, name: str) -> list[dict[str, object]]:
        """用到這個套件的場景（ast 掃描運行環境模式的場景，已發布與草稿）。"""
        key = normalize(name)
        current = self.current()
        version = str(current.packages.get(key, {}).get("version") or "")
        modules = self.top_levels(key, version)
        found: list[dict[str, object]] = []
        for scene in self.scenes():
            used = sorted(scene_imports(scene) & modules)
            if used:
                found.append(
                    {
                        "sceneId": scene.scene_id,
                        "name": scene.name,
                        "domainId": scene.domain_id,
                        "number": scene.number,
                        "published": scene.published,
                        "modules": used,
                    }
                )
        return found

    def missing_modules(self) -> list[dict[str, object]]:
        """場景 import 了、但目前的套件沒有的模組，附建議的套件。"""
        known: set[str] = set()
        for tops in self._current_tops().values():
            known |= tops
        missing: dict[str, list[dict[str, object]]] = {}
        for scene in self.scenes():
            for module in sorted(scene_imports(scene) - known):
                missing.setdefault(module, []).append(
                    {
                        "sceneId": scene.scene_id,
                        "name": scene.name,
                        "number": scene.number,
                        "published": scene.published,
                    }
                )
        return [
            {"module": module, "package": suggest_package(module), "scenes": scenes}
            for module, scenes in sorted(missing.items())
        ]


def _changed(current: Revision | None, requirements: Sequence[Requirement]) -> list[str]:
    """草稿裡改了版本條件或允許新版本的套件（解析時不沿用上一版鎖定的版本）。"""
    before = {item.key: item for item in current.requirements} if current is not None else {}
    found: list[str] = []
    for item in requirements:
        old = before.get(item.key)
        if old is not None and (old.spec, old.allow_new) != (item.spec, item.allow_new):
            found.append(item.key)
    return found


def suggest_package(module: str) -> str:
    """缺的模組建議加哪個套件。"""
    top = module.split(".", 1)[0]
    return IMPORT_NAMES.get(top, top.replace("_", "-"))


def _runtime_tops(root: Path, key: str) -> set[str]:
    from rpa_runner.pypackages import base_packages

    for (name, _version), dist in base_packages(root).items():
        if name != key:
            continue
        listed = dist.dist_info / "top_level.txt"
        if listed.is_file():
            return {
                line.strip()
                for line in listed.read_text(encoding="utf-8").splitlines()
                if line.strip().isidentifier()
            }
        tops: set[str] = set()
        for relative in dist.files:
            first = relative.split("/", 1)[0]
            if first.endswith((".dist-info", ".data")) or first == "__pycache__":
                continue
            tops.add(first.split(".", 1)[0] if "/" not in relative else first)
        return {top for top in tops if top.isidentifier()}
    return set()
