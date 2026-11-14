"""子場景（M7.2，ADR 0023）在伺服器端：存檔時帶入發布過的子場景版本、派工前比對擴充、編輯頁、
逐步調試的步驟樹、回看依路徑對應子場景的步驟。不開瀏覽器；真實的執行在 rpa_runner 的
test_call_browser.py 與 test_calls_flow.py。"""

import json
from pathlib import Path
from typing import cast

from fastapi import FastAPI
from httpx2 import Client, Response
from sqlalchemy import select

from rpa_core.dsl import validate_text
from rpa_runner.files import SCENARIO_DIR
from rpa_server import debugging, replay
from rpa_server.domain import now
from rpa_server.models import Revision, Scene
from rpa_server.replay import step_targets
from rpa_server.services import Services

JsonObject = dict[str, object]
SUB_FILE = "calls/ba-001/1.yaml"
CALLER = """\
schemaVersion: 1
id: order
name: 建立後查詢
browser: { baseUrl: 'http://127.0.0.1:8765' }
steps:
  - id: create
    action: call
    scenario: ba-001
    revision: 1
    inputs: { title: 子場景, quantity: 2 }
    as: created
  - { id: open-query, action: goto, url: '/?view=query' }
  - id: fill-id
    action: fill
    target: { label: 紀錄編號, exact: true }
    value: '{{ facts.created.recordId }}'
"""


def services(app: FastAPI) -> Services:
    return cast("Services", app.state.services)


def body(response: Response, status: int | None = None) -> JsonObject:
    if status is not None:
        assert response.status_code == status, response.text
    data: object = response.json()
    assert isinstance(data, dict), response.text
    return cast("JsonObject", data)


def issues(response: Response) -> list[JsonObject]:
    error = cast("JsonObject", body(response, 422)["error"])
    return cast("list[JsonObject]", error["issues"])


def publish(app: FastAPI, scene_id: str) -> None:
    """直接在資料庫把場景的第 1 版標成已發布（發布門檻在 test_packs.py 測過）。"""
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


def save(client: Client, text: str = CALLER, base: int = 1, **files: str) -> Response:
    return client.post(
        "/api/scenes/order/revisions",
        json={"baseRevision": base, "files": {"scenario.yaml": text, **files}},
    )


def prepared(app: FastAPI, client: Client, *, published: bool = True) -> None:
    """匯入範例（BA-001 是子場景），建立呼叫場景 order 的第 1 版（空白範本）。"""
    assert client.post("/api/scenes/import").status_code < 400
    if published:
        publish(app, "ba-001")
    assert client.post("/api/scenes", json={"id": "order", "name": "暫名"}).status_code == 201


def test_sub_scenario_must_be_a_published_revision(app: FastAPI, client: Client) -> None:
    prepared(app, client, published=False)

    refused = issues(save(client))

    assert [item["code"] for item in refused] == ["server.call_unusable"]
    assert "沒有發布過" in str(refused[0]["message"])
    missing = issues(save(client, CALLER.replace("revision: 1", "revision: 9")))
    assert "沒有第 9 版" in str(missing[0]["message"])
    unknown = issues(save(client, CALLER.replace("scenario: ba-001", "scenario: nowhere")))
    assert [item["code"] for item in unknown] == ["server.call_missing"]


def test_saving_brings_the_published_revision_in(app: FastAPI, client: Client) -> None:
    prepared(app, client)
    source = body(client.get("/api/scenes/ba-001/revisions/1"))
    sub_text = cast("JsonObject", source["files"])["scenario.yaml"]

    saved = body(save(client), 201)

    assert saved["number"] == 2
    files = cast("JsonObject", body(client.get("/api/scenes/order/revisions/2"))["files"])
    assert sorted(files) == [SUB_FILE, "scenario.yaml"]
    assert files[SUB_FILE] == sub_text
    # 內容雜湊包含子場景：場景檔一樣、子場景不同的版本，雜湊不同
    assert saved["contentHash"] != source["contentHash"]
    assert services(app).queue.features("order", 2) >= {"call"}
    assert services(app).revision_features("order", 2) >= {"call"}
    assert list(services(app).revision_calls("order", 2)) == [("ba-001", 1)]


def test_later_changes_to_the_sub_scenario_do_not_touch_the_caller(
    app: FastAPI, client: Client
) -> None:
    """子場景封存之後：已經存好的呼叫場景照樣能改別的地方再存（沿用上一版帶進來的那一份，
    送來的檔案裡沒有 calls/ 也一樣）；新的 call 才會被擋下。"""
    prepared(app, client)
    body(save(client), 201)
    body(client.patch("/api/scenes/ba-001", json={"archived": True}), 200)

    renamed = body(save(client, CALLER.replace("建立後查詢", "改名"), base=2), 201)

    assert renamed["number"] == 3
    files = cast("JsonObject", body(client.get("/api/scenes/order/revisions/3"))["files"])
    assert SUB_FILE in files
    assert client.post("/api/scenes", json={"id": "other", "name": "暫名"}).status_code == 201
    refused = client.post(
        "/api/scenes/other/revisions",
        json={
            "baseRevision": 1,
            "files": {"scenario.yaml": CALLER.replace("id: order", "id: other")},
        },
    )
    assert "已封存" in str(issues(refused)[0]["message"])


def test_removing_the_call_drops_the_copy(app: FastAPI, client: Client) -> None:
    prepared(app, client)
    body(save(client), 201)
    plain = CALLER.split("  - id: create")[0] + "  - { id: open, action: goto, url: / }\n"

    body(save(client, plain, base=2), 201)

    files = cast("JsonObject", body(client.get("/api/scenes/order/revisions/3"))["files"])
    assert sorted(files) == ["scenario.yaml"]


def test_edit_page_hides_sub_scenario_files_and_offers_the_snippet(
    app: FastAPI, client: Client
) -> None:
    prepared(app, client)
    body(save(client), 201)

    page = client.get("/scenes/order/edit").text

    assert SUB_FILE not in page
    assert "action: call" in page  # 場景檔本身與「插入」的範本


def test_debug_tree_treats_a_call_as_one_step_with_side_effects() -> None:
    scenario = validate_text(CALLER).scenario
    assert scenario is not None

    create, open_query, _ = debugging._steps(scenario)  # pyright: ignore[reportPrivateUsage]

    assert (create.action, create.target, create.side_effect) == ("call", "ba-001 v1", True)
    assert create.children == []
    assert open_query.side_effect is False
    assert json.loads(json.dumps(create.to_json()))["sideEffect"] is True


def test_replay_maps_records_into_the_sub_scenario(tmp_path: Path) -> None:
    sub = (Path(__file__).resolve().parents[3] / "scenarios" / "demo" / "ba-001.yaml").read_text(
        encoding="utf-8"
    )
    folder = tmp_path / "run"
    target = folder / SCENARIO_DIR / SUB_FILE
    target.parent.mkdir(parents=True)
    target.write_text(sub, encoding="utf-8")
    snapshot = folder / SCENARIO_DIR / "scenario.yaml"
    snapshot.write_text(CALLER, encoding="utf-8")

    definitions, sources = replay._definitions(snapshot)  # pyright: ignore[reportPrivateUsage]

    assert definitions[("steps", 0)]["scenario"] == "ba-001"
    fill = definitions[("steps", 0, "call", 1)]
    assert (fill["id"], fill["value"]) == ("fill-title", "{{ inputs.title }}")
    line, text = sources[("steps", 0, "call", 1)]
    assert sub.splitlines()[line - 1].strip() == "- id: fill-title"
    assert "inputs.title" in text
    records: list[dict[str, object]] = [
        {"path": ["steps", 0]},
        {"path": ["steps", 0, "call", 0]},
        {"path": ["steps", 0, "call", 1]},
        {"path": ["steps", 1]},
    ]
    assert step_targets(folder, records) == [
        None,
        "/",
        "{ label: 標題, exact: true }",
        "/?view=query",
    ]
