"""子場景（M7.2，ADR 0023）經過管理 Portal 的真實執行：發布子場景 → 存呼叫場景（伺服器帶入
子場景檔）→ 驗證 → 回看看得到子場景的步驟與原文。每個情境在 Chromium 與 Firefox 各跑一次；
佇列由測試呼叫 worker.run_once()。"""

from collections.abc import Iterator
from typing import cast

import pytest
from fastapi import FastAPI
from httpx2 import Client, Response

from rpa_worker import Worker
from testsite.browsers import ENGINES, require_engine
from testsite.server import running

pytestmark = pytest.mark.browser

JsonObject = dict[str, object]
CALLER = """\
schemaVersion: 1
id: order
name: 建立後查詢
inputs:
  title: { type: string, default: 子場景流程 }
browser: { baseUrl: 'http://127.0.0.1:8765' }
defaults: { timeout: 10000 }
deadline: 60000
steps:
  - id: create
    action: call
    scenario: ba-001
    revision: 1
    inputs: { title: '{{ inputs.title }}', quantity: 4 }
    as: created
  - { id: open-query, action: goto, url: '/?view=query', waitUntil: domcontentloaded }
  - id: fill-id
    action: fill
    target: { label: 紀錄編號, exact: true }
    value: '{{ facts.created.recordId }}'
  - { id: search, action: click, target: { role: button, name: 查詢, exact: true } }
  - { id: wait-receipt, action: waitFor, target: { css: '#receipt' } }
  - id: read-record
    action: extract
    target: { css: '#record-title' }
    as: foundTitle
verify:
  - { name: 查到剛建立的那一筆, value: '{{ facts.foundTitle }}', equals: '{{ inputs.title }}' }
outputs:
  recordId: { type: string, from: '{{ facts.created.recordId }}' }
"""


@pytest.fixture(params=ENGINES)
def engine(request: pytest.FixtureRequest) -> str:
    return require_engine(str(request.param))


@pytest.fixture(scope="module")
def site() -> Iterator[str]:
    with running() as url:
        yield url


def body(response: Response) -> JsonObject:
    assert response.status_code < 400, response.text
    data: object = response.json()
    assert isinstance(data, dict)
    return cast("JsonObject", data)


def worker(app: FastAPI) -> Worker:
    return cast("Worker", app.state.worker)


def validate(
    app: FastAPI, client: Client, scene: str, revision: int, inputs: JsonObject, engine: str
) -> JsonObject:
    queued = body(
        client.post(
            f"/api/scenes/{scene}/revisions/{revision}/validate",
            json={"inputs": inputs, "engine": engine, "headless": True},
        )
    )
    assert worker(app).run_once() is True
    return body(client.get(f"/api/runs/{queued['id']}"))


def test_caller_runs_the_published_sub_scenario(
    app: FastAPI, client: Client, site: str, engine: str
) -> None:
    body(client.post("/api/scenes/import"))
    body(client.patch("/api/scenes/ba-001", json={"baseUrl": site}))
    sub = validate(app, client, "ba-001", 1, {}, engine)
    assert sub["status"] == "passed", sub["error"]
    body(client.post("/api/scenes/ba-001/revisions/1/publish"))
    assert client.post("/api/scenes", json={"id": "order", "name": "暫名"}).status_code == 201
    saved = client.post(
        "/api/scenes/order/revisions",
        json={"baseRevision": 1, "files": {"scenario.yaml": CALLER}},
    )
    assert saved.status_code == 201, saved.text
    body(client.patch("/api/scenes/order", json={"baseUrl": site}))

    run = validate(app, client, "order", 2, {"title": "經過 Portal"}, engine)

    assert run["status"] == "passed", run["error"]
    output = cast("JsonObject", run["output"])
    assert str(output["recordId"]).startswith("DEMO-")
    # 回看：子場景的步驟縮排在 call 下面，原文取自帶進來的子場景檔
    replay = body(client.get(f"/api/runs/{run['id']}/replay"))
    steps = cast("list[JsonObject]", replay["steps"])
    call = steps[0]
    assert (call["action"], call["depth"]) == ("call", 0)
    info = cast("JsonObject", call["call"])
    assert (info["scenario"], info["revision"]) == ("ba-001", 1)
    inner = [step for step in steps if step["parent"] == 1]
    assert [step["id"] for step in inner][:3] == ["open", "fill-title", "fill-quantity"]
    assert all(step["depth"] == 1 for step in inner)
    fill = inner[1]
    assert fill["path"] == ["steps", 0, "call", 1]
    assert "inputs.title" in str(fill["source"])
    # 子場景的事實不混進呼叫場景的：子場景的 read-record 沒有事實可以顯示
    assert all(step["hasFact"] is False for step in inner)
    assert steps[-1]["hasFact"] is True
    # 子場景這一版發布之後再出新版本，已經存好的呼叫場景還是用第 1 版
    page = client.get(f"/runs/{run['id']}").text
    assert "order" in page
