"""流程控制（M7.1，ADR 0021）的校驗：區塊步驟、條件、retry、onError、openPage／closePage、
append。"""

from collections.abc import Iterator

import pytest

from rpa_core.dsl import Issue, Position, format_issue, validate_text
from rpa_core.dsl.steps import MAX_ITERATIONS, MAX_NESTING, walk_steps
from rpa_core.i18n import use_locale

HEADER = "schemaVersion: 1\nid: demo\nname: 示範\n"
GOTO = "{ id: %s, action: goto, url: 'https://example.test/' }"


@pytest.fixture(autouse=True)
def _zh_hant() -> Iterator[None]:
    with use_locale("zh-Hant"):
        yield


def scenario(steps: str, top: str = "") -> str:
    return HEADER + top + "steps:\n" + steps


def position_of(text: str, needle: str) -> Position:
    index = text.index(needle)
    line = text.count("\n", 0, index) + 1
    column = index - (text.rfind("\n", 0, index) + 1) + 1
    return Position(line, column)


def issues(text: str) -> list[Issue]:
    result = validate_text(text)
    assert result.scenario is None, "應該有問題"
    return list(result.issues)


def only_issue(text: str) -> Issue:
    found = issues(text)
    assert len(found) == 1, [format_issue(i) for i in found]
    return found[0]


FULL = scenario(
    """\
  - { id: open, action: goto, url: 'https://example.test/' }
  - id: notice
    action: if
    condition: { target: { role: dialog }, state: visible, wait: 500 }
    then:
      - { id: close, action: click, target: { role: button, name: 關閉 } }
    else:
      - { id: no-notice, action: screenshot }
  - id: each
    action: forEach
    items: '{{ inputs.orders }}'
    as: order
    steps:
      - id: fill
        action: fill
        target: { label: 標題 }
        value: '{{ order.title }}-{{ loop.index }}'
      - { id: read, action: extract, target: { testId: rid }, as: ids, append: true }
  - id: pages
    action: repeat
    while: { target: { role: button, name: 下一頁 }, state: enabled }
    max: 50
    steps:
      - { id: next, action: click, target: { role: button, name: 下一頁 } }
      - { id: more, action: extract, target: { testId: rid }, as: ids, append: true }
  - id: thrice
    action: repeat
    times: 3
    steps:
      - { id: tick, action: press, key: Tab, onError: continue }
  - id: guarded
    action: try
    steps:
      - { id: risky, action: click, target: { text: 問卷 } }
    catch:
      - { id: shot, action: screenshot, file: survey }
      - { id: back, action: goto, url: 'https://example.test/?from={{ error.step }}' }
  - { id: report, action: openPage, as: report, url: 'https://example.test/report' }
  - id: total
    action: extract
    page: report
    target: { testId: total }
    as: total
    retry: { times: 2, delay: 500 }
  - { id: close-report, action: closePage, page: report }
""",
    top="inputs:\n  orders: { type: array }\n"
    "outputs:\n  ids: { type: array, from: '{{ facts.ids }}' }\n"
    "verify:\n  - { name: 有編號, value: '{{ facts.ids | length }}', matches: '^[1-9]' }\n",
)


def test_full_flow_scenario_is_valid_and_walks_in_file_order() -> None:
    result = validate_text(FULL)

    assert result.issues == (), [format_issue(i) for i in result.issues]
    assert result.scenario is not None
    walked = [(path, step.id, depth) for path, step, depth in walk_steps(result.scenario.steps)]
    assert walked[:5] == [
        (("steps", 0), "open", 0),
        (("steps", 1), "notice", 0),
        (("steps", 1, "then", 0), "close", 1),
        (("steps", 1, "else", 0), "no-notice", 1),
        (("steps", 2), "each", 0),
    ]
    assert ("steps", 5, "catch", 1) in [path for path, _, _ in walked]


def test_scenarios_without_flow_dump_the_same_fields() -> None:
    """沒用到新語法的步驟，model_dump（exclude_none）不多出任何欄位。"""
    text = scenario("  - { id: a, action: extract, target: { css: b }, as: x }\n")
    checked = validate_text(text).scenario
    assert checked is not None
    assert checked.steps is not None
    dumped = checked.steps[0].model_dump(mode="json", by_alias=True, exclude_none=True)
    assert set(dumped) == {"id", "action", "target", "as", "get", "multiple"}


# ---------------------------------------------------------------- 條件


@pytest.mark.parametrize(
    ("condition", "code", "field"),
    [
        ("{ expression: '{{ inputs.a }}', wait: 100 }", "condition.expression_only", "wait"),
        ("{ expression: '{{ inputs.a }}', title: x }", "condition.expression_only", "title"),
        ("{ wait: 100 }", "condition.none", "condition"),
        ("{ target: { css: a } }", "one_of.none", "condition"),
        ("{ target: { css: a }, state: visible, url: x }", "expect.page_check_with_target", "url"),
        ("{ state: visible }", "field.requires", "state"),
        (
            "{ target: { css: a }, state: visible, match: regex }",
            "expect.match_not_applicable",
            "match",
        ),
        ("{ title: '(', match: regex }", "regex.invalid", "title"),
    ],
)
def test_condition_rules(condition: str, code: str, field: str) -> None:
    text = scenario(
        f"  - id: c\n    action: if\n    condition: {condition}\n    then: [{GOTO % 'g'}]\n",
        top="inputs:\n  a: { type: boolean }\n",
    )
    issue = only_issue(text)

    assert issue.code == code
    assert issue.field.endswith(field)


def test_expression_condition_can_use_inputs_facts_and_loop_variables() -> None:
    text = scenario(
        "  - { id: x, action: extract, target: { css: a }, as: n }\n"
        "  - id: each\n"
        "    action: forEach\n"
        "    items: [1, 2]\n"
        "    as: item\n"
        "    steps:\n"
        "      - id: c\n"
        "        action: if\n"
        "        condition: { expression: \"{{ inputs.mode == 'a' and item > facts.n|int }}\" }\n"
        f"        then: [{GOTO % 'g'}]\n",
        top="inputs:\n  mode: { type: string }\n",
    )
    assert validate_text(text).issues == ()


# ---------------------------------------------------------------- 區塊


def test_block_cannot_have_timeout_or_page() -> None:
    text = scenario(
        "  - { id: c, action: if, timeout: 100, condition: { title: x },\n"
        f"      then: [{GOTO % 'g'}] }}\n"
    )
    issue = only_issue(text)

    assert issue.code == "block.field_not_allowed"
    assert issue.field == "timeout"
    assert "if 是區塊步驟" in issue.message


@pytest.mark.parametrize(
    ("fields", "code"),
    [
        ("while: { title: x }", "repeat.max_required"),
        ("until: { title: x }", "repeat.max_required"),
        ("times: 2, max: 3", "repeat.max_with_times"),
        ("times: 2, until: { title: x }, max: 3", "one_of.many"),
        ("max: 3", "one_of.none"),
    ],
)
def test_repeat_rules(fields: str, code: str) -> None:
    text = scenario(f"  - {{ id: r, action: repeat, {fields}, steps: [{GOTO % 'g'}] }}\n")
    assert only_issue(text).code == code


def test_repeat_limits() -> None:
    text = scenario(
        f"  - {{ id: r, action: repeat, times: {MAX_ITERATIONS + 1}, steps: [{GOTO % 'g'}] }}\n"
    )
    assert only_issue(text).code == "less_than_equal"


def test_for_each_items_must_be_a_template_or_a_list() -> None:
    text = scenario(f"  - {{ id: e, action: forEach, items: abc, as: x, steps: [{GOTO % 'g'}] }}\n")
    issue = only_issue(text)

    assert issue.code == "forEach.items_format"
    assert issue.field == "items"


def test_empty_branches_are_reported_at_the_branch() -> None:
    text = scenario("  - { id: c, action: try, steps: [], catch: [] }\n")
    found = issues(text)

    assert [(i.code, i.field) for i in found] == [
        ("too_few_items", "steps"),
        ("too_few_items", "catch"),
    ]


def test_blocks_nest_at_most_max_levels() -> None:
    inner = GOTO % "leaf"
    for level in range(MAX_NESTING + 1):
        inner = f"{{ id: t{level}, action: try, steps: [{inner}], catch: [{GOTO % f'c{level}'}] }}"
    issue = only_issue(scenario(f"  - {inner}\n"))

    assert issue.code == "block.too_deep"
    assert issue.message == f"區塊步驟最多巢狀 {MAX_NESTING} 層"


def test_errors_inside_blocks_name_the_innermost_step() -> None:
    text = scenario(
        "  - " + GOTO % "g" + "\n"
        "  - id: c\n"
        "    action: if\n"
        "    condition: { title: x }\n"
        "    then:\n"
        "      - id: inner\n"
        "        action: click\n"
        "        target: { nth: 1 }\n"
    )
    issue = only_issue(text)

    assert issue.code == "locator.no_strategy"
    assert issue.step == 2
    assert issue.step_id == "inner"
    assert issue.step_path == ("steps", 1, "then", 0)
    assert issue.field == "target"
    assert issue.position == position_of(text, "{ nth")
    assert format_issue(issue).startswith("步驟 2 › then[0]（inner） › target：")


# ---------------------------------------------------------------- 迴圈變數與 {{ }} 的範圍


def test_loop_variable_only_inside_its_loop() -> None:
    text = scenario(
        "  - id: e\n"
        "    action: forEach\n"
        "    items: '{{ row }}'\n"
        "    as: row\n"
        "    steps:\n"
        "      - id: f\n"
        "        action: fill\n"
        "        target: { label: a }\n"
        "        value: '{{ row.no }} {{ loop.index }}'\n"
        "  - { id: after, action: goto, url: 'https://example.test/{{ row }}' }\n"
    )
    found = issues(text)

    assert [(i.code, i.step_id) for i in found] == [
        ("template.unknown_variable", "e"),
        ("template.unknown_variable", "after"),
    ]


def test_error_only_inside_catch() -> None:
    text = scenario(
        "  - id: t\n"
        "    action: try\n"
        "    steps:\n"
        "      - { id: a, action: goto, url: 'https://example.test/{{ error.step }}' }\n"
        "    catch:\n"
        "      - { id: b, action: goto, url: 'https://example.test/{{ error.message }}' }\n"
    )
    issue = only_issue(text)

    assert issue.code == "template.unknown_variable"
    assert issue.step_id == "a"


def test_unknown_variable_lists_loop_variables_in_scope() -> None:
    text = scenario(
        "  - id: e\n"
        "    action: forEach\n"
        "    items: [1]\n"
        "    as: row\n"
        "    steps:\n"
        "      - { id: f, action: fill, target: { label: a }, value: '{{ rwo }}' }\n"
    )
    assert "inputs, secrets, facts, env, loop, row" in only_issue(text).message


@pytest.mark.parametrize(
    ("name", "code"),
    [
        ("loop", "forEach.reserved_name"),
        ("facts", "forEach.reserved_name"),
        ("row", "forEach.shadowed_name"),
    ],
)
def test_loop_variable_names(name: str, code: str) -> None:
    text = scenario(
        "  - id: outer\n"
        "    action: forEach\n"
        "    items: [1]\n"
        "    as: row\n"
        "    steps:\n"
        f"      - {{ id: inner, action: forEach, items: [2], as: {name}, steps: [{GOTO % 'g'}] }}\n"
    )
    issue = only_issue(text)

    assert issue.code == code
    assert issue.step_id == "inner"
    assert issue.field == "as"


def test_facts_from_branches_are_available_afterwards() -> None:
    text = scenario(
        "  - id: c\n"
        "    action: if\n"
        "    condition: { title: x }\n"
        "    then:\n"
        "      - { id: a, action: extract, target: { css: a }, as: maybe }\n"
        "  - { id: b, action: goto, url: 'https://example.test/{{ facts.maybe }}' }\n"
    )
    assert validate_text(text).issues == ()


# ---------------------------------------------------------------- id、事實與 append


def test_step_ids_are_unique_across_blocks() -> None:
    text = scenario(
        "  - " + GOTO % "same" + "\n"
        f"  - {{ id: c, action: if, condition: {{ title: x }}, then: [{GOTO % 'same'}] }}\n"
    )
    issue = only_issue(text)

    assert issue.code == "step.duplicate_id"
    assert issue.step_path == ("steps", 1, "then", 0)


def test_several_steps_can_append_to_one_fact() -> None:
    text = scenario(
        "  - { id: a, action: extract, target: { css: a }, as: rows, append: true }\n"
        "  - { id: b, action: extract, target: { css: b }, as: rows, append: true }\n"
    )
    assert validate_text(text).issues == ()


def test_append_and_plain_extract_cannot_share_a_fact() -> None:
    text = scenario(
        "  - { id: a, action: extract, target: { css: a }, as: rows, append: true }\n"
        "  - { id: b, action: extract, target: { css: b }, as: rows }\n"
    )
    issue = only_issue(text)

    assert issue.code == "extract.duplicate_as_append"
    assert "append: true" in issue.message


# ---------------------------------------------------------------- onError、retry


def test_on_error_is_allowed_on_any_step() -> None:
    text = scenario(
        "  - { id: a, action: click, target: { css: a }, onError: continue }\n"
        "  - { id: b, action: try, onError: continue,\n"
        f"      steps: [{GOTO % 'g'}], catch: [{GOTO % 'h'}] }}\n"
    )
    assert validate_text(text).issues == ()


@pytest.mark.parametrize(
    ("action", "fields"),
    [
        ("click", "target: { css: a }"),
        ("fill", "target: { css: a }, value: x"),
        ("check", "target: { css: a }"),
        ("press", "key: Enter"),
        ("upload", "target: { css: a }, files: '{{ inputs.f }}'"),
        ("download", "target: { css: a }, as: d"),
        ("openPage", "as: p"),
    ],
)
def test_retry_only_on_actions_without_side_effects(action: str, fields: str) -> None:
    text = scenario(
        f"  - {{ id: a, action: {action}, {fields}, retry: {{ times: 1 }} }}\n",
        top="inputs:\n  f: { type: file }\n",
    )
    issue = only_issue(text)

    assert issue.code == "retry.not_allowed"
    assert issue.field == "retry"
    assert f"{action} 不行" in issue.message


def test_retry_limits() -> None:
    text = scenario(
        "  - { id: a, action: goto, url: 'https://example.test/', retry: { times: 6 } }\n"
    )
    issue = only_issue(text)

    assert issue.code == "less_than_equal"
    assert issue.field == "retry.times"


# ---------------------------------------------------------------- openPage、closePage


def test_open_page_and_close_page() -> None:
    text = scenario(
        "  - { id: o, action: openPage, as: report, url: /report }\n"
        "  - { id: c, action: closePage, page: report }\n"
        "  - { id: again, action: click, page: report, target: { css: a } }\n",
        top="browser: { baseUrl: 'https://example.test' }\n",
    )
    issue = only_issue(text)

    assert issue.code == "page.closed"
    assert issue.step_id == "again"


def test_open_page_names_share_popup_names() -> None:
    text = scenario(
        "  - { id: a, action: click, target: { css: a }, popup: report }\n"
        "  - { id: o, action: openPage, as: report }\n"
    )
    issue = only_issue(text)

    assert issue.code == "popup.duplicate"
    assert issue.field == "as"


@pytest.mark.parametrize(
    ("step", "code"),
    [
        ("{ id: c, action: closePage }", "closePage.page_required"),
        ("{ id: c, action: closePage, page: nowhere }", "page.undefined"),
        ("{ id: o, action: openPage, as: x, page: y }", "openPage.page_not_allowed"),
        ("{ id: o, action: openPage, as: x, url: /r }", "url.relative_without_base"),
    ],
)
def test_page_step_rules(step: str, code: str) -> None:
    assert only_issue(scenario(f"  - {step}\n")).code == code


def test_condition_page_must_be_open() -> None:
    text = scenario(
        "  - { id: c, action: if, condition: { title: x, page: nowhere },\n"
        f"      then: [{GOTO % 'g'}] }}\n"
    )
    issue = only_issue(text)

    assert issue.code == "page.undefined"
    assert issue.field == "condition.page"
