"""伺服器管理的套件版本（ADR 0027）在派工與 Worker API：執行固定版本、任務帶著清單、
舊的 App、閒置時先準備、下載 wheel（續傳、同時下載的數量）、回報準備狀態。

不需要瀏覽器、不連網；遠端 worker 用 Worker API 的 TestClient（同 test_python_nodes.py）。
新的套件版本直接寫進資料庫（複製 #1），不經過 uv 的檢查（那部分在 test_python_packages.py）。
"""

from collections.abc import Iterator
from dataclasses import replace
from typing import cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx2 import Client, Response

from rpa_core.dsl.features import FEATURES
from rpa_server.config import Settings
from rpa_server.domain import now
from rpa_server.models import PythonPackageSet, Run
from rpa_server.pypackages.service import RUNTIME
from rpa_server.services import Services
from rpa_worker.environment import CAPABILITIES, PROTOCOL

JsonObject = dict[str, object]
WORKER_PORT = 8081
API = "/worker-api/v1"

NODE = """\
schemaVersion: 1
id: py-sum
name: 加總
outputs:
  total: { type: number, from: '{{ facts.total }}' }
script:
  runtime: '1'
  automation: automation.py
verify:
  - { value: '{{ facts.total }}', matches: '^[0-9]' }
"""
AUTOMATION = """\
from rpa_script import automation


@automation
def main(run):
    run.facts["total"] = 6
"""

INFO: JsonObject = {
    "name": "BOX",
    "protocol": PROTOCOL,
    "fingerprint": "x",
    "os": "Linux",
    "python": "3.13.1",
    "host": "BOX",
    "browsers": [],
    "display": False,
    "features": sorted(FEATURES),
    "runtimes": ["1.0.0"],
    "platform": "linux-x86_64",
}
NEW_APP: JsonObject = {"capabilities": sorted(CAPABILITIES)}


@pytest.fixture
def settings(settings: Settings) -> Settings:
    return replace(settings, worker_port=WORKER_PORT)


@pytest.fixture
def remote(app: FastAPI, client: Client) -> Iterator[Client]:
    with TestClient(app, base_url=f"http://testserver:{WORKER_PORT}") as other:
        yield other


@pytest.fixture(autouse=True)
def _no_local_runtime(app: FastAPI) -> None:
    """這台伺服器沒有運行環境：運行環境模式的任務都給遠端 worker。"""
    services(app).queue.runtimes = lambda: ()


def services(app: FastAPI) -> Services:
    return cast("Services", app.state.services)


def body(response: Response, status: int | None = None) -> JsonObject:
    if status is not None:
        assert response.status_code == status, response.text
    data: object = response.json()
    assert isinstance(data, dict)
    return cast("JsonObject", data)


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def register(client: Client, worker_id: str) -> str:
    created = body(client.post("/api/workers", json={"id": worker_id, "name": worker_id}), 201)
    return str(created["token"])


def hello(remote: Client, token: str, **changes: object) -> None:
    body(remote.post(f"{API}/hello", json={**INFO, **changes}, headers=auth(token)), 200)


def claim(remote: Client, token: str) -> JsonObject | None:
    response = remote.post(f"{API}/claim", json={"waitSeconds": 0}, headers=auth(token))
    if response.status_code == 204:
        return None
    return body(response, 200)


def create_node(client: Client) -> None:
    assert client.post("/api/scenes", json={"id": "py-sum", "name": "暫名"}).status_code == 201
    files = {"scenario.yaml": NODE, "automation.py": AUTOMATION}
    created = client.post("/api/scenes/py-sum/revisions", json={"baseRevision": 1, "files": files})
    assert created.status_code == 201, created.text


def validate(client: Client, target: str = "remote") -> JsonObject:
    payload: JsonObject = {"inputs": {}, "target": target}
    return body(client.post("/api/scenes/py-sum/revisions/2/validate", json=payload), 202)


def publish_copy(app: FastAPI) -> int:
    """發布一個新的套件版本（內容和 #1 相同，只為了號碼不同）。"""
    first = services(app).packages.current()
    with services(app).sessions() as session:
        moment = now()
        row = PythonPackageSet(
            runtime=RUNTIME,
            number=(first.number or 1) + 1,
            status="published",
            requirements=[item.to_json() for item in first.requirements],
            lock=first.lock,
            lock_hash="c" * 64,
            manifests=dict(first.manifests),
            created_at=moment,
            updated_at=moment,
            published_at=moment,
        )
        session.add(row)
        session.commit()
        return row.number or 0


def run_row(app: FastAPI, run_id: object) -> Run:
    with services(app).sessions() as session:
        run = session.get(Run, str(run_id))
        assert run is not None
        return run


def test_runs_pin_the_current_package_set(app: FastAPI, client: Client, remote: Client) -> None:
    create_node(client)
    token = register(client, "py-box")
    hello(remote, token, **NEW_APP)
    queued = validate(client)
    assert run_row(app, queued["id"]).python_packages == 1

    job = claim(remote, token)
    assert job is not None
    packages = cast("JsonObject", job["pythonPackages"])
    assert packages["revision"] == 1
    assert packages["platform"] == "linux-x86_64"
    names = {
        str(cast("JsonObject", item)["name"]).lower()
        for item in cast("list[object]", packages["files"])
    }
    assert "pandas" in names
    assert "requests" in cast("list[str]", packages["direct"])

    # 發布新版之後排入的執行用新的版本；之前排入的不變
    number = publish_copy(app)
    later = validate(client)
    assert run_row(app, later["id"]).python_packages == number
    assert run_row(app, queued["id"]).python_packages == 1


def test_old_apps_only_get_the_bundled_set(app: FastAPI, client: Client, remote: Client) -> None:
    create_node(client)
    old = register(client, "old-box")
    hello(remote, old)  # 沒有回報 capabilities：看不懂套件清單的 App
    first = validate(client)
    job = claim(remote, old)
    assert job is not None
    assert job["runId"] == first["id"]  # #1 和內附的運行環境相同，舊的 App 也能跑

    number = publish_copy(app)
    second = validate(client)
    assert claim(remote, old) is None
    failed = run_row(app, second["id"])
    assert failed.status == "failed"
    assert failed.error is not None
    assert f"#{number}" in failed.error
    assert "太舊" in failed.error


def test_idle_workers_prepare_the_current_set(app: FastAPI, client: Client, remote: Client) -> None:
    token = register(client, "py-box")
    hello(remote, token, **NEW_APP)
    reply = claim(remote, token)
    assert reply is not None
    assert "runId" not in reply
    hint = cast("JsonObject", reply["pythonPackages"])
    assert hint["runtime"] == RUNTIME
    assert cast("JsonObject", hint["packages"])["revision"] == 1
    assert claim(remote, token) is None  # 同一版只叫一次

    status = remote.post(
        f"{API}/python-packages/status",
        json={"revision": 1, "state": "ready"},
        headers=auth(token),
    )
    assert status.status_code == 204, status.text
    assert services(app).packages.is_ready("py-box", 1)

    # 發布新版：再叫一次
    number = publish_copy(app)
    reply = claim(remote, token)
    assert reply is not None
    assert (
        cast("JsonObject", cast("JsonObject", reply["pythonPackages"])["packages"])["revision"]
        == number
    )

    # 舊的 App、沒有運行環境的不叫
    old = register(client, "old-box")
    hello(remote, old)
    assert claim(remote, old) is None
    plain = register(client, "plain")
    hello(remote, plain, runtimes=[], **NEW_APP)
    assert claim(remote, plain) is None


def test_workers_download_wheels(app: FastAPI, client: Client, remote: Client) -> None:
    token = register(client, "py-box")
    hello(remote, token, **NEW_APP)
    packages = services(app).packages
    entry = packages.current().platforms["linux-x86_64"][0]
    sha = str(entry["sha256"])
    packages.wheels.mkdir(parents=True, exist_ok=True)
    (packages.wheels / f"{sha}.whl").write_bytes(b"0123456789")

    url = f"{API}/python-packages/files/{sha}"
    full = remote.get(url, headers=auth(token))
    assert full.status_code == 200
    assert full.content == b"0123456789"
    part = remote.get(url, headers={**auth(token), "Range": "bytes=4-"})
    assert part.status_code == 206
    assert part.content == b"456789"

    assert (
        remote.get(f"{API}/python-packages/files/{'0' * 64}", headers=auth(token)).status_code
        == 404
    )
    assert remote.get(url).status_code == 401

    # 同時下載的 worker 數到上限：請它稍後再來
    packages.save_settings({"workerDownloads": 1})
    assert packages.begin_download("someone-else")
    busy = remote.get(url, headers=auth(token))
    assert busy.status_code == 503
    assert busy.headers["Retry-After"] == "5"
    assert body(busy)["error"] == {
        "code": "packages_busy",
        "message": "同時下載套件的裝置太多，請稍後再試",
    }
    packages.end_download("someone-else")
    assert remote.get(url, headers=auth(token)).status_code == 200
    assert packages.begin_download("someone-else")  # 下載完就讓出位置
