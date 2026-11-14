"""組合場景的定義、DAG 依賴檢查、入參解析與排程。

第 2 版以 edges 與出參綁定表達依賴，節點陣列和畫布座標不決定執行順序。第 1 版 serial 仍按
原順序執行；舊定義與歷史快照不改寫。此模組不依賴資料庫或瀏覽器。

組合場景的流程（2026-11-11，只有第 2 版）：

- **同時執行**（``concurrency``）：同時就緒的節點最多幾個一起排入佇列，由空著的 worker 各自領取；
  沒寫是 1，和以前一樣逐個執行。
- **條件連線**（``when``／``otherwise``）：連線看來源節點的一個出參，成立才算走到；``otherwise``
  是來源的其他條件連線都不成立時才走到。節點的上游都結束（通過或略過）後，只要有一條連線走到
  就執行，一條都沒有就略過，略過會往下傳。出參綁定也算一條連線：同一對節點有畫出的連線時
  依那條連線的條件，沒有時是無條件的。
- **重複次數**（``repeat``）：節點一次接一次跑幾次（最多 20），每次都要通過，下游用最後一次的出參。

排程由 :func:`advance` 從各節點目前的狀態算出：哪些節點可以開始、哪些略過、是否全部結束。
略過不另外存，任何時候都能從節點的結果重新算出來。
"""

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Annotated, Final, Literal, Self

from pydantic import Discriminator, Field, Tag, ValidationError, model_validator

from rpa_core.dsl.dynamic import DynamicValueError, escape
from rpa_core.dsl.fields import DslModel, Identifier, Slug, catalog, dsl_error
from rpa_core.dsl.issues import format_field
from rpa_core.dsl.scenario import Scenario

__all__ = [
    "MAX_CONCURRENCY",
    "MAX_NODES",
    "MAX_REPEAT",
    "AutoBinding",
    "Binding",
    "EdgeCondition",
    "InputSource",
    "LinkState",
    "NodePosition",
    "NodeState",
    "OutputBinding",
    "Progress",
    "ValueBinding",
    "Workflow",
    "WorkflowEdge",
    "WorkflowNode",
    "WorkflowProblem",
    "advance",
    "check_workflow",
    "compatible",
    "condition_holds",
    "condition_text",
    "input_sources",
    "parse_workflow",
    "plan_workflow",
    "resolve_inputs",
    "sequence",
]

MAX_NODES: Final = 50
"""一個組合場景最多幾個節點。"""

MAX_REPEAT: Final = 20
"""一個節點最多重複幾次（使用者 2026-11-11 決定）。"""

MAX_CONCURRENCY: Final = 10
"""最多幾個節點同時執行。"""

Scalar = str | int | float | bool
"""條件比較的值：字串、數字、布林。"""


class AutoBinding(DslModel):
    """從直接上游尋找唯一的同名相容出參；沒有命中時使用場景預設。"""

    auto: Literal[True]


class ValueBinding(DslModel):
    """固定值：執行時直接當成入參。"""

    value: object

    @model_validator(mode="after")
    def _check(self) -> Self:
        if self.value is None:
            raise dsl_error("workflow.value_null", at=["value"])
        return self


class OutputBinding(DslModel):
    """前面某個節點的出參：上游通過之後才有值。"""

    node: Slug
    output: Identifier


def _binding_kind(value: object) -> str:
    if isinstance(value, AutoBinding) or (isinstance(value, dict) and "auto" in value):
        return "auto"
    if isinstance(value, ValueBinding) or (isinstance(value, dict) and "value" in value):
        return "value"
    return "output"


Binding = Annotated[
    Annotated[ValueBinding, Tag("value")]
    | Annotated[OutputBinding, Tag("output")]
    | Annotated[AutoBinding, Tag("auto")],
    Discriminator(_binding_kind),
]
"""入參的來源：固定值或前面節點的出參；沒寫就用場景的預設值。"""


class NodePosition(DslModel):
    """畫布座標，僅影響顯示，不影響依賴關係。"""

    x: Annotated[float, Field(ge=0, le=100000, allow_inf_nan=False)]
    y: Annotated[float, Field(ge=0, le=100000, allow_inf_nan=False)]


class EdgeCondition(DslModel):
    """條件連線看來源節點的哪個出參、怎麼比：``equals``、``notEquals``、``in``、``empty`` 其一。

    - ``equals``／``notEquals``：和一個字串、數字或布林比；整數 12 和 12.0 相等，布林只和布林相等；
    - ``in``：是清單裡的其中一個；
    - ``empty: true`` 是沒有值（出參沒有、是 null、空字串、空清單或空物件），``false`` 是有值。

    出參沒有時，``equals``、``in`` 不成立，``notEquals`` 成立。
    """

    output: Identifier
    equals: Scalar | None = None
    not_equals: Scalar | None = None
    in_: Annotated[list[Scalar], Field(min_length=1, max_length=50)] | None = Field(
        default=None, alias="in"
    )
    empty: bool | None = None

    @model_validator(mode="after")
    def _one(self) -> Self:
        used = [
            alias
            for attr, alias in (
                ("equals", "equals"),
                ("not_equals", "notEquals"),
                ("in_", "in"),
                ("empty", "empty"),
            )
            if getattr(self, attr) is not None
        ]
        if len(used) != 1:
            raise dsl_error("workflow.condition_one")
        return self

    @property
    def operator(self) -> Literal["equals", "notEquals", "in", "empty"]:
        if self.equals is not None:
            return "equals"
        if self.not_equals is not None:
            return "notEquals"
        if self.in_ is not None:
            return "in"
        return "empty"

    def values(self) -> list[Scalar]:
        """要比較的值（``empty`` 沒有）。"""
        if self.in_ is not None:
            return list(self.in_)
        value = self.equals if self.equals is not None else self.not_equals
        return [value] if value is not None else []


class WorkflowEdge(DslModel):
    """來源通過後，目標才可開始。資料綁定也會形成相同的依賴。

    ``when`` 是條件連線：來源通過而且條件成立才算走到；``otherwise`` 是來源的其他條件連線都不成立時
    才走到。兩者都沒寫是一般連線，來源通過就走到。
    """

    source: Slug
    target: Slug
    when: EdgeCondition | None = None
    otherwise: Literal[True] | None = None

    @model_validator(mode="after")
    def _check(self) -> Self:
        if self.when is not None and self.otherwise is not None:
            raise dsl_error("workflow.edge_condition_both", at=["otherwise"])
        return self

    @property
    def conditional(self) -> bool:
        return self.when is not None or self.otherwise is not None


class WorkflowNode(DslModel):
    """組合場景的一個節點：某個場景的固定版本，加上入參的來源。"""

    position: NodePosition | None = None
    id: Slug
    """節點代號，組合場景裡不能重複；綁定時用它指定上游，例如 n1。"""
    scene_id: Slug
    revision: Annotated[int, Field(ge=1)]
    """固定的版本號碼；只能是發布過的版本。"""
    inputs: dict[Identifier, Binding] = Field(
        default_factory=dict[str, ValueBinding | OutputBinding | AutoBinding]
    )
    repeat: Annotated[int, Field(ge=1, le=MAX_REPEAT)] | None = None
    """一次接一次跑幾次，每次都要通過，下游用最後一次的出參；沒寫是 1（只有第 2 版）。"""

    @property
    def times(self) -> int:
        return self.repeat or 1


class Workflow(DslModel):
    """組合場景定義：第 1 版線性序列與第 2 版 DAG。"""

    version: Literal[1, 2] = 1
    mode: Literal["serial", "dag"] = "serial"
    edges: Annotated[list[WorkflowEdge], Field(max_length=2500)] = Field(
        default_factory=list[WorkflowEdge]
    )
    """依賴邊；執行順序由拓撲排序決定。"""
    on_failure: Literal["stop"] = "stop"
    """節點沒有通過時：停止，還沒開始的節點不執行；已經在跑的節點跑完。"""
    concurrency: Annotated[int, Field(ge=1, le=MAX_CONCURRENCY)] | None = None
    """同時就緒的節點最多幾個一起執行；沒寫是 1（只有第 2 版）。"""
    nodes: Annotated[list[WorkflowNode], Field(max_length=MAX_NODES)] = Field(
        default_factory=list[WorkflowNode]
    )

    @model_validator(mode="after")
    def _unique_ids(self) -> Self:
        if (self.version == 1) != (self.mode == "serial") or (self.mode == "serial" and self.edges):
            raise dsl_error("workflow.mode_version")
        if self.mode == "serial":
            if self.concurrency is not None:
                raise dsl_error(
                    "workflow.flow_requires_dag", at=["concurrency"], field="concurrency"
                )
            for index, node in enumerate(self.nodes):
                if node.repeat is not None:
                    raise dsl_error(
                        "workflow.flow_requires_dag", at=["nodes", index, "repeat"], field="repeat"
                    )
        seen: set[str] = set()
        for index, node in enumerate(self.nodes):
            if node.id in seen:
                raise dsl_error("workflow.node_duplicate", at=["nodes", index, "id"], node=node.id)
            seen.add(node.id)
        return self

    def node(self, node_id: str) -> WorkflowNode | None:
        return next((node for node in self.nodes if node.id == node_id), None)

    def index(self, node_id: str) -> int:
        """節點的位置（從 0 開始）；沒有這個節點時是 -1。"""
        return next((i for i, node in enumerate(self.nodes) if node.id == node_id), -1)

    @property
    def parallel(self) -> int:
        """同時執行的上限；沒寫是 1。"""
        return self.concurrency or 1

    def links(self) -> dict[str, dict[str, WorkflowEdge | None]]:
        """節點 → {上游節點 → 那條連線}；None 是無條件的依賴（出參綁定、第 1 版的順序）。

        同一對節點有畫出的連線時用那條連線（含它的條件）；只有出參綁定時是無條件的。
        """
        links: dict[str, dict[str, WorkflowEdge | None]] = {node.id: {} for node in self.nodes}
        for target, sources in self.dependencies().items():
            for source in sources:
                links[target][source] = None
        if self.mode == "dag":
            for edge in self.edges:
                if edge.target in links and edge.conditional:
                    links[edge.target][edge.source] = edge
        return links

    def dependencies(self) -> dict[str, set[str]]:
        """節點 → 必須先通過的節點；資料綁定不能繞過依賴。"""
        dependencies = {node.id: set[str]() for node in self.nodes}
        if self.mode == "serial":
            for previous, node in zip(self.nodes, self.nodes[1:], strict=False):
                dependencies[node.id].add(previous.id)
        else:
            for edge in self.edges:
                if edge.target in dependencies:
                    dependencies[edge.target].add(edge.source)
            for node in self.nodes:
                for binding in node.inputs.values():
                    if isinstance(binding, OutputBinding):
                        dependencies[node.id].add(binding.node)
        return dependencies

    def execution_nodes(self) -> list[WorkflowNode]:
        """穩定的拓撲排序；有環或缺少來源時回傳可排序的部分，由檢查阻擋執行。"""
        dependencies = self.dependencies()
        ordered: list[WorkflowNode] = []
        done: set[str] = set()
        while len(done) < len(self.nodes):
            ready = next(
                (
                    node
                    for node in self.nodes
                    if node.id not in done and dependencies[node.id] <= done
                ),
                None,
            )
            if ready is None:
                break
            ordered.append(ready)
            done.add(ready.id)
        return ordered

    def to_json(self) -> dict[str, object]:
        data = self.model_dump(mode="json", by_alias=True, exclude_none=True)
        if self.mode == "serial":
            data.pop("edges")
        return data


@dataclass(frozen=True, slots=True)
class WorkflowProblem:
    """組合場景的一個問題；message 是目前語言的說明。"""

    code: str
    message: str
    node: str | None = None
    input: str | None = None

    def to_json(self) -> dict[str, object]:
        return {"code": self.code, "message": self.message, "node": self.node, "input": self.input}


@dataclass(frozen=True, slots=True)
class InputSource:
    """一個入參的值從哪裡來：場景的預設值、固定值，或前面節點的出參（頁面顯示用）。"""

    kind: Literal["default", "value", "output", "missing", "auto"]
    node: str | None = None
    output: str | None = None
    value: object = None

    def to_json(self) -> dict[str, object]:
        return {"kind": self.kind, "node": self.node, "output": self.output, "value": self.value}


def _problem(
    code: str, node: str | None = None, input_name: str | None = None, **params: object
) -> WorkflowProblem:
    message = catalog(f"dsl.{code}", node=node, input=input_name, **params)
    return WorkflowProblem(code, message, node, input_name)


def parse_workflow(data: object) -> tuple[Workflow | None, list[WorkflowProblem]]:
    """JSON 資料 → 序列；格式不對時回傳 (None, 問題)。"""
    try:
        return Workflow.model_validate(data), []
    except ValidationError as error:
        problems: list[WorkflowProblem] = []
        for details in error.errors():
            context: dict[str, object] = dict(details.get("ctx") or {})
            at = context.pop("at", ())
            location = [
                part for part in details["loc"] if not (isinstance(part, str) and part in _TAGS)
            ]
            if isinstance(at, tuple | list):
                location += [part for part in at if isinstance(part, str | int)]  # pyright: ignore[reportUnknownVariableType]
            error_type = details["type"]
            if "." in error_type:
                message = catalog(f"dsl.{error_type}", **context)
            elif error_type == "missing":
                message = catalog("dsl.missing", field=location[-1] if location else "")
            else:
                message = catalog("dsl.generic", detail=details["msg"])
            field = format_field(location)
            text = catalog("dsl.issue.field", field=field, message=message) if field else message
            problems.append(WorkflowProblem("workflow.invalid", text))
        return None, list(dict.fromkeys(problems))


_TAGS: Final = frozenset({"value", "output", "auto"})
"""綁定寫法在錯誤路徑裡的標籤；顯示路徑時略過（它們剛好也是欄位名稱，只略過標籤那一層）。"""


def compatible(output_type: str, input_type: str) -> bool:
    """上游出參的型別能不能直接當成下游入參：相同型別，或整數給數字。"""
    return output_type == input_type or (output_type == "integer" and input_type == "number")


def plan_workflow(
    workflow: Workflow, scenarios: Mapping[str, Scenario | None]
) -> tuple[Workflow, list[WorkflowProblem]]:
    """固定同名匹配的結果；執行快照不保留會隨編輯而變動的解析規則。"""
    planned = workflow.model_copy(deep=True)
    problems: list[WorkflowProblem] = []
    for node in planned.nodes:
        scenario = scenarios.get(node.id)
        for name, binding in list(node.inputs.items()):
            if not isinstance(binding, AutoBinding):
                continue
            if workflow.mode != "dag":
                problems.append(_problem("workflow.auto_requires_dag", node.id, name))
            if scenario is not None and name not in scenario.inputs:
                problems.append(_problem("workflow.input_unknown", node.id, name))
            spec = scenario.inputs.get(name) if scenario else None
            candidates: set[str] = set()
            for source_id in workflow.dependencies()[node.id]:
                source = scenarios.get(source_id)
                output = source.outputs.get(name) if source else None
                if spec and output and compatible(output.type, spec.type):
                    candidates.add(source_id)
            if len(candidates) > 1:
                problems.append(_problem("workflow.source_ambiguous", node.id, name))
            if len(candidates) == 1:
                node.inputs[name] = OutputBinding(node=next(iter(candidates)), output=name)
            else:
                del node.inputs[name]
    return planned, problems


def check_workflow(
    workflow: Workflow, scenarios: Mapping[str, Scenario | None]
) -> list[WorkflowProblem]:
    """執行前的靜態檢查；scenarios 是「節點代號 → 固定版本的場景」。

    載入不了的場景是 None，不檢查它的契約；場景不存在、封存、版本沒有發布過等
    資料庫裡的狀態由呼叫端另外檢查。
    """
    workflow, problems = plan_workflow(workflow, scenarios)
    if not workflow.nodes:
        problems.append(_problem("workflow.empty"))
    if workflow.mode == "dag":
        ids = {node.id for node in workflow.nodes}
        seen: set[tuple[str, str]] = set()
        for edge in workflow.edges:
            if edge.source not in ids or edge.target not in ids:
                problems.append(
                    _problem("workflow.edge_unknown", source=edge.source, target=edge.target)
                )
            if (edge.source, edge.target) in seen:
                problems.append(
                    _problem("workflow.edge_duplicate", source=edge.source, target=edge.target)
                )
            seen.add((edge.source, edge.target))
        problems += _check_conditions(workflow, scenarios)
        # 缺少端點另行回報；只有完整圖才判斷環。
        deps = workflow.dependencies()
        if all(sources <= ids for sources in deps.values()) and len(
            workflow.execution_nodes()
        ) != len(workflow.nodes):
            problems.append(_problem("workflow.cycle"))
    positions = {node.id: index for index, node in enumerate(workflow.nodes)}
    for index, node in enumerate(workflow.nodes):
        scenario = scenarios.get(node.id)
        if scenario is not None:
            problems += _check_node(
                node, index, scenario, scenarios, positions, workflow.mode == "serial"
            )
    return problems


_SCALAR_TYPES: Final = frozenset({"string", "integer", "number", "boolean"})
"""條件可以比值的出參型別；其他型別（清單、物件、檔案）只能判斷有沒有值。"""


def _matches(value: Scalar, output_type: str) -> bool:
    if output_type == "boolean":
        return isinstance(value, bool)
    if isinstance(value, bool):
        return False
    if output_type == "integer":
        return isinstance(value, int)
    if output_type == "number":
        return isinstance(value, int | float)
    return isinstance(value, str)


def _check_conditions(
    workflow: Workflow, scenarios: Mapping[str, Scenario | None]
) -> list[WorkflowProblem]:
    """條件連線：看的出參要存在、比的值要符合型別；「其他情況」要有對應的條件連線、只能一條。"""
    problems: list[WorkflowProblem] = []
    whens: dict[str, int] = {}
    others: dict[str, int] = {}
    for edge in workflow.edges:
        if edge.when is not None:
            whens[edge.source] = whens.get(edge.source, 0) + 1
        elif edge.otherwise is not None:
            others[edge.source] = others.get(edge.source, 0) + 1
    for edge in workflow.edges:
        if edge.otherwise is not None:
            if not whens.get(edge.source):
                problems.append(
                    _problem("workflow.otherwise_alone", source=edge.source, target=edge.target)
                )
            continue
        condition = edge.when
        scenario = scenarios.get(edge.source)
        if condition is None or scenario is None:
            continue
        spec = scenario.outputs.get(condition.output)
        if spec is None:
            problems.append(
                _problem(
                    "workflow.condition_output_unknown",
                    output=condition.output,
                    source=edge.source,
                    target=edge.target,
                )
            )
        elif condition.operator != "empty" and spec.type not in _SCALAR_TYPES:
            problems.append(
                _problem(
                    "workflow.condition_type_unsupported",
                    output=condition.output,
                    type=spec.type,
                    source=edge.source,
                    target=edge.target,
                )
            )
        else:
            for value in condition.values():
                if not _matches(value, spec.type):
                    problems.append(
                        _problem(
                            "workflow.condition_value_type",
                            output=condition.output,
                            type=spec.type,
                            value=_show(value),
                            source=edge.source,
                            target=edge.target,
                        )
                    )
                    break
    for source, count in others.items():
        if count > 1:
            problems.append(_problem("workflow.otherwise_duplicate", source=source))
    return problems


def _check_node(
    node: WorkflowNode,
    index: int,
    scenario: Scenario,
    scenarios: Mapping[str, Scenario | None],
    positions: Mapping[str, int],
    serial: bool,
) -> list[WorkflowProblem]:
    problems: list[WorkflowProblem] = []
    for name in node.inputs:
        if name not in scenario.inputs:
            problems.append(_problem("workflow.input_unknown", node.id, name))
    for name, spec in scenario.inputs.items():
        binding = node.inputs.get(name)
        if binding is None:
            if spec.default is None:
                problems.append(_problem("workflow.input_missing", node.id, name))
        elif isinstance(binding, ValueBinding):
            # 固定值可以是動態值（例如 {{today}}），執行時才求值；這裡只檢查寫法，不提前求值
            try:
                rules = spec.check_value(binding.value)
            except DynamicValueError as error:
                problems.append(
                    _problem("workflow.value_dynamic", node.id, name, detail=error.message)
                )
                continue
            for rule in rules[:1]:
                problems.append(_problem("workflow.value_invalid", node.id, name, rule=rule))
        elif isinstance(binding, OutputBinding):
            source = binding.node
            if source not in positions:
                problems.append(_problem("workflow.source_unknown", node.id, name, source=source))
                continue
            if serial and positions[source] >= index:
                problems.append(_problem("workflow.source_order", node.id, name, source=source))
                continue
            upstream = scenarios.get(source)
            if upstream is None:
                continue
            output = upstream.outputs.get(binding.output)
            if output is None:
                problems.append(
                    _problem(
                        "workflow.output_unknown",
                        node.id,
                        name,
                        source=source,
                        output=binding.output,
                    )
                )
            elif not compatible(output.type, spec.type):
                problems.append(
                    _problem(
                        "workflow.type_mismatch",
                        node.id,
                        name,
                        source=source,
                        output=binding.output,
                        input_type=spec.type,
                        output_type=output.type,
                    )
                )
    return problems


def input_sources(node: WorkflowNode, scenario: Scenario) -> dict[str, InputSource]:
    """場景每個入參的來源，依場景檔的順序；頁面顯示「recordId ← n1.recordId」用。"""
    sources: dict[str, InputSource] = {}
    for name, spec in scenario.inputs.items():
        binding = node.inputs.get(name)
        if isinstance(binding, AutoBinding):
            sources[name] = InputSource("auto")
        elif isinstance(binding, ValueBinding):
            sources[name] = InputSource("value", value=binding.value)
        elif isinstance(binding, OutputBinding):
            sources[name] = InputSource("output", node=binding.node, output=binding.output)
        elif spec.default is not None:
            sources[name] = InputSource("default", value=spec.default)
        else:
            sources[name] = InputSource("missing")
    return sources


def resolve_inputs(
    node: WorkflowNode, outputs: Mapping[str, Mapping[str, object] | None]
) -> tuple[dict[str, object], list[WorkflowProblem]]:
    """執行到這個節點時的入參：固定值與上游節點的出參（預設值由執行時補上）。

    固定值與預設值裡的動態值（例如 ``{{today}}``）在執行開始時求值；上游的出參先跳脫，原樣使用。

    outputs 是「節點代號 → 通過之後發布的出參」；上游沒有通過（None）或沒有那個出參時回報問題。
    """
    values: dict[str, object] = {}
    problems: list[WorkflowProblem] = []
    for name, binding in node.inputs.items():
        if isinstance(binding, AutoBinding):
            problems.append(_problem("workflow.auto_unresolved", node.id, name))
            continue
        if isinstance(binding, ValueBinding):
            values[name] = binding.value
            continue
        published = outputs.get(binding.node)
        if published is None:
            problems.append(
                _problem("workflow.source_not_passed", node.id, name, source=binding.node)
            )
        elif binding.output not in published:
            problems.append(
                _problem(
                    "workflow.output_missing",
                    node.id,
                    name,
                    source=binding.node,
                    output=binding.output,
                )
            )
        else:
            # 上游的出參是資料：文字裡剛好有 {{ 時也照原樣，不當成動態值
            values[name] = escape(published[binding.output])
    return values, problems


def sequence(nodes: Sequence[WorkflowNode]) -> str:
    """節點的場景代號串成一行，例如 ``ba-001 → ba-002``（清單與標題用）。"""
    return " → ".join(node.scene_id for node in nodes)


# ------------------------------------------------------------------ 條件與排程（2026-11-11）


def _show(value: object) -> str:
    """條件裡的值給人看：字串加引號，其他照 JSON。"""
    return json.dumps(value, ensure_ascii=False)


def _empty(value: object) -> bool:
    return value is None or value == "" or (isinstance(value, list | dict) and not value)


def _same(value: object, expected: Scalar) -> bool:
    """出參的值和條件的值相等：布林只和布林比，數字不分整數與小數，字串要完全相同。"""
    if isinstance(value, bool) or isinstance(expected, bool):
        return isinstance(value, bool) and isinstance(expected, bool) and value is expected
    if isinstance(value, int | float) and isinstance(expected, int | float):
        return value == expected
    return isinstance(value, str) and isinstance(expected, str) and value == expected


def condition_holds(condition: EdgeCondition, outputs: Mapping[str, object] | None) -> bool:
    """來源節點發布的出參符不符合條件；出參沒有時 equals、in 不成立，notEquals 成立。"""
    present = outputs is not None and condition.output in outputs
    value = outputs.get(condition.output) if outputs is not None and present else None
    operator = condition.operator
    if operator == "empty":
        return _empty(value) is bool(condition.empty)
    matched = present and any(_same(value, item) for item in condition.values())
    return not matched if operator == "notEquals" else matched


def condition_text(edge: WorkflowEdge) -> str | None:
    """連線條件的一行說明（目前語言），例如「quantity 等於 12」；一般連線是 None。"""
    if edge.otherwise is not None:
        return catalog("dsl.workflow.condition.otherwise")
    condition = edge.when
    if condition is None:
        return None
    operator = condition.operator
    if operator == "empty":
        key = "empty_true" if condition.empty else "empty_false"
        return catalog(f"dsl.workflow.condition.{key}", output=condition.output)
    if operator == "in":
        values = catalog("dsl.workflow.condition.separator").join(
            _show(item) for item in condition.values()
        )
        return catalog("dsl.workflow.condition.in", output=condition.output, values=values)
    return catalog(
        f"dsl.workflow.condition.{operator}",
        output=condition.output,
        value=_show(condition.values()[0]),
    )


NodeState = Literal["pending", "running", "passed", "failed", "skipped"]
"""排程看的節點狀態：還沒開始、執行中（含還有下一次）、全部次數通過、沒有通過、略過。"""

LinkState = Literal["pending", "taken", "not_taken"]
"""一條依賴：上游還沒結束、走到、沒走到。"""


@dataclass(frozen=True, slots=True)
class Progress:
    """:func:`advance` 的結果。"""

    ready: tuple[str, ...]
    """現在可以開始的節點，依定義順序；同時執行的上限由呼叫端套用。"""
    skipped: frozenset[str]
    """沒有連線走到而略過的節點（含被略過往下傳的）。"""
    links: Mapping[tuple[str, str], LinkState]
    """每條依賴（上游, 下游）目前的狀態，畫面與報告用。"""
    finished: bool
    """每個節點都通過或略過。"""


def advance(
    workflow: Workflow,
    states: Mapping[str, NodeState],
    outputs: Mapping[str, Mapping[str, object] | None],
) -> Progress:
    """從節點目前的狀態算出下一步：可以開始的、略過的、全部結束沒有。

    states 沒列的節點當成還沒開始；outputs 是通過的節點發布的出參（重複的節點是最後一次）。
    節點的上游都通過或略過之後：有一條連線走到就可以開始，一條都沒有就略過；沒有上游的節點
    一開始就可以開始。有上游沒通過時不會走到，交給呼叫端停下。
    """
    links = workflow.links()
    current: dict[str, NodeState] = {
        node.id: states.get(node.id, "pending") for node in workflow.nodes
    }
    whens: dict[str, list[EdgeCondition]] = {}
    for edge in workflow.edges:
        if edge.when is not None:
            whens.setdefault(edge.source, []).append(edge.when)

    def state(source: str, edge: WorkflowEdge | None) -> LinkState:
        upstream = current.get(source)
        if upstream == "skipped":
            return "not_taken"
        if upstream != "passed":
            return "pending"
        if edge is None:
            return "taken"
        published = outputs.get(source)
        if edge.when is not None:
            holds = condition_holds(edge.when, published)
        else:
            holds = not any(condition_holds(item, published) for item in whens.get(source, []))
        return "taken" if holds else "not_taken"

    skipped: set[str] = set()
    changed = True
    while changed:
        changed = False
        for node in workflow.nodes:
            incoming = links[node.id]
            if current[node.id] != "pending" or not incoming:
                continue
            results = [state(source, edge) for source, edge in incoming.items()]
            if "pending" not in results and "taken" not in results:
                current[node.id] = "skipped"
                skipped.add(node.id)
                changed = True
    ready: list[str] = []
    for node in workflow.nodes:
        if current[node.id] != "pending":
            continue
        results = [state(source, edge) for source, edge in links[node.id].items()]
        if not results or ("pending" not in results and "taken" in results):
            ready.append(node.id)
    link_states: dict[tuple[str, str], LinkState] = {
        (source, target): state(source, edge)
        for target, incoming in links.items()
        for source, edge in incoming.items()
    }
    finished = all(value in ("passed", "skipped") for value in current.values())
    return Progress(tuple(ready), frozenset(skipped), link_states, finished)
