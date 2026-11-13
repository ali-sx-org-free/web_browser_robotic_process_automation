"""流程控制（M7.1，ADR 0021）的真實執行：scenarios/examples/flow 的範例與邊界情況。

用測試網站的 /flow、/flow/list、/flow/report。每個情境在 Chromium 與 Firefox 各跑一次；
本機沒有某種瀏覽器時略過，CI 設定 RPA_REQUIRE_BROWSER=1 時缺瀏覽器直接失敗。
"""

import json
from collections.abc import Iterator
from pathlib import Path

import pytest

from rpa_core.i18n import use_locale
from rpa_runner import browser
from rpa_runner.files import AUTOMATION_LOG, VIDEO_INFO
from rpa_runner.run import RunResult, execute
from testsite.browsers import ENGINES, require_engine
from testsite.server import running

pytestmark = pytest.mark.browser

FLOW = Path(__file__).resolve().parents[3] / "scenarios" / "examples" / "flow"
HEADER = """\
schemaVersion: 1
id: flow-test
name: 流程測試
browser: { baseUrl: 'http://127.0.0.1:8765' }
defaults: { timeout: 5000 }
deadline: 60000
"""


@pytest.fixture(params=ENGINES)
def engine(request: pytest.FixtureRequest) -> str:
    return require_engine(str(request.param))


@pytest.fixture(scope="module")
def site() -> Iterator[str]:
    with running() as url:
        yield url


@pytest.fixture(autouse=True)
def _zh_hant() -> Iterator[None]:
    with use_locale("zh-Hant"):
        yield


def run_example(
    name: str, site: str, engine: str, tmp_path: Path, inputs: dict[str, object] | None = None
) -> RunResult:
    return execute(FLOW / name, inputs or {}, out_root=tmp_path, base_url=site, engine=engine)


def run_text(text: str, site: str, engine: str, tmp_path: Path) -> RunResult:
    scenario = tmp_path / "scenario.yaml"
    scenario.write_text(HEADER + text, encoding="utf-8")
    return execute(scenario, {}, out_root=tmp_path / "runs", base_url=site, engine=engine)


def by_id(result: RunResult) -> dict[str, list[dict[str, object]]]:
    found: dict[str, list[dict[str, object]]] = {}
    for step in result.steps:
        found.setdefault(str(step["id"]), []).append(step)
    return found


def log_of(result: RunResult) -> str:
    return (result.directory / AUTOMATION_LOG).read_text(encoding="utf-8")


# ---------------------------------------------------------------- 範例


@pytest.mark.parametrize("shown", [True, False])
def test_close_notice_takes_the_branch_that_matches_the_page(
    site: str, engine: str, tmp_path: Path, shown: bool
) -> None:
    text = (FLOW / "close-notice.yaml").read_text(encoding="utf-8")
    text = text.replace("url: /flow\n", f"url: /flow?notice={int(shown)}\n")
    scenario = tmp_path / "close-notice.yaml"
    scenario.write_text(text, encoding="utf-8")

    result = execute(scenario, {}, out_root=tmp_path / "runs", base_url=site, engine=engine)

    assert result.status == "passed", (result.error, result.problems)
    steps = by_id(result)
    notice = steps["notice"][0]
    assert notice["condition"] is shown
    assert notice["branch"] == ("then" if shown else None)
    assert ("close-notice" in steps) is shown
    assert result.output == {"recordId": "F-001"}
    if shown:
        close = steps["close-notice"][0]
        assert close["path"] == ["steps", 1, "then", 0]
        assert close["parent"] == 2
    # 區塊裡的步驟緊接在區塊後面，最外層的步驟照原本的順序
    assert [step["id"] for step in result.steps if step["parent"] is None] == [
        "open",
        "notice",
        "fill-title",
        "add",
        "read-id",
    ]


def test_for_each_runs_once_per_item_and_appends(site: str, engine: str, tmp_path: Path) -> None:
    result = run_example("add-entries.yaml", site, engine, tmp_path)

    assert result.status == "passed", (result.error, result.problems)
    assert result.output == {"recordIds": ["F-001", "F-002", "F-003"]}
    steps = by_id(result)
    assert steps["each-order"][0]["iterations"] == 3
    assert [step["iteration"] for step in steps["fill-title"]] == [1, 2, 3]
    assert {step["parent"] for step in steps["read-id"]} == {2}
    assert len(result.steps) == 2 + 3 * 5
    log = log_of(result)
    assert "第 2/2 步  每一筆訂單（forEach）  開始" in log
    assert "› fill-title（fill）（第 3 輪）  通過" in log
    assert "共執行 3 輪" in log


@pytest.mark.parametrize(("rows", "rounds"), [(13, 2), (5, 0)])
def test_repeat_while_reads_every_page(
    site: str, engine: str, tmp_path: Path, rows: int, rounds: int
) -> None:
    result = run_example("read-all-pages.yaml", site, engine, tmp_path, {"rows": rows})

    assert result.status == "passed", (result.error, result.problems)
    output = result.output or {}
    assert [row["單號"] for row in output["rows"]] == [f"L-{i:03d}" for i in range(1, rows + 1)]  # type: ignore[index]
    assert by_id(result)["next-pages"][0]["iterations"] == rounds


def test_retry_waits_for_the_report(site: str, engine: str, tmp_path: Path) -> None:
    result = run_example("wait-report.yaml", site, engine, tmp_path)

    assert result.status == "passed", (result.error, result.problems)
    wait = by_id(result)["wait-done"][0]
    assert int(str(wait["attempts"])) >= 2
    assert any("再試一次" in str(note) for note in wait["notes"])  # type: ignore[union-attr]
    assert "（retry）" in log_of(result)


def test_retry_gives_up_after_the_last_attempt(site: str, engine: str, tmp_path: Path) -> None:
    text = (FLOW / "wait-report.yaml").read_text(encoding="utf-8")
    text = text.replace("retry: { times: 4, delay: 500 }", "retry: { times: 1, delay: 100 }")
    scenario = tmp_path / "wait.yaml"
    scenario.write_text(text, encoding="utf-8")

    result = execute(
        scenario, {"delay": 5000}, out_root=tmp_path / "runs", base_url=site, engine=engine
    )

    assert result.status == "failed"
    wait = by_id(result)["wait-done"][0]
    assert wait["attempts"] == 2
    assert wait["status"] == "failed"


def test_try_catches_and_on_error_continues(site: str, engine: str, tmp_path: Path) -> None:
    result = run_example("optional-survey.yaml", site, engine, tmp_path)

    assert result.status == "passed", (result.error, result.problems)
    steps = by_id(result)
    survey = steps["survey"][0]
    assert survey["status"] == "passed"
    assert survey["caught"] == {
        "step": "submit-survey",
        "error": steps["submit-survey"][0]["error"],
    }
    assert steps["submit-survey"][0]["handled"] == "caught"
    assert steps["survey-failed"][0]["artifacts"] == ["survey-failed.png"]
    assert (result.directory / "survey-failed.png").is_file()
    assert steps["optional-tip"][0]["status"] == "failed"
    assert steps["optional-tip"][0]["handled"] == "continued"
    log = log_of(result)
    assert "失敗，由 catch 處理" in log
    assert "失敗，繼續執行（onError: continue）" in log
    assert "接住 submit-survey 的失敗" in log
    report = (result.directory / "report.html").read_text(encoding="utf-8")
    assert "有 2 步失敗後繼續（onError 或 catch）" in report
    assert '<span class="badge amber">由 catch 處理</span>' in report
    assert "padding-left:24px'>submit-survey" in report  # 區塊裡的步驟縮排


def test_open_page_and_close_page(site: str, engine: str, tmp_path: Path) -> None:
    result = run_example("report-tab.yaml", site, engine, tmp_path, {"month": "2026-11"})

    assert result.status == "passed", (result.error, result.problems)
    assert result.output == {"total": "1320"}
    steps = by_id(result)
    assert str(steps["read-total"][0]["url"]).endswith("/flow/report?month=2026-11")
    assert str(steps["still-here"][0]["url"]).endswith("/flow?notice=0")


def test_open_page_is_replayed_on_the_new_tab(site: str, tmp_path: Path) -> None:
    """openPage 這一步記在新分頁上：回看在新分頁載入時就切過去（2026-11-13）。"""
    require_engine("chromium")
    result = execute(
        FLOW / "report-tab.yaml",
        {},
        out_root=tmp_path,
        base_url=site,
        engine="chromium",
        record_video=True,
    )

    assert result.status == "passed", (result.error, result.problems)
    steps = by_id(result)
    opened = steps["open-report"][0]
    assert opened["pageId"] == opened["createdPageId"] == "page-2"
    assert [steps[name][0]["pageId"] for name in ("open", "read-total", "close-report")] == [
        "page-1",
        "page-2",
        "page-2",
    ]
    assert steps["still-here"][0]["pageId"] == "page-1"
    info = json.loads((result.directory / VIDEO_INFO).read_text(encoding="utf-8"))
    assert {clip["pageId"] for clip in info["clips"]} == {"page-1", "page-2"}


# ---------------------------------------------------------------- 邊界


def test_expression_conditions_and_nested_loops(site: str, engine: str, tmp_path: Path) -> None:
    result = run_text(
        """\
steps:
  - { id: open, action: goto, url: '/flow?notice=0' }
  - id: rows
    action: forEach
    items: [1, 2, 3]
    as: n
    steps:
      - id: odd
        action: if
        condition: { expression: '{{ n % 2 == 1 }}' }
        then:
          - id: add-odd
            action: fill
            target: { label: 標題 }
            value: '第 {{ loop.index }}／{{ loop.count }} 項是 {{ n }}'
        else:
          - { id: even, action: expect, title: 流程控制, match: contains }
""",
        site,
        engine,
        tmp_path,
    )

    assert result.status == "passed", (result.error, result.problems)
    steps = by_id(result)
    assert [step["branch"] for step in steps["odd"]] == ["then", "else", "then"]
    assert len(steps["add-odd"]) == 2
    assert [step["iteration"] for step in steps["odd"]] == [1, 2, 3]


def test_condition_errors_fail_the_block(site: str, engine: str, tmp_path: Path) -> None:
    """判斷出錯不當成「不成立」：引用沒有值的事實（產生它的分支沒走到），這個區塊失敗。"""
    result = run_text(
        """\
steps:
  - { id: open, action: goto, url: '/flow?notice=0' }
  - id: maybe
    action: if
    condition: { expression: '{{ false }}' }
    then:
      - { id: read, action: extract, target: { css: h1 }, as: heading }
  - id: check
    action: if
    condition: { expression: "{{ facts.heading == 'x' }}" }
    then:
      - { id: never, action: goto, url: /flow }
""",
        site,
        engine,
        tmp_path,
    )

    assert result.status == "failed"
    assert by_id(result)["check"][0]["status"] == "failed"
    assert "never" not in by_id(result)


def test_repeat_until_that_never_ends_fails_at_max(site: str, engine: str, tmp_path: Path) -> None:
    result = run_text(
        """\
steps:
  - { id: open, action: goto, url: '/flow?notice=0' }
  - id: forever
    action: repeat
    until: { title: 永遠不會出現的標題 }
    max: 3
    steps:
      - { id: look, action: expect, title: 流程控制 }
""",
        site,
        engine,
        tmp_path,
    )

    assert result.status == "failed"
    forever = by_id(result)["forever"][0]
    assert forever["iterations"] == 3
    assert "until 的條件還沒成立" in str(forever["error"])


def test_too_many_records_cannot_be_continued(
    site: str, engine: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """紀錄超過上限：即使寫了 onError: continue 也停下（D4）。子程序讀不到 monkeypatch，
    所以在同一個程序裡直接呼叫 run_steps。"""
    monkeypatch.setattr(browser, "MAX_RECORDS", 4)
    scenario_text = HEADER + (
        "steps:\n"
        "  - { id: open, action: goto, url: '/flow?notice=0' }\n"
        "  - id: many\n"
        "    action: forEach\n"
        "    onError: continue\n"
        "    items: [1, 2, 3, 4, 5]\n"
        "    as: n\n"
        "    steps:\n"
        "      - { id: look, action: expect, title: 流程控制 }\n"
    )
    from playwright.sync_api import sync_playwright

    from rpa_core.dsl import validate_text

    checked = validate_text(scenario_text).scenario
    assert checked is not None
    records = browser.plan_records(checked)
    with sync_playwright() as playwright:
        launched = getattr(playwright, engine).launch()
        try:
            page = launched.new_page()
            with pytest.raises(browser.FlowLimitExceeded):
                browser.run_steps(
                    page,
                    checked,
                    records=records,
                    context={"inputs": {}, "secrets": {}, "env": {}},
                    base_url=site,
                    artifacts=tmp_path,
                    deadline=browser.Deadline.after(60),
                )
        finally:
            launched.close()
    assert len(records) == 4
    assert records[1].status == "failed"
    assert records[1].handled is None
