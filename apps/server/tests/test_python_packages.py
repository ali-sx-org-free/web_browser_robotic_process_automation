"""伺服器管理的 RPA Python 套件（ADR 0027，rpa_server.pypackages）。

套件來源是測試自己起的本機 HTTP 伺服器（PEP 691 JSON simple 索引，有上架時間、METADATA、
Range），wheel 是測試產生的純 Python 套件，不連外網。需要解析的測試用這台電腦的 uv（``RPA_UV``），
沒有 uv 時略過。「內附的運行環境」是用這次測試的 Python 建的 venv，裡面裝了預設套件 demo-a 1.0。
"""

import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import tomllib
import zipfile
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import cast

import pytest
from sqlalchemy.orm import Session, sessionmaker

from rpa_runner.pypackages import install_wheel, site_packages
from rpa_runner.pyruntime import PreparedRuntime, platform_tag
from rpa_server.config import sqlite_url
from rpa_server.db import create_db_engine, upgrade
from rpa_server.errors import ServiceError
from rpa_server.pypackages.finder import SceneSource
from rpa_server.pypackages.locks import (
    PLATFORMS,
    PYTHON_VERSION,
    Requirement,
    parse_lock,
    parse_requirements_in,
)
from rpa_server.pypackages.resolve import (
    platform_manifest,
    resolve_platform,
    resolve_universal,
    uv_environment,
)
from rpa_server.pypackages.service import (
    DEFAULTS,
    PackageService,
    PackageSettings,
    _via_from_requirements_lock,  # pyright: ignore[reportPrivateUsage]
    load_defaults,
)
from rpa_server.pypackages.sources import (
    DownloadError,
    Http,
    Source,
    candidates,
    custom_source,
    download,
    speed_test,
)

ROOT = Path(__file__).resolve().parents[3]
OLD = datetime(2026, 1, 1, tzinfo=UTC)
UV = shutil.which("uv")
needs_uv = pytest.mark.skipif(UV is None, reason="沒有 uv")


# ---------------------------------------------------------------- 假的套件來源


def make_wheel(
    folder: Path,
    name: str,
    version: str,
    files: Mapping[str, bytes],
    *,
    requires: tuple[str, ...] = (),
    tag: str = "py3-none-any",
    summary: str = "",
) -> tuple[Path, bytes]:
    """一個 wheel 與它的 METADATA。"""
    folder.mkdir(parents=True, exist_ok=True)
    stem = f"{name.replace('-', '_')}-{version}"
    path = folder / f"{stem}-{tag}.whl"
    metadata = f"Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n"
    if summary:
        metadata += f"Summary: {summary}\n"
    metadata += "".join(f"Requires-Dist: {item}\n" for item in requires) + "\nbody\n"
    content = dict(files)
    content[f"{stem}.dist-info/METADATA"] = metadata.encode()
    pure = "true" if tag.endswith("-any") else "false"
    content[f"{stem}.dist-info/WHEEL"] = (
        f"Wheel-Version: 1.0\nGenerator: test\nRoot-Is-Purelib: {pure}\nTag: {tag}\n".encode()
    )
    rows: list[str] = []
    for key, data in content.items():
        digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()
        rows.append(f"{key},sha256={digest},{len(data)}")
    rows.append(f"{stem}.dist-info/RECORD,,")
    content[f"{stem}.dist-info/RECORD"] = ("\n".join(rows) + "\n").encode()
    with zipfile.ZipFile(path, "w") as archive:
        for key, data in content.items():
            archive.writestr(key, data)
    return path, metadata.encode()


@dataclass
class Release:
    name: str
    version: str
    filename: str
    data: bytes
    metadata: bytes
    uploaded: datetime

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.data).hexdigest()


@dataclass
class Index:
    """本機的套件來源：/simple/<名稱>/（JSON）、/packages/<檔名>、/pypi/<名稱>/<版本>/json。"""

    folder: Path
    releases: dict[str, list[Release]] = field(default_factory=dict[str, list[Release]])
    requests: list[tuple[str, str]] = field(default_factory=list[tuple[str, str]])
    """（路徑, Range 標頭）。"""
    cut: dict[str, int] = field(default_factory=dict[str, int])
    """檔名 → 第一次只送這麼多位元組就斷線。"""
    missing: set[str] = field(default_factory=set[str])
    """這些檔名回 404。"""
    url: str = ""

    def add(
        self,
        name: str,
        version: str,
        files: Mapping[str, bytes],
        *,
        requires: tuple[str, ...] = (),
        tag: str = "py3-none-any",
        uploaded: datetime = OLD,
        summary: str = "",
    ) -> Release:
        path, metadata = make_wheel(
            self.folder, name, version, files, requires=requires, tag=tag, summary=summary
        )
        release = Release(name, version, path.name, path.read_bytes(), metadata, uploaded)
        self.releases.setdefault(name, []).append(release)
        return release

    def find(self, filename: str) -> Release | None:
        for items in self.releases.values():
            for item in items:
                if item.filename == filename:
                    return item
        return None

    @property
    def simple(self) -> str:
        return f"{self.url}/simple"

    def source(self) -> Source:
        return custom_source(self.simple)

    def handler(self) -> type[BaseHTTPRequestHandler]:
        index = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format: str, *args: object) -> None:
                return

            def _send(self, status: int, body: bytes, content_type: str) -> None:
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                if self.command != "HEAD":
                    self.wfile.write(body)

            def do_HEAD(self) -> None:
                self.do_GET()

            def do_GET(self) -> None:
                path = self.path.split("?", 1)[0]
                index.requests.append((path, self.headers.get("Range") or ""))
                parts = [part for part in path.split("/") if part]
                if parts[:1] == ["simple"] and len(parts) == 2:
                    self._simple(parts[1])
                elif parts[:1] == ["packages"] and len(parts) == 2:
                    self._file(parts[1])
                elif parts[:1] == ["pypi"] and len(parts) == 4:
                    self._pypi(parts[1], parts[2])
                else:
                    self._send(404, b"not found", "text/plain")

            def _simple(self, key: str) -> None:
                items = index.releases.get(key)
                if not items:
                    self._send(404, b"not found", "text/plain")
                    return
                files = [
                    {
                        "filename": item.filename,
                        "url": f"{index.url}/packages/{item.filename}",
                        "hashes": {"sha256": item.sha256},
                        "size": len(item.data),
                        "upload-time": item.uploaded.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                        "core-metadata": {"sha256": hashlib.sha256(item.metadata).hexdigest()},
                        "requires-python": ">=3.9",
                    }
                    for item in items
                ]
                body = {
                    "meta": {"api-version": "1.1"},
                    "name": key,
                    "versions": sorted({item.version for item in items}),
                    "files": files,
                }
                self._send(200, json.dumps(body).encode(), "application/vnd.pypi.simple.v1+json")

            def _file(self, filename: str) -> None:
                metadata = filename.endswith(".metadata")
                item = index.find(filename.removesuffix(".metadata"))
                if item is None or filename in index.missing:
                    self._send(404, b"not found", "text/plain")
                    return
                if metadata:
                    self._send(200, item.metadata, "text/plain")
                    return
                data = item.data
                start = 0
                header = self.headers.get("Range") or ""
                if header.startswith("bytes=") and header.endswith("-"):
                    start = int(header[6:-1])
                    if start >= len(data):
                        self._send(416, b"", "text/plain")
                        return
                limit = index.cut.pop(filename, None)
                if start:
                    self.send_response(206)
                    self.send_header("Content-Range", f"bytes {start}-{len(data) - 1}/{len(data)}")
                else:
                    self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Length", str(len(data) - start))
                self.end_headers()
                if self.command == "HEAD":
                    return
                if limit is not None:
                    self.wfile.write(data[start : start + limit])
                    self.wfile.flush()
                    self.close_connection = True
                    return
                self.wfile.write(data[start:])

            def _pypi(self, key: str, version: str) -> None:
                items = [item for item in index.releases.get(key, []) if item.version == version]
                if not items:
                    self._send(404, b"not found", "text/plain")
                    return
                urls = [
                    {
                        "filename": item.filename,
                        "digests": {"sha256": item.sha256},
                        "upload_time_iso_8601": item.uploaded.isoformat().replace("+00:00", "Z"),
                    }
                    for item in items
                ]
                self._send(200, json.dumps({"urls": urls}).encode(), "application/json")

        return Handler


def module(name: str, text: str = "") -> dict[str, bytes]:
    return {f"{name}/__init__.py": (text or f"NAME = {name!r}\n").encode()}


@pytest.fixture(scope="module")
def index(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Index]:
    found = Index(tmp_path_factory.mktemp("index"))
    found.add("demo-a", "1.0", module("demo_a"), summary="Demo A")
    found.add("demo-b", "1.0", module("demo_b"), requires=("demo-a>=1",))
    found.add(
        "demo-b",
        "2.0",
        module("demo_b", "NAME = 'demo_b 2'\n"),
        requires=("demo-a>=1",),
        uploaded=datetime.now(UTC) - timedelta(days=1),
    )
    found.add("demo-win", "1.0", module("demo_win"), tag="py3-none-win_amd64")
    found.add("demo-clash", "1.0", module("json"))
    server = ThreadingHTTPServer(("127.0.0.1", 0), found.handler())
    found.url = f"http://127.0.0.1:{server.server_address[1]}"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    with pytest.MonkeyPatch.context() as patch:
        # 本機的假來源不走這台電腦設定的代理
        patch.setenv("NO_PROXY", "127.0.0.1,localhost")
        patch.setenv("no_proxy", "127.0.0.1,localhost")
        yield found
    server.shutdown()
    server.server_close()


@pytest.fixture(autouse=True)
def _reset_index(index: Index) -> None:
    index.requests.clear()
    index.cut.clear()
    index.missing.clear()


@pytest.fixture(scope="module")
def base_root(tmp_path_factory: pytest.TempPathFactory, index: Index) -> Path:
    """假的內附運行環境：venv 裡裝了 demo-a 1.0（測試用的預設套件）。"""
    root = tmp_path_factory.mktemp("base") / "runtime"
    subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(root)], check=True)
    site = site_packages(root)
    assert site is not None
    release = index.releases["demo-a"][0]
    wheel = tmp_path_factory.mktemp("base-wheel") / release.filename
    wheel.write_bytes(release.data)
    install_wheel(wheel, site, root)
    return root


@pytest.fixture(scope="module")
def test_defaults(tmp_path_factory: pytest.TempPathFactory, index: Index) -> Path:
    """測試用的預設套件 #1（只有 demo-a），和 tools/build_python_runtime.py 產生的檔案相同格式。"""
    if UV is None:
        pytest.skip("沒有 uv")
    folder = tmp_path_factory.mktemp("defaults")
    work = tmp_path_factory.mktemp("defaults-work")
    requirements = [Requirement("demo-a", ">=1", default=True, note="Demo")]
    env = uv_environment(Http(), work / "uv-cache", os.environ)
    source = index.source()
    resolved = resolve_universal(Path(UV), requirements, source, work, env)
    (folder / "requirements.in").write_text("# Demo\ndemo-a>=1\n", encoding="utf-8")
    (folder / "requirements.lock").write_text(
        "demo-a==1.0 \\\n    --hash=sha256:00\n    # via -r requirements.in\n", encoding="utf-8"
    )
    (folder / "pylock.toml").write_text(resolved.lock, encoding="utf-8")
    for tag in PLATFORMS:
        resolve_platform(Path(UV), requirements, resolved.packages, source, tag, work, env)
        shutil.copyfile(work / tag / "pylock.toml", folder / f"pylock.{tag}.toml")
    return folder


@pytest.fixture
def sessions(tmp_path: Path) -> sessionmaker[Session]:
    engine = create_db_engine(sqlite_url(tmp_path / "rpa.db"))
    upgrade(engine)
    return sessionmaker(engine, expire_on_commit=False)


@dataclass
class Scenes:
    items: list[SceneSource] = field(default_factory=list[SceneSource])

    def __call__(self) -> list[SceneSource]:
        return self.items


def make_service(
    sessions: sessionmaker[Session],
    tmp_path: Path,
    index: Index,
    *,
    defaults: Path = DEFAULTS,
    runtime: Callable[[], PreparedRuntime] | None = None,
    scenes: Scenes | None = None,
) -> PackageService:
    environ = {**os.environ, "RPA_CACHE_DIR": str(tmp_path / "cache")}
    if UV is not None:
        environ["RPA_UV"] = UV
    service = PackageService(
        sessions,
        tmp_path / "data",
        scenes=scenes or Scenes(),
        runtime=runtime,
        environ=environ,
        defaults=defaults,
        pypi_api=f"{index.url}/pypi",
    )
    service.save_settings({"source": "custom", "customUrl": index.simple})
    return service


@pytest.fixture
def runtime(base_root: Path) -> PreparedRuntime:
    return PreparedRuntime(
        root=base_root,
        version="1.0.0",
        platform=platform_tag(),
        python_version="3",
        reused=True,
        prepared_ms=0,
    )


@pytest.fixture
def service(
    sessions: sessionmaker[Session],
    tmp_path: Path,
    index: Index,
    test_defaults: Path,
    runtime: PreparedRuntime,
) -> Iterator[PackageService]:
    found = make_service(sessions, tmp_path, index, defaults=test_defaults, runtime=lambda: runtime)
    yield found
    found.close()


def rows(value: object) -> list[dict[str, object]]:
    """檢查結果裡的清單（步驟、錯誤、警告）。"""
    assert isinstance(value, list)
    return cast("list[dict[str, object]]", value)


def checked(service: PackageService) -> dict[str, object]:
    service.wait(120)
    draft = service.draft()
    assert draft is not None
    assert draft.check is not None
    return dict(draft.check)


# ---------------------------------------------------------------- 內附的預設套件


def test_defaults_match_bundled_runtime() -> None:
    """預設套件 #1 和內附的運行環境（runtimes/python）相同：要求、版本、Python 版本。"""
    runtime = tomllib.loads((ROOT / "runtimes/python/runtime.toml").read_text(encoding="utf-8"))
    assert runtime["python"] == PYTHON_VERSION
    bundled = parse_requirements_in(
        (ROOT / "runtimes/python/requirements.in").read_text(encoding="utf-8")
    )
    requirements, lock, manifests = load_defaults()
    assert [(item.name, item.spec) for item in requirements] == [
        (item.name, item.spec) for item in bundled
    ]
    assert all(item.default for item in requirements)
    assert requirements[0].note  # 說明來自 requirements.in 的註解
    pins = {
        line.split("==", 1)[0].lower(): line.split("==", 1)[1].split()[0]
        for line in (ROOT / "runtimes/python/requirements.lock").read_text().splitlines()
        if "==" in line and not line.startswith((" ", "#"))
    }
    assert {item.key: item.version for item in parse_lock(lock)} == pins
    platforms = cast("dict[str, list[dict[str, object]]]", manifests["platforms"])
    assert sorted(platforms) == sorted(PLATFORMS)
    packages = cast("dict[str, dict[str, object]]", manifests["packages"])
    assert packages["certifi"]["via"] == ["requests"]
    assert packages["pandas"]["direct"] is True
    linux = {str(item["name"]).lower() for item in platforms["linux-x86_64"]}
    assert "pandas" in linux


def test_via_from_requirements_lock() -> None:
    text = (
        "a==1 \\\n    --hash=sha256:00\n    # via -r requirements.in\n"
        "b==2 \\\n    --hash=sha256:00\n    # via\n    #   a\n    #   c\n"
    )
    assert _via_from_requirements_lock(text) == {"a": ["requirements.in"], "b": ["a", "c"]}


# ---------------------------------------------------------------- 草稿


def test_first_revision_and_draft(
    sessions: sessionmaker[Session], tmp_path: Path, index: Index
) -> None:
    service = make_service(sessions, tmp_path, index)
    first = service.current()
    assert first.number == 1
    assert first.status == "published"
    assert service.ensure_defaults().id == first.id
    assert "pandas" in first.direct()
    assert service.draft() is None

    draft = service.add("tabulate", ">=0.9", note="表格")
    assert draft.number is None
    assert draft.status == "draft"
    assert draft.base_number == 1
    added = next(item for item in draft.requirements if item.key == "tabulate")
    assert (added.spec, added.note, added.default) == (">=0.9", "表格", False)
    assert added.added_at is not None

    # 改預設套件的版本條件：還是預設的，說明不變
    draft = service.add("requests", ">=2.32,<3")
    changed = next(item for item in draft.requirements if item.key == "requests")
    assert changed.default
    assert changed.note

    draft = service.remove("tabulate")
    assert "tabulate" not in draft.direct()
    assert service.current().number == 1  # 發布的版本不變

    with pytest.raises(ServiceError) as error:
        service.add("pip")
    assert error.value.code == "package_blocked_tool"
    with pytest.raises(ServiceError) as error:
        service.add("bad name!")
    assert error.value.code == "package_invalid_name"
    with pytest.raises(ServiceError) as error:
        service.add("tabulate", "latest")
    assert error.value.code == "package_invalid_spec"
    with pytest.raises(ServiceError) as error:
        service.remove("not-in-list")
    assert error.value.code == "package_not_in_list"
    with pytest.raises(ServiceError) as error:
        service.publish()
    assert error.value.code == "package_not_checked"

    service.discard()
    assert service.draft() is None


def test_remove_used_package_needs_reason(
    sessions: sessionmaker[Session], tmp_path: Path, index: Index
) -> None:
    scenes = Scenes(
        [
            SceneSource("s1", "報表", "d1", 3, True, {"main.py": "import openpyxl\nimport yaml\n"}),
            SceneSource("s2", "草稿", "d1", 4, False, {"main.py": "from openpyxl import load\n"}),
        ]
    )
    service = make_service(sessions, tmp_path, index, scenes=scenes)
    impact = service.impact("openpyxl")
    assert [(item["sceneId"], item["published"]) for item in impact] == [
        ("s1", True),
        ("s2", False),
    ]

    with pytest.raises(ServiceError) as error:
        service.remove("openpyxl")
    assert error.value.code == "package_in_use"
    assert error.value.status == 409
    assert len(rows(error.value.details["scenes"])) == 1

    draft = service.remove("openpyxl", reason="改用 xlsxwriter")
    assert "openpyxl" not in draft.direct()
    assert draft.note is not None
    assert "改用 xlsxwriter" in draft.note

    missing = {item["module"]: item for item in service.missing_modules()}
    assert missing["yaml"]["package"] == "PyYAML"
    assert "openpyxl" not in missing  # 目前發布的版本還有


def test_settings(sessions: sessionmaker[Session], tmp_path: Path, index: Index) -> None:
    service = make_service(sessions, tmp_path, index)
    assert service.settings().source == "custom"
    with pytest.raises(ServiceError) as error:
        service.save_settings({"source": "custom", "customUrl": "nexus/simple"})
    assert error.value.code == "package_custom_url"
    with pytest.raises(ServiceError) as error:
        service.save_settings({"proxy": "proxy:8080"})
    assert error.value.code == "package_proxy"
    with pytest.raises(ServiceError) as error:
        service.save_settings({"caFile": str(tmp_path / "missing.pem")})
    assert error.value.code == "package_ca_file"
    saved = service.save_settings({"source": "tuna", "cooldownDays": 3, "parallel": 99})
    assert (saved.source, saved.cooldown_days, saved.parallel) == ("tuna", 3, 4)
    assert service.settings() == saved
    assert PackageSettings.from_json({"source": "elsewhere"}).source == "auto"


def test_worker_download_slots(
    sessions: sessionmaker[Session], tmp_path: Path, index: Index
) -> None:
    service = make_service(sessions, tmp_path, index)
    service.save_settings({"workerDownloads": 1})
    assert service.begin_download("w1")
    assert service.begin_download("w1")  # 同一台不重複算
    assert not service.begin_download("w2")
    service.end_download("w1")
    assert service.begin_download("w2")

    service.report("w2", {"state": "ready", "revision": 1})
    assert service.is_ready("w2", 1)
    assert not service.is_ready("w2", 2)
    service.report("w2", {"state": "unknown"})
    assert service.is_ready("w2", 1)


def test_sweep_removes_unused_wheels(
    sessions: sessionmaker[Session], tmp_path: Path, index: Index
) -> None:
    service = make_service(sessions, tmp_path, index)
    current = service.current()
    used = str(current.platforms["linux-x86_64"][0]["sha256"])
    service.wheels.mkdir(parents=True)
    old = time.time() - 3 * 86400
    for name in (used, "f" * 64, "e" * 64):
        path = service.wheels / f"{name}.whl"
        path.write_bytes(b"x")
        if name != "e" * 64:
            os.utime(path, (old, old))
    assert service.sweep() == 1  # 沒用到而且放超過一天的
    assert (service.wheels / f"{used}.whl").is_file()
    assert (service.wheels / f"{'e' * 64}.whl").is_file()  # 剛下載的先留著


# ---------------------------------------------------------------- 來源與下載


def test_download_falls_back_and_resumes(tmp_path: Path, index: Index) -> None:
    release = index.releases["demo-a"][0]
    index.missing.add(release.filename)
    first = Source("first", f"{index.url}/simple", f"{index.url}/")
    target = tmp_path / "out" / release.filename
    url = f"https://files.pythonhosted.org/packages/{release.filename}"
    urls = candidates(url, [first, index.source()], known=[first])
    assert urls[-1] == url
    assert urls[0] == f"{index.url}/packages/{release.filename}"

    index.missing.clear()
    index.cut[release.filename] = 100
    seen: list[int] = []
    used = download(Http(), urls[:1], target, release.sha256, progress=seen.append)
    assert used == urls[0]
    assert target.read_bytes() == release.data
    assert sum(seen) == len(release.data)
    ranges = [header for path, header in index.requests if path.endswith(release.filename)]
    assert ranges == ["", "bytes=100-"]  # 斷線後從斷點接著下載

    target.unlink()
    with pytest.raises(DownloadError, match="sha256 mismatch"):
        download(Http(), urls[:1], target, "0" * 64)
    assert not target.exists()
    assert not list(target.parent.glob(".*.part"))


def test_speed_test_ranks_sources(tmp_path: Path, index: Index) -> None:
    release = index.releases["demo-a"][0]
    good = index.source()
    bad = Source("bad", f"{index.url}/simple", f"{index.url}/nothing/")
    results = speed_test(
        Http(), [bad, good], f"packages/{release.filename}", release.sha256, "demo-a", tmp_path
    )
    assert [(item.source, item.ok) for item in results] == [("custom", True), ("bad", False)]
    assert results[0].upload_times is True
    assert results[0].speed > 0


def test_lookup(sessions: sessionmaker[Session], tmp_path: Path, index: Index) -> None:
    service = make_service(sessions, tmp_path, index)
    found = service.lookup("demo_b")
    assert (found["name"], found["latest"], found["allowed"]) == ("demo-b", "2.0", "1.0")
    assert found["cooldown"] is True
    assert found["inList"] is False
    assert found["uploadTimes"] is True
    platforms = found["platforms"]
    assert isinstance(platforms, dict)
    assert all(platforms[tag] is not None for tag in PLATFORMS)

    win = service.lookup("demo-win")
    win_platforms = win["platforms"]
    assert isinstance(win_platforms, dict)
    assert win_platforms["windows-x86_64"] is not None
    assert win_platforms["linux-x86_64"] is None
    assert service.lookup("demo-a")["metadata"] == {
        "summary": "Demo A",
        "license": "",
        "homepage": "",
        "requires": [],
        "requiresPython": "",
    }
    with pytest.raises(ServiceError) as error:
        service.lookup("nothing-here")
    assert error.value.code == "package_not_found"


# ---------------------------------------------------------------- 檢查、發布、回退


@needs_uv
def test_check_publish_and_restore(service: PackageService, index: Index) -> None:
    first = service.current()
    assert first.number == 1
    assert first.versions() == {"demo-a": "1.0"}

    service.add("demo-b")
    service.start_check()
    with pytest.raises(ServiceError) as error:
        service.add("demo-c")  # 檢查中不能改
    assert error.value.code in ("package_checking",)
    result = checked(service)
    assert result["state"] == "passed", result
    assert result["diff"] == {"added": [["demo-b", "1.0"]], "removed": [], "changed": []}
    steps = {item["id"]: item["status"] for item in rows(result["steps"])}
    assert steps == {
        "resolve": "passed",
        "platforms": "passed",
        "download": "passed",
        "verify": "passed",
        "import": "passed",
    }
    # demo-b 2.0 還在冷卻期，用 1.0；demo-a 是內附的，伺服器不下載
    downloaded = {path for path, _ in index.requests if path.startswith("/packages/")}
    assert f"/packages/{index.releases['demo-b'][0].filename}" in downloaded
    assert f"/packages/{index.releases['demo-a'][0].filename}" not in downloaded

    second = service.publish(note="加 demo-b")
    assert second.number == 2
    assert service.current().versions() == {"demo-a": "1.0", "demo-b": "1.0"}
    packages = service.package_set(platform_tag())
    assert packages is not None
    assert packages.revision == 2
    assert [item.name for item in packages.files] == ["demo-a", "demo-b"]
    assert packages.direct == ("demo-a", "demo-b")
    assert service.wheel_file(index.releases["demo-b"][0].sha256) is not None
    assert service.wheel_file("0" * 64) is None
    assert service.wheel_file("../etc") is None

    # 管理員確認可以用冷卻期內的版本
    service.add("demo-b", allow_new=True)
    service.start_check()
    result = checked(service)
    assert result["state"] == "passed", result
    assert result["diff"] == {"added": [], "removed": [], "changed": [["demo-b", "1.0", "2.0"]]}
    assert service.publish().number == 3

    # 回到 #2：不重新解析
    service.restore(2)
    result = checked(service)
    assert result["state"] == "passed", result
    steps = {item["id"]: item["status"] for item in rows(result["steps"])}
    assert steps["resolve"] == "skipped"
    fourth = service.publish()
    assert fourth.number == 4
    assert fourth.restored_from == 2
    assert fourth.versions() == {"demo-a": "1.0", "demo-b": "1.0"}
    assert [item.number for item in service.history()] == [4, 3, 2, 1]


@needs_uv
def test_check_platform_wheels(service: PackageService) -> None:
    service.add("demo-win")
    service.start_check()
    result = checked(service)
    assert result["state"] == "failed"
    failed = {item.get("platform") for item in rows(result["errors"])}
    assert "linux-x86_64" in failed
    assert "windows-x86_64" not in failed

    # 只在 Windows 安裝：其他平台的清單沒有它
    service.add("demo-win", platforms=["windows"])
    service.start_check()
    result = checked(service)
    assert result["state"] == "passed", result
    service.publish()
    linux = service.package_set("linux-x86_64")
    windows = service.package_set("windows-x86_64")
    assert linux is not None
    assert windows is not None
    assert [item.name for item in linux.files] == ["demo-a"]
    assert [item.name for item in windows.files] == ["demo-a", "demo-win"]
    assert windows.direct == ("demo-a", "demo-win")


@needs_uv
def test_check_rejects_stdlib_module(service: PackageService) -> None:
    service.add("demo-clash")
    service.start_check()
    result = checked(service)
    assert result["state"] == "failed"
    codes = [item["code"] for item in rows(result["errors"])]
    assert codes == ["module_conflict"]


@needs_uv
def test_check_reports_resolve_errors(service: PackageService) -> None:
    service.add("demo-b", ">=3")
    service.start_check()
    result = checked(service)
    assert result["state"] == "failed"
    first = rows(result["errors"])[0]
    assert first["code"] == "resolve_failed"
    assert "demo-b" in str(first["detail"])
    draft = service.draft()
    assert draft is not None
    assert draft.status == "failed"
    service.discard()


def test_platform_manifest_from_lock(test_defaults: Path) -> None:
    lock = parse_lock((test_defaults / "pylock.windows-x86_64.toml").read_text(encoding="utf-8"))
    entries = platform_manifest(lock, "windows-x86_64")
    assert [item["name"] for item in entries] == ["demo-a"]
    assert entries[0]["uploadTime"] is not None
