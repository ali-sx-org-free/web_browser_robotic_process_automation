"""M7.3 批次執行的 API（不需要瀏覽器）：表格與欄位對應、每一列的檢查、依「同時幾列」排入、
一列沒通過時照跑或停下、手動停下、只重跑沒有通過的列（可以先改儲存格）、匯出，以及頁面；
Agent API 的批次（一列一組入參、建立後直接開始、冪等鍵、排隊上限、只看得到自己的批次）。
Agent 的請求打到對外埠（base_url 帶 :8081）並帶 API 金鑰（同 test_agent_api.py）。

每一列的執行換成假的執行器：標題（title）以「失敗」開頭的列失敗，其餘通過、出參取同名的入參。
表格的讀入與換算本身在 test_batch_table.py。
"""

import base64
import threading
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass, replace
from pathlib import Path
from typing import cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx2 import Client, Response
from sqlalchemy import select

from rpa_core.dsl import validate_file
from rpa_runner.contract import check_inputs
from rpa_runner.login import LoginSettings
from rpa_runner.run import RunResult, StageName
from rpa_server.batch_table import read_table
from rpa_server.config import Settings
from rpa_server.domain import now
from rpa_server.models import Revision, Scene
from rpa_server.services import Services
from rpa_worker import Worker

JsonObject = dict[str, object]
WORKER_PORT = 8081
AGENT = "/agent-api/v1"
SCOPES = ["scenes:read", "runs:execute", "runs:read"]


class FakeExecutor:
    """假的執行器：記下每次執行的入參；標題以「失敗」開頭的以 failed 結束。"""

    def __init__(self) -> None:
        self.titles: list[object] = []

    def __call__(
        self,
        path: Path,
        inputs: Mapping[str, object],
        *,
        out_root: Path,
        base_url: str | None = None,
        engine: str | None = None,
        headed: bool = False,
        deadline_ms: int | None = None,
        run_id: str | None = None,
        cancel: threading.Event | None = None,
        on_stage: Callable[[StageName], None] | None = None,
        login: LoginSettings | None = None,
        secrets: Mapping[str, str] | None = None,
        record_video: bool = False,
        **_files: object,
    ) -> RunResult:
        scenario = validate_file(path).scenario
        assert scenario is not None
        assert run_id is not None
        resolved, problems = check_inputs(scenario, inputs)
        assert problems == []
        title = resolved.get("title")
        self.titles.append(title)
        failed = isinstance(title, str) and title.startswith("失敗")
        output: dict[str, object] | None = None
        if not failed:
            output = {
                "recordId": "DEMO-" + str(len(self.titles)),
                "title": title,
                "quantity": resolved.get("quantity"),
            }
        directory = out_root / run_id
        directory.mkdir(parents=True, exist_ok=True)
        return RunResult(
            run_id=run_id,
            scenario_id=scenario.id,
            scenario_name=scenario.name,
            scenario_hash="0" * 64,
            kind="dsl",
            engine=engine or scenario.browser.engine,
            directory=directory,
            started_at=now().isoformat(),
            status="failed" if failed else "passed",
            input=resolved,
            output=output,
            error="假的失敗" if failed else None,
        )


@pytest.fixture
def settings(settings: Settings) -> Settings:
    """Agent API 在對外埠；管理頁面與 /api 不受影響。"""
    return replace(settings, worker_port=WORKER_PORT, worker_host="192.168.1.10")


@pytest.fixture
def remote(app: FastAPI, client: Client) -> Iterator[Client]:
    """打到對外埠的用戶端（伺服器已經由 client 啟動）。"""
    with TestClient(app, base_url=f"http://testserver:{WORKER_PORT}") as other:
        yield other


@pytest.fixture
def executor() -> FakeExecutor:
    return FakeExecutor()


@pytest.fixture
def worker(app: FastAPI, executor: FakeExecutor) -> Worker:
    """同一個任務來源（資料庫的佇列），換成假的執行器；測試自己呼叫 run_once。"""
    return Worker(cast("Worker", app.state.worker).source, executor=executor)


def services(app: FastAPI) -> Services:
    return cast("Services", app.state.services)


def body(response: Response, status: int | None = None) -> JsonObject:
    if status is not None:
        assert response.status_code == status, response.text
    data: object = response.json()
    assert isinstance(data, dict)
    return cast("JsonObject", data)


def error(response: Response, status: int) -> JsonObject:
    data = body(response, status)["error"]
    assert isinstance(data, dict)
    return cast("JsonObject", data)


def publish(app: FastAPI, scene_id: str, number: int = 1) -> None:
    """直接在資料庫標成已發布（發布門檻本身在 test_api.py 測過）。"""
    with services(app).sessions() as session:
        scene = session.get(Scene, scene_id)
        revision = session.scalars(
            select(Revision).where(Revision.scene_id == scene_id, Revision.number == number)
        ).one()
        assert scene is not None
        revision.status = "passed"
        revision.published_at = now()
        scene.published_number = number
        session.commit()


@pytest.fixture
def scene(app: FastAPI, client: Client) -> str:
    """匯入範例並發布 BA-001（入參 title、quantity，quantity 是 1～30 的整數，都有預設值）。"""
    body(client.post("/api/scenes/import"))
    publish(app, "ba-001")
    return "ba-001"


def rows(batch: JsonObject) -> list[JsonObject]:
    return cast("list[JsonObject]", batch["rows"])


def statuses(batch: JsonObject) -> list[str]:
    return [str(row["status"]) for row in rows(batch)]


def create(client: Client, text: str, **options: object) -> JsonObject:
    return body(client.post("/api/scenes/ba-001/batches", json={"text": text, **options}), 201)


def get(client: Client, batch: JsonObject) -> JsonObject:
    return body(client.get(f"/api/batches/{batch['id']}"))


def drain(worker: Worker) -> int:
    """把佇列跑完（每一列結束後批次會排下一列），回傳跑了幾次。"""
    count = 0
    while worker.run_once():
        count += 1
        assert count < 50
    return count


# ---------------------------------------------------------------- 建立與設定


def test_table_mapping_and_row_checks_before_start(scene: str, client: Client) -> None:
    batch = create(client, "名稱\tquantity\t備註\n甲\t3\tx\n乙\t99\t\n丙\t\t\n")
    assert batch["status"] == "draft"
    assert batch["revision"] == 1
    assert batch["columns"] == ["名稱", "quantity", "備註"]
    # 依標題自動對應：quantity 有同名的欄位；title 沒有，用預設值
    assert batch["mapping"] == {"title": None, "quantity": "quantity"}
    assert statuses(batch) == ["pending", "invalid", "pending"]
    assert [row["inputs"] for row in rows(batch)] == [{"quantity": 3}, {"quantity": 99}, {}]
    problems = cast("list[JsonObject]", rows(batch)[1]["problems"])
    assert [(item["input"], item["column"]) for item in problems] == [("quantity", "quantity")]
    assert batch["counts"] == {"total": 3, "pending": 2, "invalid": 1}

    url = f"/api/batches/{batch['id']}"
    mapped = body(client.patch(url, json={"mapping": {"title": "名稱"}, "concurrency": 3}))
    assert mapped["mapping"] == {"title": "名稱", "quantity": "quantity"}
    assert mapped["concurrency"] == 3
    assert [row["inputs"] for row in rows(mapped)] == [
        {"title": "甲", "quantity": 3},
        {"title": "乙", "quantity": 99},
        {"title": "丙"},
    ]
    unknown = client.patch(url, json={"mapping": {"title": "沒有這欄"}})
    assert error(unknown, 422)["code"] == "batch_column_unknown"
    assert error(client.patch(url, json={"mapping": {"nope": None}}), 422)["code"] == (
        "batch_input_unknown"
    )
    bad_url = client.patch(url, json={"baseUrl": "ftp://example.com"})
    assert error(bad_url, 422)["code"] == "base_url_invalid"

    # 頁面
    assert client.get("/scenes/ba-001/batch").status_code == 200
    page = client.get(f"/batches/{batch['id']}")
    assert page.status_code == 200
    assert 'data-mapping="title"' in page.text
    assert 'data-signature="draft:invalid=1,pending=2,total=3"' in page.text
    listed = client.get("/batches")
    assert listed.status_code == 200
    assert str(batch["id"]) in listed.text
    found = cast("list[JsonObject]", body(client.get("/api/batches?scene=ba-001"))["batches"])
    assert [item["id"] for item in found] == [batch["id"]]
    assert "rows" not in found[0]

    # 還沒開始的批次可以刪除
    assert client.delete(url).status_code == 204
    assert error(client.get(url), 404)["code"] == "batch_not_found"


def test_table_problems_and_unpublished_scenes(scene: str, client: Client) -> None:
    missing = client.post("/api/scenes/ba-001/batches", json={"text": "  "})
    assert error(missing, 422)["code"] == "batch_table"
    garbled = client.post(
        "/api/scenes/ba-001/batches", json={"fileName": "a.csv", "fileContent": "@@@"}
    )
    assert error(garbled, 422)["code"] == "batch_table"
    unpublished = client.post("/api/scenes/ba-002/batches", json={"text": "title\n甲\n"})
    assert error(unpublished, 409)["code"] == "not_published"
    assert client.get("/scenes/ba-002/batch").status_code == 409
    # 上傳的檔案：UTF-8（帶 BOM）的 CSV
    data = "﻿title,quantity\r\n甲,2\r\n".encode()
    uploaded = body(
        client.post(
            "/api/scenes/ba-001/batches",
            json={"fileName": "清單.csv", "fileContent": base64.b64encode(data).decode()},
        ),
        201,
    )
    assert uploaded["source"] == "清單.csv"
    assert [row["inputs"] for row in rows(uploaded)] == [{"title": "甲", "quantity": 2}]
    # 同一個冪等鍵：同一個批次
    first = create(client, "title\n乙\n", idempotencyKey="k-1")
    assert create(client, "title\n丙\n", idempotencyKey="k-1")["id"] == first["id"]
    # 沒有一列可以執行
    invalid_only = create(client, "quantity\n99\n")
    started = client.post(f"/api/batches/{invalid_only['id']}/start")
    assert error(started, 422)["code"] == "batch_no_valid_rows"


# ---------------------------------------------------------------- 執行


def test_rows_run_with_concurrency_and_failed_rows_rerun_after_editing(
    scene: str, client: Client, worker: Worker, executor: FakeExecutor
) -> None:
    batch = create(
        client,
        "title\tquantity\n甲\t3\n失敗一\t4\n乙\t1,0\n丙\t5\n",
        concurrency=2,
        start=True,
    )
    assert batch["status"] == "running"
    # 第 3 列的 1,0 不是數字：資料有問題，不執行；同時排入兩列
    assert statuses(batch) == ["queued", "queued", "invalid", "pending"]
    assert error(client.delete(f"/api/batches/{batch['id']}"), 409)["code"] == "batch_not_draft"

    assert worker.run_once() is True  # 第 1 列；結束後補上第 4 列
    assert statuses(get(client, batch)) == ["passed", "queued", "invalid", "queued"]
    assert drain(worker) == 2
    done = get(client, batch)
    assert done["status"] == "finished"
    assert done["finishedAt"] is not None
    assert statuses(done) == ["passed", "failed", "invalid", "passed"]
    assert executor.titles == ["甲", "失敗一", "丙"]
    first = rows(done)[0]
    assert first["output"] == {"recordId": "DEMO-1", "title": "甲", "quantity": 3}
    assert first["attempts"] == 1
    run = body(client.get(f"/api/runs/{first['runId']}"))
    assert (run["batchId"], run["batchRow"], run["purpose"]) == (done["id"], 1, "execution")
    assert error(client.post(f"/api/batches/{batch['id']}/start"), 409)["code"] == (
        "batch_not_draft"
    )
    page = client.get(f"/batches/{batch['id']}")
    assert 'data-cell data-row="2"' in page.text  # 沒有通過的列可以改
    assert 'data-cell data-row="1"' not in page.text

    # 匯出：CSV（UTF-8 帶 BOM）與 Excel；Excel 用同一個模組讀回來
    csv = client.get(f"/api/batches/{batch['id']}/export?format=csv")
    assert csv.status_code == 200
    assert csv.headers["content-type"].startswith("text/csv")
    assert f'filename="{batch["id"]}.csv"' in csv.headers["content-disposition"]
    assert csv.content.startswith(b"\xef\xbb\xbf")
    assert len(csv.content.decode("utf-8-sig").strip().splitlines()) == 5
    xlsx = client.get(f"/api/batches/{batch['id']}/export?format=xlsx")
    assert xlsx.status_code == 200
    table = read_table("result.xlsx", xlsx.content)
    assert table.columns[1:3] == ("title", "quantity")
    assert [row[1] for row in table.rows] == ["甲", "失敗一", "乙", "丙"]
    assert str(first["runId"]) in [cell for row in table.rows for cell in row]

    # 重跑沒有通過的列：第 2 列改標題、第 3 列改成數字
    cells = {"2": {"title": "改好了"}, "3": {"quantity": "10"}}
    rerun = body(client.post(f"/api/batches/{batch['id']}/rerun", json={"cells": cells}), 202)
    assert rerun["status"] == "running"
    assert statuses(rerun) == ["passed", "queued", "queued", "passed"]
    assert drain(worker) == 2
    again = get(client, batch)
    assert again["status"] == "finished"
    assert statuses(again) == ["passed", "passed", "passed", "passed"]
    second = rows(again)[1]
    assert second["cells"] == {"title": "改好了", "quantity": "4"}
    assert second["attempts"] == 2
    assert [item["status"] for item in cast("list[JsonObject]", second["runs"])] == [
        "passed",
        "failed",
    ]
    assert rows(again)[0]["attempts"] == 1  # 通過的列不重跑
    assert executor.titles == ["甲", "失敗一", "丙", "改好了", "乙"]
    nothing = client.post(f"/api/batches/{batch['id']}/rerun", json={})
    assert error(nothing, 422)["code"] == "batch_nothing_to_rerun"
    unknown = client.post(f"/api/batches/{batch['id']}/rerun", json={"cells": {"9": {}}})
    assert error(unknown, 422)["code"] == "batch_row_unknown"


def test_stop_on_failure_and_rerun_only_the_chosen_rows(
    scene: str, client: Client, worker: Worker, executor: FakeExecutor
) -> None:
    batch = create(client, "title\n失敗\n甲\n乙\n", onFailure="stop", start=True)
    assert statuses(batch) == ["queued", "pending", "pending"]
    assert drain(worker) == 1
    stopped = get(client, batch)
    assert stopped["status"] == "stopped"
    assert str(stopped["error"]).startswith("第 1 列沒有通過")
    assert statuses(stopped) == ["failed", "skipped", "skipped"]

    # 只重跑第 2 列：第 3 列（沒有執行過）不會跟著跑；上一輪的失敗不算這一輪
    chosen = body(client.post(f"/api/batches/{batch['id']}/rerun", json={"rows": [2]}), 202)
    assert statuses(chosen) == ["failed", "queued", "skipped"]
    assert drain(worker) == 1
    finished = get(client, batch)
    assert finished["status"] == "finished"
    assert finished["error"] is None
    assert statuses(finished) == ["failed", "passed", "skipped"]

    # 沒指定：沒有通過與沒有執行的列（第 1、3 列）；第 1 列又失敗，第 3 列不排
    body(client.post(f"/api/batches/{batch['id']}/rerun"), 202)
    assert drain(worker) == 1
    final = get(client, batch)
    assert final["status"] == "stopped"
    assert statuses(final) == ["failed", "passed", "skipped"]
    assert executor.titles == ["失敗", "甲", "失敗"]


def test_stop_cancels_queued_rows(scene: str, client: Client, worker: Worker) -> None:
    batch = create(client, "title\n甲\n乙\n丙\n", concurrency=2, start=True)
    stopped = body(client.post(f"/api/batches/{batch['id']}/stop"), 202)
    assert stopped["status"] == "stopped"
    assert stopped["error"] == "手動停下"
    assert statuses(stopped) == ["cancelled", "cancelled", "skipped"]
    assert worker.run_once() is False
    again = client.post(f"/api/batches/{batch['id']}/stop")
    assert error(again, 409)["code"] == "batch_not_running"
    page = client.get(f"/batches/{batch['id']}")
    assert "data-poll" not in page.text
    rerun = body(client.post(f"/api/batches/{batch['id']}/rerun"), 202)
    assert statuses(rerun) == ["queued", "queued", "pending"]
    assert "data-poll" in client.get(f"/batches/{batch['id']}").text
    assert drain(worker) == 3
    assert get(client, batch)["status"] == "finished"


def test_recover_continues_running_batches(
    app: FastAPI, scene: str, client: Client, worker: Worker
) -> None:
    """伺服器重啟：執行中的批次依各列的結果接著走（排隊中的執行留在佇列）。"""
    batch = create(client, "title\n甲\n乙\n", start=True)
    assert worker.run_once() is True
    services(app).batches.recover()  # 同一個通知來兩次也不會重複排入
    services(app).batches.row_finished(str(rows(get(client, batch))[0]["runId"]))
    assert statuses(get(client, batch)) == ["passed", "queued"]
    assert drain(worker) == 1
    assert get(client, batch)["status"] == "finished"


# ---------------------------------------------------------------- Agent API


@dataclass
class Agent:
    remote: Client
    key: str

    def get(self, path: str) -> Response:
        return self.remote.get(AGENT + path, headers={"Authorization": f"Bearer {self.key}"})

    def post(self, path: str, payload: JsonObject | None = None) -> Response:
        return self.remote.post(
            AGENT + path, json=payload or {}, headers={"Authorization": f"Bearer {self.key}"}
        )


def register(client: Client, remote: Client, agent_id: str, **policy: object) -> Agent:
    created = body(
        client.post("/api/agents", json={"id": agent_id, "policy": {"scopes": SCOPES, **policy}}),
        201,
    )
    return Agent(remote, str(created["key"]))


@pytest.mark.usefixtures("scene")
def test_agent_batches_run_rows_and_stay_private(
    client: Client, remote: Client, worker: Worker, executor: FakeExecutor
) -> None:
    agent = register(client, remote, "agent-erp", maxQueuedRuns=5)
    payload: JsonObject = {
        "sceneId": "ba-001",
        "rows": [{"title": "甲", "quantity": 2}, {"title": "失敗"}, {"title": "乙"}],
        "concurrency": 2,
        "idempotencyKey": "b-1",
    }
    batch = body(agent.post("/batches", payload), 202)
    assert batch["status"] == "running"
    assert batch["clientId"] == "agent-erp"
    assert batch["portalPath"] == f"/batches/{batch['id']}"
    assert batch["columns"] == ["title", "quantity"]
    assert [row["status"] for row in rows(batch)] == ["queued", "queued", "pending"]
    assert body(agent.post("/batches", payload), 202)["id"] == batch["id"]  # 冪等鍵

    while worker.run_once():
        pass
    done = body(agent.get(f"/batches/{batch['id']}"))
    assert done["status"] == "finished"
    assert [row["status"] for row in rows(done)] == ["passed", "failed", "passed"]
    assert rows(done)[0]["output"] == {"recordId": "DEMO-1", "title": "甲", "quantity": 2}
    run = body(agent.get(f"/runs/{rows(done)[0]['runId']}"))
    assert (run["clientId"], run["batchId"]) == ("agent-erp", batch["id"])

    # 只重跑沒有通過的列
    rerun = body(agent.post(f"/batches/{batch['id']}/rerun"), 202)
    assert [row["status"] for row in rows(rerun)] == ["passed", "queued", "passed"]
    while worker.run_once():
        pass
    assert executor.titles == ["甲", "失敗", "乙", "失敗"]

    # 別的用戶端看不到這個批次
    other = register(client, remote, "agent-bi")
    assert error(other.get(f"/batches/{batch['id']}"), 404)["code"] == "batch_not_found"
    assert error(other.post(f"/batches/{batch['id']}/stop"), 404)["code"] == "batch_not_found"


@pytest.mark.usefixtures("scene")
def test_agent_batches_check_rows_limits_and_scopes(client: Client, remote: Client) -> None:
    agent = register(client, remote, "agent-erp", maxQueuedRuns=2)
    invalid = error(
        agent.post("/batches", {"sceneId": "ba-001", "rows": [{"title": "甲"}, {"quantity": 99}]}),
        422,
    )
    assert invalid["code"] == "batch_rows_invalid"
    problems = cast("list[JsonObject]", invalid["problems"])
    assert [(item["row"], item["input"]) for item in problems] == [(2, "quantity")]
    unknown = error(agent.post("/batches", {"sceneId": "ba-001", "rows": [{"color": "紅"}]}), 422)
    assert cast("list[JsonObject]", unknown["problems"])[0]["input"] == "color"
    unpublished = agent.post("/batches", {"sceneId": "ba-002", "rows": [{"title": "甲"}]})
    assert error(unpublished, 409)["code"] == "not_published"

    # 同時排入的列也算在排隊上限裡
    many: JsonObject = {"sceneId": "ba-001", "rows": [{"title": str(n)} for n in range(5)]}
    limited = error(agent.post("/batches", {**many, "concurrency": 3}), 429)
    assert limited["code"] == "limit_reached"
    batch = body(agent.post("/batches", {**many, "concurrency": 2}), 202)
    stopped = body(agent.post(f"/batches/{batch['id']}/stop"), 202)
    assert stopped["status"] == "stopped"
    assert [row["status"] for row in rows(stopped)] == [
        "cancelled",
        "cancelled",
        "skipped",
        "skipped",
        "skipped",
    ]

    reader = register(client, remote, "agent-reader", scopes=["scenes:read", "runs:read"])
    refused = reader.post("/batches", {"sceneId": "ba-001", "rows": [{"title": "甲"}]})
    assert error(refused, 403)["code"] == "scope_missing"
