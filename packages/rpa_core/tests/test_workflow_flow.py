"""組合場景的流程（2026-11-11）：同時執行、條件連線、重複次數的定義、檢查與排程。"""

from collections.abc import Iterator, Mapping
from pathlib import Path

import pytest

from rpa_core.dsl import Scenario, validate_file
from rpa_core.i18n import use_locale
from rpa_core.workflow import (
    EdgeCondition,
    NodeState,
    Workflow,
    WorkflowEdge,
    advance,
    check_workflow,
    condition_holds,
    condition_text,
    parse_workflow,
)

DEMO = Path(__file__).resolve().parents[3] / "scenarios" / "demo"


def load(name: str) -> Scenario:
    scenario = validate_file(DEMO / f"{name}.yaml").scenario
    assert scenario is not None
    return scenario


@pytest.fixture(autouse=True)
def _zh_hant() -> Iterator[None]:
    with use_locale("zh-Hant"):
        yield


def node(node_id: str, scene: str = "ba-004", **extra: object) -> dict[str, object]:
    return {"id": node_id, "sceneId": scene, "revision": 1, **extra}


def dag(
    nodes: list[dict[str, object]], edges: list[dict[str, object]], **extra: object
) -> Workflow:
    workflow, problems = parse_workflow(
        {"version": 2, "mode": "dag", "nodes": nodes, "edges": edges, **extra}
    )
    assert workflow is not None, problems
    return workflow


def branch() -> Workflow:
    """n1 建立紀錄 → quantity 等於 12 走 n2，其他情況走 n3 → 兩邊在 n4 匯合。"""
    return dag(
        [node("n1", "ba-001"), node("n2", "ba-004"), node("n3", "ba-005"), node("n4", "ba-004")],
        [
            {"source": "n1", "target": "n2", "when": {"output": "quantity", "equals": 12}},
            {"source": "n1", "target": "n3", "otherwise": True},
            {"source": "n2", "target": "n4"},
            {"source": "n3", "target": "n4"},
        ],
    )


def scenes(workflow: Workflow) -> dict[str, Scenario | None]:
    return {item.id: load(item.scene_id) for item in workflow.nodes}


# ------------------------------------------------------------------ 定義


def test_old_definitions_keep_their_json() -> None:
    """沒用到新欄位的定義，JSON（也就是雜湊）和以前一樣。"""
    nodes = [node("n1"), node("n2")]
    data: dict[str, object] = {
        "version": 2,
        "mode": "dag",
        "edges": [{"source": "n1", "target": "n2"}],
        "onFailure": "stop",
        "nodes": nodes,
    }
    workflow, problems = parse_workflow(data)
    assert workflow is not None
    assert not problems
    assert workflow.to_json() == {**data, "nodes": [{**item, "inputs": {}} for item in nodes]}


def test_flow_fields_round_trip() -> None:
    workflow = dag(
        [node("n1", "ba-001", repeat=3), node("n2")],
        [{"source": "n1", "target": "n2", "when": {"output": "quantity", "in": [1, 2.5]}}],
        concurrency=2,
    )
    data = workflow.to_json()
    assert data["concurrency"] == 2
    assert data["nodes"][0]["repeat"] == 3  # type: ignore[index]
    assert data["edges"] == [
        {"source": "n1", "target": "n2", "when": {"output": "quantity", "in": [1, 2.5]}}
    ]
    assert Workflow.model_validate(data) == workflow
    assert workflow.parallel == 2
    assert workflow.nodes[0].times == 3
    assert workflow.nodes[1].times == 1


@pytest.mark.parametrize(
    "field",
    [{"concurrency": 2}, {"nodes": [{**node("n1"), "repeat": 2}]}],
)
def test_flow_fields_need_version_2(field: dict[str, object]) -> None:
    data: dict[str, object] = {"version": 1, "mode": "serial", "nodes": [node("n1")], **field}
    workflow, problems = parse_workflow(data)
    assert workflow is None
    assert "只能用在第 2 版" in problems[0].message


@pytest.mark.parametrize(
    ("edge", "message"),
    [
        ({"when": {"output": "quantity"}}, "其中一個"),
        ({"when": {"output": "quantity", "equals": 1, "empty": True}}, "其中一個"),
        ({"when": {"output": "quantity", "in": []}}, "in"),
        ({"when": {"output": "quantity", "equals": None}}, "其中一個"),
        ({"when": {"output": "quantity", "empty": True}, "otherwise": True}, "when 和 otherwise"),
        ({"otherwise": False}, "otherwise"),
    ],
)
def test_bad_conditions(edge: dict[str, object], message: str) -> None:
    workflow, problems = parse_workflow(
        {
            "version": 2,
            "mode": "dag",
            "nodes": [node("n1", "ba-001"), node("n2")],
            "edges": [{"source": "n1", "target": "n2", **edge}],
        }
    )
    assert workflow is None
    assert message in problems[0].message


@pytest.mark.parametrize(("field", "value"), [("repeat", 0), ("repeat", 21), ("concurrency", 11)])
def test_limits(field: str, value: int) -> None:
    nodes = [{**node("n1"), "repeat": value}] if field == "repeat" else [node("n1")]
    extra = {"concurrency": value} if field == "concurrency" else {}
    workflow, _ = parse_workflow({"version": 2, "mode": "dag", "nodes": nodes, **extra})
    assert workflow is None


# ------------------------------------------------------------------ 檢查


def test_branch_checks_clean() -> None:
    workflow = branch()
    assert check_workflow(workflow, scenes(workflow)) == []


@pytest.mark.parametrize(
    ("when", "message"),
    [
        ({"output": "nothing", "equals": 1}, "沒有這個出參"),
        ({"output": "quantity", "equals": "12"}, "不符合出參 quantity 的型別 integer"),
        ({"output": "quantity", "in": [1, True]}, "true 不符合"),
        ({"output": "title", "notEquals": 3}, "型別 string"),
    ],
)
def test_condition_problems(when: dict[str, object], message: str) -> None:
    workflow = dag(
        [node("n1", "ba-001"), node("n2")], [{"source": "n1", "target": "n2", "when": when}]
    )
    problems = check_workflow(workflow, scenes(workflow))
    assert [problem.code for problem in problems][:1] in (
        ["workflow.condition_output_unknown"],
        ["workflow.condition_value_type"],
    )
    assert message in problems[0].message


def test_number_condition_accepts_integers() -> None:
    workflow = dag(
        [node("n1", "ba-001"), node("n2")],
        [{"source": "n1", "target": "n2", "when": {"output": "title", "empty": False}}],
    )
    assert check_workflow(workflow, scenes(workflow)) == []


def test_otherwise_problems() -> None:
    alone = dag(
        [node("n1", "ba-001"), node("n2")], [{"source": "n1", "target": "n2", "otherwise": True}]
    )
    assert [p.code for p in check_workflow(alone, scenes(alone))] == ["workflow.otherwise_alone"]
    twice = dag(
        [node("n1", "ba-001"), node("n2"), node("n3"), node("n4")],
        [
            {"source": "n1", "target": "n2", "when": {"output": "quantity", "equals": 1}},
            {"source": "n1", "target": "n3", "otherwise": True},
            {"source": "n1", "target": "n4", "otherwise": True},
        ],
    )
    assert [p.code for p in check_workflow(twice, scenes(twice))] == [
        "workflow.otherwise_duplicate"
    ]


# ------------------------------------------------------------------ 條件


@pytest.mark.parametrize(
    ("condition", "outputs", "holds"),
    [
        ({"equals": 12}, {"x": 12}, True),
        ({"equals": 12}, {"x": 12.0}, True),
        ({"equals": 12}, {"x": "12"}, False),
        ({"equals": 1}, {"x": True}, False),
        ({"equals": True}, {"x": True}, True),
        ({"equals": True}, {"x": 1}, False),
        ({"equals": "a"}, {}, False),
        ({"equals": "a"}, None, False),
        ({"notEquals": "a"}, {"x": "b"}, True),
        ({"notEquals": "a"}, {"x": "a"}, False),
        ({"notEquals": "a"}, {}, True),
        ({"in": ["a", "b"]}, {"x": "b"}, True),
        ({"in": ["a", "b"]}, {"x": "c"}, False),
        ({"empty": True}, {}, True),
        ({"empty": True}, {"x": None}, True),
        ({"empty": True}, {"x": ""}, True),
        ({"empty": True}, {"x": []}, True),
        ({"empty": True}, {"x": 0}, False),
        ({"empty": False}, {"x": False}, True),
        ({"empty": False}, {"x": {}}, False),
    ],
)
def test_condition_holds(
    condition: dict[str, object], outputs: Mapping[str, object] | None, holds: bool
) -> None:
    parsed = EdgeCondition.model_validate({"output": "x", **condition})
    assert condition_holds(parsed, outputs) is holds


@pytest.mark.parametrize(
    ("edge", "text"),
    [
        ({"when": {"output": "q", "equals": 12}}, "q 等於 12"),
        ({"when": {"output": "q", "notEquals": "A"}}, 'q 不等於 "A"'),
        ({"when": {"output": "q", "in": ["A", 2]}}, 'q 是 "A"、2 其中之一'),
        ({"when": {"output": "q", "empty": True}}, "q 沒有值"),
        ({"when": {"output": "q", "empty": False}}, "q 有值"),
        ({"otherwise": True}, "其他情況"),
        ({}, None),
    ],
)
def test_condition_text(edge: dict[str, object], text: str | None) -> None:
    parsed = WorkflowEdge.model_validate({"source": "a", "target": "b", **edge})
    assert condition_text(parsed) == text


# ------------------------------------------------------------------ 排程


def test_branch_takes_one_side_and_joins() -> None:
    workflow = branch()
    start = advance(workflow, {}, {})
    assert start.ready == ("n1",)
    assert not start.finished

    states: dict[str, NodeState] = {"n1": "passed"}
    outputs: dict[str, Mapping[str, object] | None] = {"n1": {"quantity": 12}}
    step = advance(workflow, states, outputs)
    assert step.ready == ("n2",)
    assert step.skipped == {"n3"}
    assert step.links[("n1", "n2")] == "taken"
    assert step.links[("n1", "n3")] == "not_taken"
    assert step.links[("n3", "n4")] == "not_taken"
    assert step.links[("n2", "n4")] == "pending"

    states["n2"] = "passed"
    step = advance(workflow, states, outputs)
    assert step.ready == ("n4",)

    states["n4"] = "passed"
    assert advance(workflow, states, outputs).finished


def test_otherwise_side() -> None:
    step = advance(branch(), {"n1": "passed"}, {"n1": {"quantity": 3}})
    assert step.ready == ("n3",)
    assert step.skipped == {"n2"}


def test_skip_spreads_downstream() -> None:
    workflow = dag(
        [node("n1", "ba-001"), node("n2"), node("n3"), node("n4")],
        [
            {"source": "n1", "target": "n2", "when": {"output": "quantity", "equals": 1}},
            {"source": "n2", "target": "n3"},
            {"source": "n3", "target": "n4"},
        ],
    )
    step = advance(workflow, {"n1": "passed"}, {"n1": {"quantity": 2}})
    assert step.ready == ()
    assert step.skipped == {"n2", "n3", "n4"}
    assert step.finished


def test_binding_follows_the_drawn_condition() -> None:
    """出參綁定和條件連線指同一對節點時，依那條連線的條件。"""
    workflow = dag(
        [
            node("n1", "ba-001"),
            node("n2", "ba-002", inputs={"recordId": {"node": "n1", "output": "recordId"}}),
        ],
        [{"source": "n1", "target": "n2", "when": {"output": "quantity", "equals": 1}}],
    )
    step = advance(workflow, {"n1": "passed"}, {"n1": {"recordId": "R1", "quantity": 5}})
    assert step.skipped == {"n2"}


def test_binding_alone_is_unconditional() -> None:
    workflow = dag(
        [
            node("n1", "ba-001"),
            node("n2", "ba-002", inputs={"recordId": {"node": "n1", "output": "recordId"}}),
        ],
        [],
    )
    assert advance(workflow, {"n1": "passed"}, {"n1": {"recordId": "R1"}}).ready == ("n2",)


def test_fan_out_is_ready_together() -> None:
    workflow = dag(
        [node("n1"), node("n2"), node("n3"), node("n4")],
        [
            {"source": "n1", "target": "n2"},
            {"source": "n1", "target": "n3"},
            {"source": "n2", "target": "n4"},
            {"source": "n3", "target": "n4"},
        ],
        concurrency=2,
    )
    assert advance(workflow, {}, {}).ready == ("n1",)
    assert advance(workflow, {"n1": "passed"}, {}).ready == ("n2", "n3")
    running: dict[str, NodeState] = {"n1": "passed", "n2": "passed", "n3": "running"}
    step = advance(workflow, running, {})
    assert step.ready == ()
    assert not step.finished


def test_failed_upstream_never_resolves() -> None:
    step = advance(branch(), {"n1": "failed"}, {})
    assert step.ready == ()
    assert not step.skipped
    assert not step.finished


def test_serial_definition_still_runs_in_order() -> None:
    workflow, _ = parse_workflow({"version": 1, "mode": "serial", "nodes": [node("a"), node("b")]})
    assert workflow is not None
    assert advance(workflow, {}, {}).ready == ("a",)
    assert advance(workflow, {"a": "passed"}, {}).ready == ("b",)
    assert advance(workflow, {"a": "passed", "b": "passed"}, {}).finished
