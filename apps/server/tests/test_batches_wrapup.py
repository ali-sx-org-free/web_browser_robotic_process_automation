"""M7 收尾的批次執行：組合場景的批次、Excel 選工作表、所有批次共用的上限（不需要瀏覽器）。

執行換成假的執行器：一律通過，出參取同名的入參（沒有的用固定值），回報磁碟上場景版本的
真實雜湊（組合場景的驗證紀錄要能證明節點跑的是釘住的版本，才能發布）。標題以「失敗」開頭的
執行失敗。批次本身的流程在 test_batches_api.py，表格的讀入在 test_batch_table.py。
"""

import base64
import io
import threading
import zipfile
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import cast
from xml.sax.saxutils import escape

import pytest
from fastapi import FastAPI
from httpx2 import Client, Response
from sqlalchemy import select

from rpa_core.dsl import validate_file
from rpa_core.dsl.sources import scenario_digest
from rpa_runner.contract import check_inputs
from rpa_runner.login import LoginSettings
from rpa_runner.run import RunResult, StageName
from rpa_server.batch_table import read_table
from rpa_server.domain import now
from rpa_server.models import Revision, Scene
from rpa_server.services import Services
from rpa_worker import Worker

JsonObject = dict[str, object]
MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
RELATIONSHIPS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

CHAIN: JsonObject = {
    "version": 2,
    "mode": "dag",
    "nodes": [
        {"id": "n1", "sceneId": "ba-001", "revision": 1, "inputs": {"title": {"value": "組合"}}},
        {"id": "n2", "sceneId": "ba-002", "revision": 1, "inputs": {"recordId": {"auto": True}}},
    ],
    "edges": [{"source": "n1", "target": "n2"}],
}


class Executor:
    """假的執行器：記下每次執行的場景與標題；標題以「失敗」開頭的失敗。"""

    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

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
        self.calls.append((scenario.id, title))
        failed = isinstance(title, str) and title.startswith("失敗")
        fixed = "DEMO-" + scenario.id.upper().replace("-", "")
        directory = out_root / run_id
        directory.mkdir(parents=True, exist_ok=True)
        return RunResult(
            run_id=run_id,
            scenario_id=scenario.id,
            scenario_name=scenario.name,
            scenario_hash=scenario_digest(path, scenario),
            kind="dsl",
            engine=engine or scenario.browser.engine,
            directory=directory,
            started_at=now().isoformat(),
            status="failed" if failed else "passed",
            input=resolved,
            output=None
            if failed
            else {
                name: resolved.get(name, fixed if spec.type == "string" else 1)
                for name, spec in scenario.outputs.items()
            },
            error="假的失敗" if failed else None,
        )


@pytest.fixture
def executor() -> Executor:
    return Executor()


@pytest.fixture
def worker(app: FastAPI, executor: Executor) -> Worker:
    return Worker(cast("Worker", app.state.worker).source, executor=executor)


def services(app: FastAPI) -> Services:
    return cast("Services", app.state.services)


def body(response: Response, status: int | None = None) -> JsonObject:
    if status is not None:
        assert response.status_code == status, response.text
    data: object = response.json()
    assert isinstance(data, dict), response.text
    return cast("JsonObject", data)


def error(response: Response, status: int) -> JsonObject:
    data = body(response, status)["error"]
    assert isinstance(data, dict)
    return cast("JsonObject", data)


def publish(app: FastAPI, scene_id: str) -> None:
    """直接在資料庫把場景的第 1 版標成已發布（發布門檻在別的測試）。"""
    with services(app).sessions() as session:
        scene = session.get(Scene, scene_id)
        revision = session.scalars(
            select(Revision).where(Revision.scene_id == scene_id, Revision.number == 1)
        ).one()
        assert scene is not None
        revision.status = "passed"
        revision.published_at = now()
        scene.published_number = 1
        session.commit()


@pytest.fixture
def examples(app: FastAPI, client: Client) -> None:
    body(client.post("/api/scenes/import"))
    publish(app, "ba-001")
    publish(app, "ba-002")


def drain(worker: Worker) -> int:
    count = 0
    while worker.run_once():
        count += 1
        assert count < 80
    return count


def rows(batch: JsonObject) -> list[JsonObject]:
    return cast("list[JsonObject]", batch["rows"])


def statuses(batch: JsonObject) -> list[str]:
    return [str(row["status"]) for row in rows(batch)]


@pytest.fixture
def composite(examples: None, client: Client, worker: Worker) -> int:
    """「BA-001 → BA-002」的組合場景：驗證一次、發布第 1 版。"""
    created = body(
        client.post("/api/workflows", json={"name": "建立後查詢", "definition": CHAIN}), 201
    )
    workflow_id = int(cast("int", created["id"]))
    started = body(client.post(f"/api/workflows/{workflow_id}/runs", json={"headless": True}), 202)
    drain(worker)
    assert body(client.get(f"/api/workflow-runs/{started['id']}"))["status"] == "passed"
    body(client.post(f"/api/workflows/{workflow_id}/revisions/1/publish"))
    return workflow_id


# ---------------------------------------------------------------- 組合場景的批次


def test_composite_batch_runs_each_row_as_a_composite_run(
    composite: int, client: Client, worker: Worker, executor: Executor
) -> None:
    # 入參：沒有接上游出參的 n1.title（固定值「組合」）與 n1.quantity；n2.recordId 接 n1 的出參
    page = client.get(f"/playground/{composite}/batch")
    assert page.status_code == 200
    assert "n1.title" in page.text
    assert "n2.recordId" not in page.text.split('id="outputs"')[0]  # 接上游出參的不列
    assert f'data-workflow="{composite}"' in page.text

    text = "title\tn1.quantity\n甲\t3\n乙\t99\n\t5\n失敗了\t2\n"
    created = client.post(f"/api/workflows/{composite}/batches", json={"text": text})
    batch = body(created, 201)
    assert (batch["sceneId"], batch["workflowId"], batch["revision"]) == (None, composite, 1)
    assert batch["sceneName"] == "建立後查詢"
    # 只有一個節點有 title：標題 title 對到 n1.title
    assert batch["mapping"] == {"n1.title": "title", "n1.quantity": "n1.quantity"}
    assert statuses(batch) == ["pending", "invalid", "pending", "pending"]
    url = f"/api/batches/{batch['id']}"
    refused = client.patch(url, json={"baseUrl": "https://example.com"})
    assert error(refused, 422)["code"] == "batch_composite_base_url"

    started = body(client.post(f"{url}/start"), 202)
    assert statuses(started) == ["running", "invalid", "pending", "pending"]
    drain(worker)
    done = body(client.get(url))
    assert done["status"] == "finished"
    assert statuses(done) == ["passed", "invalid", "passed", "failed"]
    # 每一列各一次組合運行：n1 用表格的值（空白用固定值），n2 接 n1 的出參
    assert [call for call in executor.calls if call[0] == "ba-001"][-3:] == [
        ("ba-001", "甲"),
        ("ba-001", "組合"),
        ("ba-001", "失敗了"),
    ]
    first, third, fourth = rows(done)[0], rows(done)[2], rows(done)[3]
    output = cast("JsonObject", first["output"])
    assert (output["n1.title"], output["n1.quantity"]) == ("甲", 3)
    assert output["n2.recordId"] == "DEMO-BA001"  # n2 接 n1 的出參
    assert cast("JsonObject", third["output"])["n1.title"] == "組合"
    assert fourth["output"] is None
    run = body(client.get(f"/api/workflow-runs/{first['runId']}"))
    assert (run["purpose"], run["workflowVersion"], run["status"]) == ("execution", 1, "passed")

    # 頁面、清單、匯出
    detail = client.get(f"/batches/{batch['id']}")
    assert detail.status_code == 200
    assert f"/playground/runs/{first['runId']}" in detail.text
    listed = cast(
        "list[JsonObject]", body(client.get(f"/api/batches?workflow={composite}"))["batches"]
    )
    assert [item["id"] for item in listed] == [batch["id"]]
    assert cast("JsonObject", listed[0]["counts"])["passed"] == 2
    assert client.get("/batches").status_code == 200
    exported = client.get(f"{url}/export?format=xlsx")
    table = read_table("result.xlsx", exported.content)
    assert "出參：n2.recordId" in table.columns

    # 重跑沒有通過的列（改好標題）：同一個批次再一次組合運行
    rerun = client.post(f"{url}/rerun", json={"cells": {"4": {"title": "改好了"}}})
    assert body(rerun, 202)["status"] == "running"
    drain(worker)
    again = body(client.get(url))
    assert statuses(again) == ["passed", "invalid", "passed", "passed"]
    assert len(cast("list[object]", rows(again)[3]["runs"])) == 2


def test_composite_batch_stop_cancels_the_composite_runs(
    composite: int, client: Client, worker: Worker
) -> None:
    batch = body(
        client.post(
            f"/api/workflows/{composite}/batches",
            json={"text": "title\n甲\n乙\n", "start": True, "concurrency": 2},
        ),
        201,
    )
    assert statuses(batch) == ["running", "running"]
    stopped = body(client.post(f"/api/batches/{batch['id']}/stop"), 202)
    assert stopped["status"] == "stopped"
    assert statuses(stopped) == ["cancelled", "cancelled"]
    assert drain(worker) == 0


def test_unpublished_composite_cannot_have_a_batch(examples: None, client: Client) -> None:
    created = body(client.post("/api/workflows", json={"name": "沒發布", "definition": CHAIN}), 201)
    refused = client.post(f"/api/workflows/{created['id']}/batches", json={"text": "title\n甲\n"})
    assert error(refused, 409)["code"] == "workflow_unpublished"
    assert client.get(f"/playground/{created['id']}/batch").status_code == 409


# ---------------------------------------------------------------- Excel 選工作表


def two_sheets() -> bytes:
    def sheet(table: list[list[str]]) -> str:
        lines = "".join(
            f'<row r="{number}">'
            + "".join(
                f'<c r="{chr(ord("A") + index)}{number}" t="inlineStr"><is><t>{escape(text)}</t>'
                "</is></c>"
                for index, text in enumerate(row)
            )
            + "</row>"
            for number, row in enumerate(table, start=1)
        )
        return f'<worksheet xmlns="{MAIN}"><sheetData>{lines}</sheetData></worksheet>'

    files = {
        "xl/workbook.xml": (
            f'<workbook xmlns="{MAIN}" xmlns:r="{RELATIONSHIPS}"><sheets>'
            '<sheet name="說明" sheetId="1" r:id="rId1"/>'
            '<sheet name="訂單" sheetId="2" r:id="rId2"/></sheets></workbook>'
        ),
        "xl/_rels/workbook.xml.rels": (
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="worksheet" Target="worksheets/sheet1.xml"/>'
            '<Relationship Id="rId2" Type="worksheet" Target="worksheets/sheet2.xml"/>'
            "</Relationships>"
        ),
        "xl/worksheets/sheet1.xml": sheet([["說明"], ["第二個工作表才是資料"]]),
        "xl/worksheets/sheet2.xml": sheet([["title", "quantity"], ["甲", "2"], ["乙", "3"]]),
    }
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as book:
        for name, text in files.items():
            book.writestr(name, text)
    return buffer.getvalue()


def test_excel_worksheet_choice(examples: None, client: Client) -> None:
    content = base64.b64encode(two_sheets()).decode()
    sheets = body(
        client.post("/api/batch-sheets", json={"fileName": "訂單.xlsx", "fileContent": content})
    )
    assert sheets == {"sheets": ["說明", "訂單"]}
    csv = base64.b64encode("title\n甲\n".encode()).decode()
    plain = client.post("/api/batch-sheets", json={"fileName": "a.csv", "fileContent": csv})
    assert body(plain) == {"sheets": []}
    upload = {"fileName": "訂單.xlsx", "fileContent": content, "sheet": "訂單"}
    batch = body(client.post("/api/scenes/ba-001/batches", json=upload), 201)
    assert batch["columns"] == ["title", "quantity"]
    assert batch["source"] == "訂單.xlsx › 訂單"
    assert [row["inputs"] for row in rows(batch)] == [
        {"title": "甲", "quantity": 2},
        {"title": "乙", "quantity": 3},
    ]
    unknown = client.post("/api/scenes/ba-001/batches", json={**upload, "sheet": "彙總"})
    assert "彙總" in str(error(unknown, 422)["message"])
    page = client.get("/scenes/ba-001/batch")
    assert 'id="sheet-field"' in page.text


# ---------------------------------------------------------------- 共用的上限


def test_shared_limit_spans_all_batches(
    examples: None, client: Client, worker: Worker, executor: Executor
) -> None:
    assert body(client.get("/api/settings/batches")) == {"limit": 10, "active": 0}
    assert client.put("/api/settings/batches", json={"sharedLimit": 0}).status_code == 422
    assert body(client.put("/api/settings/batches", json={"sharedLimit": 1})) == {
        "limit": 1,
        "active": 0,
    }
    first = body(
        client.post(
            "/api/scenes/ba-001/batches",
            json={"text": "title\nA1\nA2\n", "concurrency": 2, "start": True},
        ),
        201,
    )
    second = body(
        client.post(
            "/api/scenes/ba-001/batches",
            json={"text": "title\nB1\nB2\n", "concurrency": 2, "start": True},
        ),
        201,
    )
    # 合計只能排入 1 列：先開始的批次先排
    assert statuses(first) == ["queued", "pending"]
    assert statuses(second) == ["pending", "pending"]
    assert body(client.get("/api/settings/batches")) == {"limit": 1, "active": 1}
    page = client.get("/batches")
    assert 'name="sharedLimit"' in page.text
    assert drain(worker) == 4
    assert [title for _, title in executor.calls] == ["A1", "A2", "B1", "B2"]
    for batch in (first, second):
        assert body(client.get(f"/api/batches/{batch['id']}"))["status"] == "finished"

    # 調高時馬上補等著的批次
    body(client.put("/api/settings/batches", json={"sharedLimit": 1}))
    third = body(
        client.post(
            "/api/scenes/ba-001/batches",
            json={"text": "title\nC1\nC2\n", "concurrency": 2, "start": True},
        ),
        201,
    )
    assert statuses(third) == ["queued", "pending"]
    body(client.put("/api/settings/batches", json={"sharedLimit": 5}))
    assert statuses(body(client.get(f"/api/batches/{third['id']}"))) == ["queued", "queued"]
