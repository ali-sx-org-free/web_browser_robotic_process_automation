"""子場景（M7.2，ADR 0023）的真實執行：scenarios/examples/call 的範例與邊界情況。

用測試網站的建立與查詢頁。每個情境在 Chromium 與 Firefox 各跑一次；本機沒有某種瀏覽器時略過，
CI 設定 RPA_REQUIRE_BROWSER=1 時缺瀏覽器直接失敗。
"""

from collections.abc import Iterator
from pathlib import Path
from typing import cast

import pytest

from rpa_core.dsl.calls import call_file
from rpa_core.i18n import use_locale
from rpa_runner.files import AUTOMATION_LOG, REPORT, SCENARIO_DIR
from rpa_runner.run import RunResult, execute
from testsite.browsers import ENGINES, require_engine
from testsite.server import running

pytestmark = pytest.mark.browser

CALL = Path(__file__).resolve().parents[3] / "scenarios" / "examples" / "call"
SUB = (CALL / call_file("call-create-record", 1)).read_text(encoding="utf-8")
HEADER = """\
schemaVersion: 1
id: call-test
name: 子場景測試
browser: { baseUrl: 'http://127.0.0.1:8765' }
defaults: { timeout: 5000 }
deadline: 60000
"""
CREATE = """\
  - id: create
    action: call
    scenario: call-create-record
    revision: 1
    inputs: { title: 測試, quantity: %s }
    as: created
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


def write(folder: Path, text: str, **subs: str) -> Path:
    """寫出呼叫場景與子場景檔；``subs`` 的鍵是 ``代號__版本``（- 寫成 _），沒給時用範例的子場景。"""
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "scenario.yaml"
    path.write_text(HEADER + text, encoding="utf-8")
    for key, content in (subs or {"call_create_record__1": SUB}).items():
        name, _, revision = key.rpartition("__")
        target = folder / call_file(name.replace("_", "-"), int(revision))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return path


def run_text(text: str, site: str, engine: str, tmp_path: Path, **subs: str) -> RunResult:
    path = write(tmp_path / "scene", text, **subs)
    return execute(path, {}, out_root=tmp_path / "runs", base_url=site, engine=engine)


def by_id(result: RunResult) -> dict[str, list[dict[str, object]]]:
    found: dict[str, list[dict[str, object]]] = {}
    for step in result.steps:
        found.setdefault(str(step["id"]), []).append(step)
    return found


def call_info(step: dict[str, object]) -> dict[str, object]:
    """步驟紀錄的 ``call``（子場景的代號、版本、名稱、獨立斷言與出參名稱）。"""
    info = step["call"]
    assert isinstance(info, dict)
    return cast("dict[str, object]", info)


def checks_of(info: dict[str, object]) -> list[object]:
    """``call.checks`` 每一條的結果（passed）。"""
    checks = info["checks"]
    assert isinstance(checks, list)
    return [cast("dict[str, object]", check)["passed"] for check in cast("list[object]", checks)]


def log_of(result: RunResult) -> str:
    return (result.directory / AUTOMATION_LOG).read_text(encoding="utf-8")


# ---------------------------------------------------------------- 範例


def test_create_and_check_shares_the_browser(site: str, engine: str, tmp_path: Path) -> None:
    result = execute(
        CALL / "create-and-check.yaml", {}, out_root=tmp_path, base_url=site, engine=engine
    )
    assert result.status == "passed", result.error
    assert result.output is not None
    assert str(result.output["recordId"]).startswith("DEMO-")
    steps = by_id(result)
    call = steps["create"][0]
    assert call["action"] == "call"
    assert call["path"] == ["steps", 0]
    info = call_info(call)
    assert (info["scenario"], info["revision"], info["name"]) == (
        "call-create-record",
        1,
        "建立一筆紀錄",
    )
    assert checks_of(info) == [True, True, True]
    assert info["outputs"] == ["recordId", "title", "quantity"]
    # 子場景的步驟縮排在 call 下面：parent 是 call 那一筆，path 過了 "call" 是子場景裡的第幾步
    inner = [step for step in result.steps if step["parent"] == 1]
    assert [step["id"] for step in inner] == [
        "open",
        "fill-title",
        "fill-quantity",
        "submit",
        "wait-receipt",
        "read-record",
    ]
    assert [step["path"] for step in inner] == [["steps", 0, "call", n] for n in range(6)]
    # 呼叫場景自己也有 wait-receipt、read-record：兩邊各一筆，id 相同不相撞
    assert len(steps["read-record"]) == 2
    # 快照帶著子場景檔，回看與報告才找得到子場景步驟的原文
    assert (result.directory / SCENARIO_DIR / call_file("call-create-record", 1)).is_file()
    log = log_of(result)
    assert "子場景 call-create-record 第 1 版" in log
    assert "子場景的獨立斷言：3/3 條通過" in log
    report = (result.directory / REPORT).read_text(encoding="utf-8")
    assert "子場景 call-create-record 第 1 版（建立一筆紀錄）" in report


def test_create_many_collects_every_call(site: str, engine: str, tmp_path: Path) -> None:
    result = execute(
        CALL / "create-many.yaml",
        {"titles": ["甲", "乙"]},
        out_root=tmp_path,
        base_url=site,
        engine=engine,
    )
    assert result.status == "passed", result.error
    assert result.output is not None
    ids = result.output["recordIds"]
    assert isinstance(ids, list)
    assert len(cast("list[str]", ids)) == 2
    assert len(set(cast("list[str]", ids))) == 2
    calls = by_id(result)["create"]
    assert [step["iteration"] for step in calls] == [1, 2]


# ---------------------------------------------------------------- 契約


def test_inputs_are_checked_before_any_sub_step(site: str, engine: str, tmp_path: Path) -> None:
    """代入後才知道的入參（這裡是 99，超過子場景的 maximum）在執行時擋下：子場景一步都不做。"""
    text = "inputs:\n  n: { type: integer, default: 99 }\nsteps:\n" + CREATE % "'{{ inputs.n }}'"
    result = run_text(text, site, engine, tmp_path)
    assert result.status == "failed"
    steps = by_id(result)
    assert steps["create"][0]["status"] == "failed"
    assert "maximum: 30" in str(steps["create"][0]["error"])
    assert "open" not in steps


def test_failed_sub_verify_fails_the_call(site: str, engine: str, tmp_path: Path) -> None:
    """子場景的步驟都通過，但它自己的獨立斷言不通過：call 失敗、出參不交出來。"""
    sub = SUB.replace("equals: 已建立", "equals: 已核准")
    text = "steps:\n" + CREATE % "2" + "  - { id: after, action: screenshot }\n"
    result = run_text(text, site, engine, tmp_path, call_create_record__1=sub)
    assert result.status == "failed"
    steps = by_id(result)
    call = steps["create"][0]
    assert call["status"] == "failed"
    assert "狀態是已建立" in str(call["error"])
    info = call_info(call)
    assert checks_of(info) == [True, False, True]
    assert "outputs" not in info
    assert steps["read-record"][0]["status"] == "passed"
    assert steps["after"][0]["status"] == "skipped"


def test_on_error_continue_and_try_handle_a_failed_call(
    site: str, engine: str, tmp_path: Path
) -> None:
    sub = SUB.replace("equals: 已建立", "equals: 已核准")
    text = (
        "steps:\n"
        + (CREATE % "2").replace("    as: created\n", "    onError: continue\n")
        + """\
  - id: guarded
    action: try
    steps:
      - id: again
        action: call
        scenario: call-create-record
        revision: 1
        inputs: { title: 再一次 }
    catch:
      - { id: note, action: screenshot, file: caught }
  - { id: after, action: screenshot }
"""
    )
    result = run_text(text, site, engine, tmp_path, call_create_record__1=sub)
    assert result.status == "passed", result.error
    steps = by_id(result)
    assert (steps["create"][0]["status"], steps["create"][0]["handled"]) == ("failed", "continued")
    assert (steps["again"][0]["status"], steps["again"][0]["handled"]) == ("failed", "caught")
    assert steps["guarded"][0]["caught"] is not None
    assert steps["after"][0]["status"] == "passed"


def test_failed_sub_step_stops_the_run(site: str, engine: str, tmp_path: Path) -> None:
    sub = SUB.replace("name: 建立紀錄, exact: true", "name: 沒有這個按鈕, exact: true").replace(
        "timeout: 10000", "timeout: 800"
    )
    result = run_text("steps:\n" + CREATE % "2", site, engine, tmp_path, call_create_record__1=sub)
    assert result.status == "failed"
    steps = by_id(result)
    assert steps["submit"][0]["status"] == "failed"
    assert steps["create"][0]["status"] == "failed"
    assert steps["create"][0]["handled"] is None
    assert "wait-receipt" not in steps


# ---------------------------------------------------------------- 隔離


def test_sub_scenario_has_its_own_facts_tabs_and_shots(
    site: str, engine: str, tmp_path: Path
) -> None:
    """子場景的事實不會蓋掉呼叫場景同名的事實；它開了沒關的分頁結束時關掉；截圖檔名加上
    call 的 id。"""
    sub = """\
schemaVersion: 1
id: side
name: 開分頁的子場景
browser: { baseUrl: 'http://127.0.0.1:8765' }
steps:
  - { id: tab, action: openPage, as: extra, url: '/flow?notice=0' }
  - { id: read, action: extract, page: extra, target: { css: h1 }, as: title }
  - { id: shot, action: screenshot, page: extra }
verify:
  - { name: 有標題, value: '{{ facts.title }}', notEmpty: true }
outputs:
  title: { type: string, from: '{{ facts.title }}' }
"""
    text = """\
steps:
  - { id: open, action: goto, url: / }
  - { id: read, action: extract, target: { css: h1 }, as: title }
  - { id: shot, action: screenshot }
  - { id: side, action: call, scenario: side, revision: 1, as: other }
  - { id: tab, action: openPage, as: extra, url: /flow/list }
  - { id: check, action: expect, url: /flow/list, page: extra }
verify:
  - { name: 自己的事實還在, value: '{{ facts.title }}', notEmpty: true }
outputs:
  mine: { type: string, from: '{{ facts.title }}' }
  theirs: { type: string, from: '{{ facts.other.title }}' }
"""
    result = run_text(text, site, engine, tmp_path, side__1=sub)
    assert result.status == "passed", result.error
    assert result.output is not None
    assert result.output["mine"] != result.output["theirs"]
    shots = sorted(path.name for path in result.directory.glob("*shot.png"))
    # screenshot.png 是整次執行結束時的截圖
    assert shots == ["screenshot.png", "shot.png", "side.shot.png"]


def test_nested_sub_scenarios(site: str, engine: str, tmp_path: Path) -> None:
    middle = """\
schemaVersion: 1
id: middle
name: 中間那一層
inputs:
  title: { type: string }
steps:
  - id: inner
    action: call
    scenario: call-create-record
    revision: 1
    inputs: { title: '{{ inputs.title }}' }
    as: made
verify:
  - { name: 有編號, value: '{{ facts.made.recordId }}', notEmpty: true }
outputs:
  recordId: { type: string, from: '{{ facts.made.recordId }}' }
"""
    text = """\
steps:
  - { id: outer, action: call, scenario: middle, revision: 1, inputs: { title: 兩層 }, as: got }
verify:
  - { name: 編號傳回來了, value: '{{ facts.got.recordId }}', matches: '^DEMO-' }
outputs:
  recordId: { type: string, from: '{{ facts.got.recordId }}' }
"""
    result = run_text(text, site, engine, tmp_path, middle__1=middle, call_create_record__1=SUB)
    assert result.status == "passed", result.error
    steps = by_id(result)
    assert steps["inner"][0]["path"] == ["steps", 0, "call", 0]
    assert steps["submit"][0]["path"] == ["steps", 0, "call", 0, "call", 3]
    assert steps["submit"][0]["parent"] == 2
