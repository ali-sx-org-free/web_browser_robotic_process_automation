"""遠端 worker 與伺服器管理的套件版本（ADR 0027）：任務帶著套件清單、下載 wheel（續傳、
伺服器忙時等一下）、閒置時先準備並回報狀態。對本機的假 Worker API 測試，不連網、不需要運行環境。
"""

import hashlib
import json
import threading
import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from rpa_runner.pypackages import PackageFile, PackageSet, PreparedPackages
from rpa_runner.pyruntime import PreparedRuntime, RuntimeUnavailableError
from rpa_worker import remote
from rpa_worker.environment import WorkerInfo
from rpa_worker.protocol import API_PREFIX, JobPayload
from rpa_worker.remote import RemoteJobSource, WorkerApiError, WorkerClient

TOKEN = "t0ken"
DATA = bytes(range(256)) * 40
SHA = hashlib.sha256(DATA).hexdigest()
ITEM = PackageFile("demo", "1.0", "demo-1.0-py3-none-any.whl", SHA, len(DATA))
PACKAGES = PackageSet(revision=3, lock="d" * 64, platform="linux-x86_64", files=(ITEM,))


@dataclass
class Api:
    busy: int = 0
    """前幾次下載回 503。"""
    cut: list[int] = field(default_factory=list[int])
    """每一次下載只送這麼多位元組就斷線（用完就送完整的）。"""
    ranges: list[str] = field(default_factory=list[str])
    statuses: list[dict[str, object]] = field(default_factory=list[dict[str, object]])
    claims: list[dict[str, object]] = field(default_factory=list[dict[str, object]])


@contextmanager
def serving(api: Api) -> Generator[str]:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            return

        def _json(self, status: int, data: object) -> None:
            raw = b"" if data is None else json.dumps(data).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            if status == 503:
                self.send_header("Retry-After", "0")
            self.end_headers()
            self.wfile.write(raw)

        def do_POST(self) -> None:
            length = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(length) or b"{}")
            path = self.path.removeprefix(API_PREFIX)
            if path == "/python-packages/status":
                api.statuses.append(body)
                self._json(204, None)
            elif path == "/hello":
                self._json(200, {"worker": "box"})
            elif path == "/claim":
                self._json(200, api.claims.pop(0)) if api.claims else self._json(204, None)
            else:
                self._json(404, {"error": {"code": "not_found", "message": path}})

        def do_GET(self) -> None:
            path = self.path.removeprefix(API_PREFIX)
            if (self.headers.get("Authorization") or "") != f"Bearer {TOKEN}":
                self._json(401, {"error": {"code": "worker_unauthorized", "message": "x"}})
                return
            if path != f"/python-packages/files/{SHA}":
                self._json(404, {"error": {"code": "package_file_not_found", "message": "x"}})
                return
            if api.busy:
                api.busy -= 1
                self._json(503, {"error": {"code": "packages_busy", "message": "busy"}})
                return
            header = self.headers.get("Range") or ""
            api.ranges.append(header)
            start = int(header[6:-1]) if header.startswith("bytes=") else 0
            self.send_response(206 if start else 200)
            self.send_header("Content-Length", str(len(DATA) - start))
            self.end_headers()
            limit = api.cut.pop(0) if api.cut else None
            if limit is not None:
                self.wfile.write(DATA[start : start + limit])
                self.wfile.flush()
                self.close_connection = True
                return
            self.wfile.write(DATA[start:])

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()


def ignore(count: int) -> None:
    del count


def make_source(url: str, tmp_path: Path) -> RemoteJobSource:
    info = WorkerInfo(name="box", fingerprint="same", runtimes=("1.0.0",), platform="linux-x86_64")
    return RemoteJobSource(WorkerClient(url, TOKEN, timeout=5), info, tmp_path / "work")


def test_payload_carries_the_package_set() -> None:
    payload = JobPayload(run_id="r1", files={"scenario.yaml": b"x"}, python_packages=PACKAGES)
    data = payload.to_json()
    assert data["pythonPackages"] == PACKAGES.to_json()
    parsed = JobPayload.from_json(data, state_path=Path("state.json"))
    assert parsed.python_packages == PACKAGES
    assert (
        JobPayload.from_json({**data, "pythonPackages": None}, state_path=Path("s")).python_packages
        is None
    )
    with pytest.raises(ValueError, match="pythonPackages"):
        JobPayload.from_json({**data, "pythonPackages": {"revision": 0}}, state_path=Path("s"))


def test_fetch_resumes_and_waits_when_busy(tmp_path: Path) -> None:
    api = Api(busy=1, cut=[1000, 3000])
    seen: list[int] = []
    with serving(api) as url:
        source = make_source(url, tmp_path)
        target = tmp_path / ".part"
        source.fetch_package(ITEM, target, seen.append)
    assert target.read_bytes() == DATA
    assert sum(seen) == len(DATA)
    assert api.ranges == ["", "bytes=1000-", "bytes=4000-"]


def test_fetch_gives_up_on_missing_files(tmp_path: Path) -> None:
    missing = PackageFile("x", "1", "x-1-py3-none-any.whl", "0" * 64, 10)
    with serving(Api()) as url:
        source = make_source(url, tmp_path)
        with pytest.raises(WorkerApiError) as error:
            source.fetch_package(missing, tmp_path / ".part", ignore)
    assert error.value.status == 404


def test_idle_worker_prepares_and_reports(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    prepared: list[tuple[str, PackageSet]] = []
    runtime = PreparedRuntime(
        root=tmp_path,
        version="1.0.0",
        platform="linux-x86_64",
        python_version="3",
        reused=True,
        prepared_ms=0,
    )

    def fake_prepare(
        found: PreparedRuntime, packages: PackageSet, *, fetch: Callable[..., None]
    ) -> PreparedPackages:
        target = tmp_path / ".wheel"
        fetch(packages.files[0], target, ignore)
        assert target.read_bytes() == DATA
        prepared.append((found.version, packages))
        return PreparedPackages(
            root=tmp_path,
            python=tmp_path / "python",
            revision=packages.revision,
            lock=packages.lock,
            bundled=False,
            reused=False,
            prepared_ms=1,
        )

    def found_runtime(major: str) -> PreparedRuntime:
        assert major == "1"
        return runtime

    monkeypatch.setattr(remote, "prepare_runtime", found_runtime)
    monkeypatch.setattr(remote, "prepare_packages", fake_prepare)
    api = Api(claims=[{"pythonPackages": {"runtime": "1", "packages": PACKAGES.to_json()}}])
    with serving(api) as url:
        source = make_source(url, tmp_path)
        assert source.claim() is None
        thread = source._preparing  # pyright: ignore[reportPrivateUsage]
        assert thread is not None
        thread.join(10)
    assert prepared == [("1.0.0", PACKAGES)]
    assert [(item["revision"], item["state"]) for item in api.statuses] == [
        (3, "preparing"),
        (3, "ready"),
    ]


def test_failed_preparation_is_reported(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def unavailable(major: str) -> PreparedRuntime:
        raise RuntimeUnavailableError(f"no runtime {major}")

    monkeypatch.setattr(remote, "prepare_runtime", unavailable)
    api = Api()
    with serving(api) as url:
        source = make_source(url, tmp_path)
        source.prefetch({"runtime": "1", "packages": PACKAGES.to_json()})
        source.prefetch({"runtime": "1", "packages": {"revision": "bad"}})  # 格式不對：不理
        thread = source._preparing  # pyright: ignore[reportPrivateUsage]
        assert thread is not None
        thread.join(10)
        deadline = time.monotonic() + 5
        while len(api.statuses) < 2 and time.monotonic() < deadline:
            time.sleep(0.01)
    assert api.statuses[-1]["state"] == "failed"
    assert "no runtime 1" in str(api.statuses[-1]["error"])
