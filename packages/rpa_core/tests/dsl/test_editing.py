"""改寫場景檔的入參、出參段落（表單編輯），以及產生 YAML 片段。"""

import json
from pathlib import Path
from textwrap import dedent
from typing import cast

import pytest

from rpa_core.dsl import validate_text
from rpa_core.dsl.editing import (
    SectionError,
    append_items,
    contract_section,
    find_block,
    json_document,
    rename_input,
    replace_contract,
    replace_section,
    section_line,
    section_text,
)
from rpa_core.dsl.yaml_loader import load_yaml
from rpa_core.dsl.yaml_writer import block, flow, scalar

ROOT = Path(__file__).resolve().parents[4]
BA_001 = ROOT / "scenarios" / "demo" / "ba-001.yaml"


@pytest.mark.parametrize(
    "value",
    [
        "建立紀錄",
        "true",
        "123",
        "1.5",
        "null",
        "",
        " 前後有空白 ",
        "a: b",
        "# 註解",
        "{{ inputs.title }}",
        "#record-id",
        "^DEMO-[A-Z0-9]+$",
        "\\S",
        "line\nbreak",
        "「全形」",
        "- 開頭是減號",
        "http://127.0.0.1:8765",
    ],
)
def test_scalar_reads_back_as_the_same_string(value: str) -> None:
    data, _ = load_yaml(f"key: {scalar(value)}\nflow: {{ a: {scalar(value)} }}\n")
    assert data == {"key": value, "flow": {"a": value}}


def test_scalar_writes_plain_text_when_it_can() -> None:
    assert scalar("建立紀錄") == "建立紀錄"
    assert scalar("true") == '"true"'
    assert scalar(True) == "true"
    assert scalar(12) == "12"
    assert scalar(None) == "null"


def test_block_and_flow() -> None:
    lines = block(
        {
            "steps": [{"id": "a", "action": "click", "target": {"role": "button", "name": "OK"}}],
            "inputs": {"title": {"type": "string", "enum": ["a", "b"]}},
            "empty": {},
        },
        flow_keys=frozenset({"target"}),
    )
    assert lines == [
        "steps:",
        "  - id: a",
        "    action: click",
        "    target: { role: button, name: OK }",
        "inputs:",
        "  title:",
        "    type: string",
        "    enum: [a, b]",
        "empty: {}",
    ]
    assert flow({}) == "{}"


SCENARIO = """\
# 開頭的註解
schemaVersion: 1
id: demo
name: 示範

# 入參說明
inputs:
  title:
    type: string
    default: 舊的
  # 中間的註解
  count:
    type: integer

# 步驟的說明
steps:
  - id: fill
    action: fill
    target: { label: 標題 }
    value: '{{ inputs.title }}'
  - id: fill-again
    action: fill
    target: { label: 標題 }
    value: '{{ inputs["title"] }} / {{ inputs.titles }}'
"""


def test_find_block_keeps_comments_of_the_next_section_outside() -> None:
    lines = SCENARIO.splitlines()
    start, end = find_block(lines, "inputs") or (0, 0)
    assert lines[start] == "inputs:"
    assert lines[end - 1] == "    type: integer"
    assert find_block(lines, "outputs") is None


def test_replace_contract_only_changes_the_two_sections() -> None:
    text = replace_contract(
        SCENARIO,
        inputs={
            "headline": {"type": "string", "default": "新的", "minLength": 1},
            "count": {"type": "integer", "minimum": 0},
        },
        outputs={"result": {"type": "string", "from": "{{ inputs.headline }}"}},
        renames={"title": "headline"},
    )

    assert text.startswith("# 開頭的註解\nschemaVersion: 1\n")
    assert (
        "# 入參說明\ninputs:\n  headline:\n    type: string\n    default: 新的\n    minLength: 1\n"
        in text
    )
    assert "  count:\n    type: integer\n    minimum: 0\n\noutputs:\n  result:\n" in text
    assert "# 步驟的說明\nsteps:" in text
    assert "value: '{{ inputs.headline }}'" in text
    # 名稱只是開頭相同的引用（titles）不會被改
    assert """value: '{{ inputs["headline"] }} / {{ inputs.titles }}'""" in text
    assert "中間的註解" not in text


def test_removing_all_inputs_drops_the_section() -> None:
    text = replace_contract(SCENARIO.replace("{{ inputs.title }}", "x"), inputs={}, outputs={})
    assert "inputs:" not in text
    assert "\n\n\n" not in text


def test_adding_sections_to_a_scenario_without_them() -> None:
    plain = (
        "schemaVersion: 1\nid: demo\nname: 示範\n\n"
        "steps:\n  - id: open\n    action: goto\n    url: https://example.com/\n"
    )
    text = replace_contract(plain, inputs={"q": {"type": "string", "default": "x"}}, outputs={})
    assert text == (
        "schemaVersion: 1\nid: demo\nname: 示範\n\ninputs:\n  q:\n    type: string\n"
        "    default: x\n\nsteps:\n  - id: open\n    action: goto\n    url: https://example.com/\n"
    )
    assert validate_text(text).ok


def test_round_trip_of_a_real_scenario_keeps_it_valid() -> None:
    original = BA_001.read_text(encoding="utf-8")
    scenario = validate_text(original).scenario
    assert scenario is not None
    inputs = {
        name: spec.model_dump(mode="json", by_alias=True, exclude_none=True)
        for name, spec in scenario.inputs.items()
    }
    outputs = {
        name: spec.model_dump(mode="json", by_alias=True, exclude_none=True)
        for name, spec in scenario.outputs.items()
    }
    text = replace_contract(original, inputs=inputs, outputs=outputs)
    again = validate_text(text).scenario
    assert again is not None
    assert again.inputs == scenario.inputs
    assert again.outputs == scenario.outputs
    assert again.steps == scenario.steps
    # 段落以外的內容完全相同
    assert text.split("inputs:")[0] == original.split("inputs:")[0]
    assert text.split("\nbrowser:")[1] == original.split("\nbrowser:")[1]


def test_crlf_files_keep_their_line_endings() -> None:
    text = replace_contract(SCENARIO.replace("\n", "\r\n"), inputs={}, outputs={}, renames={})
    assert "\r\n" in text
    assert "\n" not in text.replace("\r\n", "")


def test_rename_input() -> None:
    assert rename_input("{{ inputs.a }} {{ inputs.ab }} {{ facts.inputs.a }}", "a", "b") == (
        "{{ inputs.b }} {{ inputs.ab }} {{ facts.inputs.a }}"
    )
    assert rename_input("{{ inputs['a'] }}", "a", "b") == "{{ inputs['b'] }}"


SECTIONS = dedent(
    """\
    schemaVersion: 1
    id: demo
    name: 範例

    steps:
    - id: open  # 第一欄開始的清單也是 steps 的內容
      action: goto
      url: https://example.com/

    # 斷言的說明
    verify:
      - value: "{{ facts.x }}"
        notEmpty: true
    """
)


def test_section_text_and_replace_section() -> None:
    from rpa_core.dsl.editing import replace_section, section_text

    steps = section_text(SECTIONS, "steps")
    assert steps.splitlines()[0] == "steps:"
    assert steps.splitlines()[-1] == "  url: https://example.com/"
    assert section_text(SECTIONS, "inputs") == ""

    verify = 'verify:\n  - value: "{{ facts.y }}"\n    equals: a'
    replaced = replace_section(SECTIONS, "verify", verify)
    assert "# 斷言的說明" in replaced  # 段落前的註解保留
    assert "facts.x" not in replaced
    assert "facts.y" in replaced
    assert replaced.startswith(SECTIONS.split("verify:")[0])

    added = replace_section(SECTIONS, "inputs", "inputs:\n  q: { type: string }")
    assert added.index("inputs:") < added.index("steps:")
    removed = replace_section(added, "inputs", "")
    assert removed == SECTIONS


def test_append_items_follows_the_existing_indentation() -> None:
    from rpa_core.dsl.editing import append_items

    item = ["  - id: next", "    action: goto", "    url: https://example.com/next"]
    appended = append_items(SECTIONS, "steps", item, whole=["steps:", *item])
    assert "\n- id: next\n  action: goto\n" in appended
    assert appended.index("- id: next") < appended.index("# 斷言的說明")

    flow = "schemaVersion: 1\nsecrets: [A]\n"
    assert append_items(flow, "secrets", ["  - B"], whole=["secrets:", "  - A", "  - B"]) == (
        "schemaVersion: 1\nsecrets:\n  - A\n  - B\n"
    )


# ---------------------------------------------------------------- JSON 寫法的場景檔（2026-11-10）

JSON_SCENARIO = (
    json.dumps(
        {
            "schemaVersion": 1,
            "id": "demo",
            "name": "示範",
            "inputs": {"title": {"type": "string", "default": "舊的"}},
            "deadline": 120000,
            "steps": [
                {"id": "open", "action": "goto", "url": "https://example.com/"},
                {
                    "id": "fill",
                    "action": "fill",
                    "target": {"label": "標題"},
                    "value": '{{ inputs.title }} / {{ inputs["title"] }}',
                },
                {"id": "read", "action": "extract", "target": {"css": "#result"}, "as": "result"},
            ],
            "verify": [{"name": "有結果", "value": "{{ facts.result }}", "notEmpty": True}],
            "outputs": {"result": {"type": "string", "from": "{{ facts.result }}"}},
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
    + "\n"
)
"""壓成一行的 JSON 場景檔：使用者回報的寫法（AI 產生），可以執行，但段落不能顯示與編輯。"""


def _keys(text: str) -> list[str]:
    return list(json.loads(text))


def test_json_document_only_accepts_a_plain_json_object() -> None:
    assert json_document(JSON_SCENARIO) is not None
    assert json_document("﻿  " + JSON_SCENARIO) is not None
    assert json_document(SECTIONS) is None
    assert json_document("[1, 2]") is None
    assert json_document('{"a": 1, "a": 2}') is None  # 重複的鍵交給校驗說明
    assert json_document('{"a": NaN}') is None
    assert json_document("{ a: 1 }") is None  # YAML 的流式寫法不是 JSON


def test_section_text_of_a_json_scenario_is_a_json_object_with_that_key() -> None:
    steps = section_text(JSON_SCENARIO, "steps")
    assert steps.startswith('{\n  "steps": [\n    {\n      "id": "open",')
    assert json.loads(steps) == {"steps": json.loads(JSON_SCENARIO)["steps"]}
    assert '"label": "標題"' in steps  # 中文不跳脫
    assert json.loads(section_text(JSON_SCENARIO, "inputs")) == {
        "inputs": {"title": {"type": "string", "default": "舊的"}}
    }
    assert section_text(JSON_SCENARIO, "secrets") == ""


def test_replacing_a_section_of_a_json_scenario_keeps_it_json() -> None:
    """回報的問題：入參存檔時在 JSON 後面接上 YAML，出現「expected '<document start>'」。"""
    yaml_inputs = (
        "inputs:\n  title:\n    type: string\n    default: 新的\n  count:\n    type: integer"
    )
    json_inputs = '{"inputs": {"title": {"type": "string", "default": "新的"}, "count": {}}}'
    for section in (yaml_inputs, json_inputs):
        text = replace_section(JSON_SCENARIO, "inputs", section)
        assert text.endswith("}\n")
        assert text.count("\n") == 1  # 壓成一行的還是一行
        assert _keys(text) == _keys(JSON_SCENARIO)  # 鍵的順序不變
        assert json.loads(text)["inputs"]["title"]["default"] == "新的"
        assert validate_text(text).ok
    assert replace_section(JSON_SCENARIO, "steps", section_text(JSON_SCENARIO, "steps")) == (
        JSON_SCENARIO
    )


def test_adding_and_removing_sections_of_a_json_scenario() -> None:
    without = replace_section(JSON_SCENARIO, "verify", "")
    assert "verify" not in json.loads(without)
    again = replace_section(without, "verify", section_text(JSON_SCENARIO, "verify"))
    assert again == JSON_SCENARIO  # 加回來時接在 steps 後面
    no_inputs = replace_section(JSON_SCENARIO, "inputs", "  \n")
    added = replace_section(no_inputs, "inputs", "inputs:\n  q: { type: string }")
    assert _keys(added).index("inputs") < _keys(added).index("deadline")


def test_json_scenarios_keep_their_indentation_and_line_endings() -> None:
    data = json.loads(JSON_SCENARIO)
    pretty = json.dumps(data, ensure_ascii=False, indent=4).replace("\n", "\r\n")
    text = replace_section(pretty, "inputs", "inputs:\n  title: { type: string }")
    assert text.startswith('{\r\n    "schemaVersion": 1,')
    assert "\n" not in text.replace("\r\n", "")
    assert not text.endswith("\n")
    spaced = json.dumps(data, ensure_ascii=False) + "\n"
    assert replace_section(spaced, "inputs", section_text(spaced, "inputs")) == spaced


def test_unreadable_or_wrong_sections_raise_section_error() -> None:
    with pytest.raises(SectionError) as caught:
        replace_section(JSON_SCENARIO, "steps", '{\n  "steps": [\n    {"id" "a"}\n  ]\n}')
    assert caught.value.error is not None
    assert caught.value.position is not None
    assert caught.value.position.line == 3  # 段落裡的行號
    with pytest.raises(SectionError) as caught:
        replace_section(JSON_SCENARIO, "steps", '{"verify": []}')
    assert caught.value.error is None
    with pytest.raises(SectionError):
        replace_section(SECTIONS, "steps", '{"steps": [], "verify": []}')


def test_json_sections_in_a_yaml_scenario_become_block_yaml() -> None:
    steps = '{"steps": [{"id": "open", "action": "goto", "url": "https://example.com/"}, ' + (
        '{"id": "ok", "action": "click", "target": {"role": "button", "name": "確定"}}]}'
    )
    text = replace_section(SECTIONS, "steps", steps)
    assert "\nsteps:\n  - id: open\n" in text
    assert "    target: { role: button, name: 確定 }\n" in text
    assert "# 斷言的說明\nverify:" in text  # 其他段落一個字都不動
    assert text.startswith("schemaVersion: 1\nid: demo\nname: 範例\n\nsteps:")
    data, _ = load_yaml(text)
    assert cast("dict[str, object]", data)["steps"] == json.loads(steps)["steps"]


def test_replace_contract_of_a_json_scenario_renames_references_in_values() -> None:
    text = replace_contract(
        JSON_SCENARIO,
        inputs={"headline": {"default": "x", "type": "string"}},
        outputs={},
        renames={"title": "headline"},
    )
    data = json.loads(text)
    assert data["inputs"] == {"headline": {"type": "string", "default": "x"}}  # 欄位依固定順序
    assert data["steps"][1]["value"] == '{{ inputs.headline }} / {{ inputs["headline"] }}'
    assert "outputs" not in data
    assert text.count("\n") == 1
    assert replace_contract(JSON_SCENARIO, inputs=None, outputs=None) == JSON_SCENARIO
    assert json.loads(
        contract_section("outputs", {"a": {"from": "x", "type": "string"}}, as_json=True)
    ) == {"outputs": {"a": {"type": "string", "from": "x"}}}


def test_append_items_to_a_json_scenario() -> None:
    step = ["  - id: next", "    action: goto", "    url: https://example.com/next"]
    text = append_items(JSON_SCENARIO, "steps", step, whole=["steps:", *step])
    assert [item["id"] for item in json.loads(text)["steps"]] == ["open", "fill", "read", "next"]
    text = append_items(text, "inputs", ["  q:", "    type: string"], whole=[])
    assert list(json.loads(text)["inputs"]) == ["title", "q"]
    text = append_items(text, "secrets", ["  - PASSWORD"], whole=["secrets:", "  - PASSWORD"])
    assert _keys(text).index("secrets") < _keys(text).index("steps")
    assert append_items(text, "steps", ["  # 轉不了的一行"], whole=[]) == text
    assert text.count("\n") == 1


def test_section_line_points_into_the_section_text() -> None:
    broken = replace_section(JSON_SCENARIO, "steps", '{"steps": [{"id": "a", "action": "goto"}]}')
    issues = validate_text(broken).issues
    assert issues
    issue = issues[0]
    assert issue.position is not None
    assert issue.position.line == 1  # 整份只有一行
    line = section_line(broken, "steps", issue.path, issue.position.line)
    assert line == 3
    assert section_text(broken, "steps").splitlines()[2] == "    {"
    assert section_line(broken, "verify", issue.path, issue.position.line) is None
    # YAML 寫法照舊用檔案的行號換算：段落第一行是 steps:
    assert section_line(SECTIONS, "steps", ("steps", 0), 6) == 2
    assert section_line(SECTIONS, "steps", ("verify", 0), 11) is None
