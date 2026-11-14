"""子場景（M7.2，ADR 0023）：call 步驟的校驗、子場景檔的解析與場景的內容雜湊。"""

from collections.abc import Iterator
from pathlib import Path

import pytest

from rpa_core.dsl import Issue, format_issue, validate_file, validate_text
from rpa_core.dsl.calls import (
    MAX_CALL_DEPTH,
    MAX_CALLS,
    call_file,
    call_files,
    closure_features,
    data_call_refs,
    is_call_path,
    load_calls,
)
from rpa_core.dsl.sources import scenario_digest, scenario_sources
from rpa_core.dsl.steps import CallStep
from rpa_core.dsl.yaml_loader import load_yaml
from rpa_core.i18n import use_locale

CALLER = """\
schemaVersion: 1
id: order-new
name: 建立訂單
inputs:
  customer: { type: string }
browser: { baseUrl: 'https://example.test' }
steps:
  - { id: open, action: goto, url: / }
  - id: create-customer
    action: call
    scenario: cust-new
    revision: 4
    inputs: { name: '{{ inputs.customer }}' }
    as: customer
  - id: fill-customer
    action: fill
    target: { label: 客戶編號 }
    value: '{{ facts.customer.customerId }}'
"""

CALLEE = """\
schemaVersion: 1
id: cust-new
name: 建立客戶
inputs:
  name: { type: string, minLength: 1 }
  level: { type: string, default: normal, enum: [normal, vip] }
steps:
  - { id: fill-name, action: fill, target: { label: 名稱 }, value: '{{ inputs.name }}' }
  - { id: save, action: click, target: { role: button, name: 儲存 } }
  - { id: read-id, action: extract, target: { testId: customer-id }, as: customerId }
verify:
  - { name: 有客戶編號, value: '{{ facts.customerId }}', notEmpty: true }
outputs:
  customerId: { type: string, from: '{{ facts.customerId }}' }
"""


@pytest.fixture(autouse=True)
def _zh_hant() -> Iterator[None]:
    with use_locale("zh-Hant"):
        yield


def write(folder: Path, caller: str = CALLER, **callees: str) -> Path:
    """寫出呼叫場景與子場景檔；``callees`` 的鍵是 ``代號__版本``（- 寫成 _）。"""
    path = folder / "scenario.yaml"
    path.write_text(caller, encoding="utf-8")
    for key, text in callees.items():
        name, _, revision = key.rpartition("__")
        target = folder / call_file(name.replace("_", "-"), int(revision))
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return path


def issues(path: Path) -> list[Issue]:
    result = validate_file(path)
    assert result.scenario is None, "應該有問題"
    return list(result.issues)


def only_issue(path: Path) -> Issue:
    found = issues(path)
    assert len(found) == 1, [format_issue(item) for item in found]
    return found[0]


def test_call_step_is_valid_without_a_folder() -> None:
    """只有文字（沒有資料夾）時只檢查寫法：子場景在不在要有資料夾才知道。"""
    result = validate_text(CALLER)
    assert result.ok, [format_issue(item) for item in result.issues]
    assert result.scenario is not None
    steps = result.scenario.steps or []
    assert isinstance(steps[1], CallStep)


def test_call_resolves_and_facts_are_available(tmp_path: Path) -> None:
    path = write(tmp_path, cust_new__4=CALLEE)
    result = validate_file(path)
    assert result.ok, [format_issue(item) for item in result.issues]
    assert result.scenario is not None
    table, problems = load_calls(tmp_path, result.scenario)
    assert problems == []
    assert list(table) == [("cust-new", 4)]
    assert table[("cust-new", 4)].name == "建立客戶"


def test_call_cannot_have_timeout_or_retry() -> None:
    bad = CALLER.replace("    as: customer\n", "    as: customer\n    timeout: 5000\n")
    found = list(validate_text(bad).issues)
    assert [item.code for item in found] == ["call.timeout_not_allowed"]
    assert found[0].path == ("steps", 1, "timeout")
    retry = CALLER.replace("    as: customer\n", "    as: customer\n    retry: { times: 1 }\n")
    assert [item.code for item in validate_text(retry).issues] == ["retry.not_allowed"]


def test_fact_from_call_must_come_first() -> None:
    lines = CALLER.splitlines(keepends=True)
    # 把用到 facts.customer 的那一步搬到 call 前面
    moved = "".join(lines[:8] + lines[14:] + lines[8:14])
    found = list(validate_text(moved).issues)
    assert [item.code for item in found] == ["template.fact_not_yet"]


def test_missing_sub_scenario_file(tmp_path: Path) -> None:
    issue = only_issue(write(tmp_path))
    assert issue.code == "call.missing"
    assert issue.path == ("steps", 1, "scenario")
    assert "calls/cust-new/4.yaml" in issue.message
    assert issue.position is not None
    assert issue.position.line == 11


def test_invalid_sub_scenario(tmp_path: Path) -> None:
    broken = CALLEE.replace("action: click", "action: clik")
    issue = only_issue(write(tmp_path, cust_new__4=broken))
    assert issue.code == "call.invalid"
    assert "clik" in issue.message


def test_sub_scenario_id_must_match(tmp_path: Path) -> None:
    other = CALLEE.replace("id: cust-new", "id: cust-other")
    issue = only_issue(write(tmp_path, cust_new__4=other))
    assert issue.code == "call.id_mismatch"
    assert "cust-other" in issue.message


def test_sub_scenario_must_be_dsl(tmp_path: Path) -> None:
    script = """\
schemaVersion: 1
id: cust-new
name: 腳本
script: { automation: automation.py, assertion: assertion.py }
"""
    caller = CALLER.replace("    inputs: { name: '{{ inputs.customer }}' }\n", "").replace(
        "    as: customer\n", ""
    )
    caller = caller.split("  - id: fill-customer")[0]
    issue = only_issue(write(tmp_path, caller, cust_new__4=script))
    assert issue.code == "call.script"


def test_login_role_must_match(tmp_path: Path) -> None:
    callee = CALLEE.replace("steps:\n", "login: { role: clerk }\nsteps:\n", 1)
    issue = only_issue(write(tmp_path, cust_new__4=callee))
    assert issue.code == "call.login"
    same = CALLER.replace("steps:\n", "login: { role: clerk }\nsteps:\n", 1)
    assert validate_file(write(tmp_path, same, cust_new__4=callee)).ok
    # 子場景不需要登入時，呼叫場景有沒有登入都可以
    assert validate_file(write(tmp_path, same, cust_new__4=CALLEE)).ok


def test_secrets_must_be_declared_by_caller(tmp_path: Path) -> None:
    callee = CALLEE.replace("steps:\n", "secrets: [ERP_TOKEN]\nsteps:\n", 1)
    issue = only_issue(write(tmp_path, cust_new__4=callee))
    assert issue.code == "call.secrets"
    assert "ERP_TOKEN" in issue.message
    caller = CALLER.replace("steps:\n", "secrets: [ERP_TOKEN]\nsteps:\n", 1)
    assert validate_file(write(tmp_path, caller, cust_new__4=callee)).ok


def test_file_inputs_are_not_supported(tmp_path: Path) -> None:
    callee = CALLEE.replace(
        "  level: { type: string, default: normal, enum: [normal, vip] }\n",
        "  level: { type: string, default: normal, enum: [normal, vip] }\n"
        "  sheet: { type: file, default: files/a.xlsx }\n",
    )
    issue = only_issue(write(tmp_path, cust_new__4=callee))
    assert issue.code == "call.files"
    assert "sheet" in issue.message


def test_inputs_are_checked_against_the_contract(tmp_path: Path) -> None:
    unknown = CALLER.replace(
        "inputs: { name: '{{ inputs.customer }}' }",
        "inputs: { name: '{{ inputs.customer }}', nmae: x }",
    )
    issue = only_issue(write(tmp_path, unknown, cust_new__4=CALLEE))
    assert (issue.code, issue.path) == ("call.input_unknown", ("steps", 1, "inputs", "nmae"))

    missing = CALLER.replace("    inputs: { name: '{{ inputs.customer }}' }\n", "")
    issue = only_issue(write(tmp_path, missing, cust_new__4=CALLEE))
    assert issue.code == "call.input_missing"
    assert "name" in issue.message

    invalid = CALLER.replace(
        "inputs: { name: '{{ inputs.customer }}' }", "inputs: { name: A, level: gold }"
    )
    issue = only_issue(write(tmp_path, invalid, cust_new__4=CALLEE))
    assert (issue.code, issue.path) == ("call.input_invalid", ("steps", 1, "inputs", "level"))
    assert "enum" in issue.message

    wrong_type = CALLER.replace("inputs: { name: '{{ inputs.customer }}' }", "inputs: { name: 3 }")
    issue = only_issue(write(tmp_path, wrong_type, cust_new__4=CALLEE))
    assert issue.code == "call.input_invalid"
    assert "type: string" in issue.message


def test_as_requires_outputs(tmp_path: Path) -> None:
    callee = CALLEE.split("verify:")[0]
    caller = CALLER.split("  - id: fill-customer")[0]
    issue = only_issue(write(tmp_path, caller, cust_new__4=callee))
    assert (issue.code, issue.path) == ("call.no_outputs", ("steps", 1, "as"))
    assert validate_file(
        write(tmp_path, caller.replace("    as: customer\n", ""), cust_new__4=callee)
    ).ok


def _chain(folder: Path, depth: int) -> Path:
    """呼叫場景 → s1 → s2 → …，共 ``depth`` 層子場景。"""
    path = folder / "scenario.yaml"
    for level in range(depth + 1):
        name = "root" if level == 0 else f"s{level}"
        steps = "  - { id: open, action: goto, url: 'https://example.test/' }\n"
        if level < depth:
            steps += f"  - {{ id: next, action: call, scenario: s{level + 1}, revision: 1 }}\n"
        text = f"schemaVersion: 1\nid: {name}\nname: 第 {level} 層\nsteps:\n{steps}"
        target = path if level == 0 else folder / call_file(name, 1)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return path


def test_nested_calls_up_to_the_limit(tmp_path: Path) -> None:
    path = _chain(tmp_path, MAX_CALL_DEPTH)
    result = validate_file(path)
    assert result.ok, [format_issue(item) for item in result.issues]
    assert result.scenario is not None
    assert call_files(tmp_path, result.scenario) == [
        call_file(f"s{level}", 1) for level in range(1, MAX_CALL_DEPTH + 1)
    ]


def test_nested_calls_too_deep(tmp_path: Path) -> None:
    deep = tmp_path / "deep"
    deep.mkdir()
    issue = only_issue(_chain(deep, MAX_CALL_DEPTH + 1))
    assert issue.code == "call.too_deep"
    assert issue.path == ("steps", 1, "scenario")


def test_call_cycle(tmp_path: Path) -> None:
    a = (
        "schemaVersion: 1\nid: a\nname: A\nsteps:\n"
        "  - { id: to-b, action: call, scenario: b, revision: 1 }\n"
    )
    b = (
        "schemaVersion: 1\nid: b\nname: B\nsteps:\n"
        "  - { id: to-a, action: call, scenario: a, revision: 2 }\n"
    )
    issue = only_issue(write(tmp_path, a, b__1=b))
    assert issue.code == "call.cycle"
    own = a.replace("scenario: b, revision: 1", "scenario: a, revision: 1")
    assert only_issue(write(tmp_path, own)).code == "call.cycle"


def test_too_many_sub_scenarios(tmp_path: Path) -> None:
    count = MAX_CALLS + 1
    steps = "".join(
        f"  - {{ id: c{n}, action: call, scenario: s{n}, revision: 1 }}\n" for n in range(count)
    )
    caller = f"schemaVersion: 1\nid: many\nname: 很多\nsteps:\n{steps}"
    path = tmp_path / "scenario.yaml"
    path.write_text(caller, encoding="utf-8")
    for n in range(count):
        target = tmp_path / call_file(f"s{n}", 1)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            f"schemaVersion: 1\nid: s{n}\nname: 子場景\nsteps:\n"
            "  - { id: open, action: goto, url: 'https://example.test/' }\n",
            encoding="utf-8",
        )
    issue = only_issue(path)
    assert issue.code == "call.too_many"


def test_sub_scenarios_are_part_of_the_digest(tmp_path: Path) -> None:
    path = write(tmp_path, cust_new__4=CALLEE)
    scenario = validate_file(path).scenario
    assert scenario is not None
    assert scenario_sources(path, scenario) == ["scenario.yaml", "calls/cust-new/4.yaml"]
    before = scenario_digest(path, scenario)
    (tmp_path / call_file("cust-new", 4)).write_text(
        CALLEE.replace("建立客戶", "建立客戶（改）"), encoding="utf-8"
    )
    assert scenario_digest(path, scenario) != before


def test_scenarios_without_calls_keep_their_digest(tmp_path: Path) -> None:
    """沒有用到 call 的場景：來源只有場景檔，旁邊多出 calls/ 也不算進去。"""
    path = tmp_path / "scenario.yaml"
    path.write_text(CALLEE, encoding="utf-8")
    scenario = validate_file(path).scenario
    assert scenario is not None
    before = scenario_digest(path, scenario)
    extra = tmp_path / call_file("unused", 1)
    extra.parent.mkdir(parents=True)
    extra.write_text(CALLEE, encoding="utf-8")
    assert scenario_sources(path, scenario) == ["scenario.yaml"]
    assert scenario_digest(path, scenario) == before


def test_call_inside_a_block_and_data_refs(tmp_path: Path) -> None:
    caller = """\
schemaVersion: 1
id: batch
name: 逐筆建立
inputs:
  names: { type: array }
steps:
  - id: each
    action: forEach
    items: '{{ inputs.names }}'
    as: item
    steps:
      - id: create
        action: call
        scenario: cust-new
        revision: 4
        inputs: { name: '{{ item }}' }
        onError: continue
"""
    path = write(tmp_path, caller, cust_new__4=CALLEE)
    result = validate_file(path)
    assert result.ok, [format_issue(item) for item in result.issues]
    data, _ = load_yaml(caller)
    assert data_call_refs(data) == [("cust-new", 4)]
    assert data_call_refs({"steps": "x"}) == []
    assert data_call_refs(None) == []


def test_closure_features(tmp_path: Path) -> None:
    callee = CALLEE.replace("name: 儲存 } }\n", "name: 儲存 }, onError: continue }\n")
    path = write(tmp_path, cust_new__4=callee)
    scenario = validate_file(path).scenario
    assert scenario is not None
    table, _ = load_calls(tmp_path, scenario)
    assert closure_features(scenario, table) == {"call", "flow"}


def test_is_call_path() -> None:
    assert is_call_path("calls/cust-new/4.yaml")
    assert is_call_path("calls")
    assert not is_call_path("callsx/a.yaml")
    assert not is_call_path("files/calls/a.yaml")
