"""M7 收尾：流程控制的範例（scenarios/examples/flow）在第一次啟動時和 BA 範例一起匯入
「測試網站自動化」；運行頁有「N 步失敗後繼續」的提醒（M7.1 的 D6，和執行報告相同）。"""

import json
import threading
from collections.abc import Callable, Mapping
from dataclasses import replace
from pathlib import Path
from typing import cast

import pytest
from fastapi import FastAPI
from httpx2 import Client

from rpa_core.dsl import validate_file
from rpa_runner.files import RESULT
from rpa_runner.login import LoginSettings
from rpa_runner.run import RunResult, StageName
from rpa_server.config import Settings
from rpa_server.domain import now
from rpa_server.services import Services
from rpa_worker import Worker

ROOT = Path(__file__).resolve().parents[3]
FLOW = ROOT / "scenarios" / "examples" / "flow"
FLOW_IDS = [
    "flow-add-entries",
    "flow-close-notice",
    "flow-optional-survey",
    "flow-read-all-pages",
    "flow-report-tab",
    "flow-wait-report",
]
BA_IDS = ["ba-001", "ba-001-script", "ba-002", "ba-003", "ba-004", "ba-005"]


@pytest.fixture
def settings(settings: Settings) -> Settings:
    return replace(settings, extra_examples=(FLOW,))


def services(app: FastAPI) -> Services:
    return cast("Services", app.state.services)


def test_flow_examples_are_seeded_with_the_testsite_examples(app: FastAPI, client: Client) -> None:
    report = services(app).seed_examples_domain()
    assert report is not None
    assert sorted(report.imported) == sorted(BA_IDS + FLOW_IDS)
    domain = client.get("/api/domains/testsite").json()
    assert sorted(card["id"] for card in domain["scenes"]) == sorted(BA_IDS + FLOW_IDS)
    again = client.post("/api/scenes/import").json()
    assert again["imported"] == []


class HandledExecutor:
    """假的執行器：通過，但有一步失敗後繼續、一步被 catch 接住；照真的執行器寫 result.json。"""

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
        directory = out_root / run_id
        directory.mkdir(parents=True, exist_ok=True)
        result = RunResult(
            run_id=run_id,
            scenario_id=scenario.id,
            scenario_name=scenario.name,
            scenario_hash="0" * 64,
            kind="dsl",
            engine=engine or scenario.browser.engine,
            directory=directory,
            started_at=now().isoformat(),
            status="passed",
            input=dict(inputs),
            output={"recordId": "DEMO-1", "title": "x", "quantity": 1},
            steps=[
                {"id": "open", "status": "passed"},
                {"id": "optional-tip", "status": "failed", "handled": "continued"},
                {"id": "survey", "status": "failed", "handled": "caught"},
            ],
        )
        (directory / RESULT).write_text(json.dumps(result.to_json()), encoding="utf-8")
        return result


def test_run_page_shows_steps_that_failed_and_continued(app: FastAPI, client: Client) -> None:
    client.post("/api/scenes/import")
    queued = client.post("/api/scenes/ba-001/revisions/1/validate", json={"inputs": {}})
    assert queued.status_code == 202, queued.text
    run_id = queued.json()["id"]
    worker = Worker(cast("Worker", app.state.worker).source, executor=HandledExecutor())
    assert worker.run_once() is True
    page = client.get(f"/runs/{run_id}")
    assert page.status_code == 200
    assert 'data-handled="2"' in page.text
    assert "有 2 步失敗後繼續" in page.text
