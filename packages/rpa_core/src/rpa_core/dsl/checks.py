"""跨欄位、跨步驟的檢查：只在場景的結構都正確之後執行。

- 場景主體：steps 與 script 二擇一。Python 節點（ADR 0020）：相容模式要有 assertion，
  不寫 verify 與 outputs 的 from；運行環境模式不寫 browser、login，assertion 與 verify 二擇一
  （沒有出參時可以都不寫），用 verify 時出參要有 from
- 出參：DSL 場景的每個出參都要有 from，有出參就要有 verify（獨立斷言通過才發布）
- 步驟 id（含區塊裡的步驟）、secrets 名稱、extract 與 download 的 as 不能重複；
  好幾步寫同一個 as 時，每一步都要寫 ``append: true``（M7.1 的 ``extract``、M7.2 的 ``call``）
- goto 的網址以 / 開頭時，要有 browser.baseUrl
- 新分頁（M7b）：page 要是「之前」某一步的 popup（或 M7.1 的 openPage）開出來的分頁；名稱不能
  重複；最外層 closePage 關掉之後不能再用
- 區塊步驟（M7.1）：最多巢狀 MAX_NESTING 層；forEach 的迴圈變數不能用保留的名稱、不能和外層的
  迴圈變數同名
- 上傳（M7c）：upload 的 files 要引用 type: file 的入參；沒有 runtime 的 Python 節點不能有
  file 入參，也不能有 file 出參（ADR 0020）
- ``{{ }}``：以 Jinja2 解析，語法要正確；只能用 inputs、secrets、facts、env，迴圈裡多了迴圈變數
  與 ``loop``，``catch`` 裡多了 ``error``（M7.1）；inputs、secrets 要宣告，facts 要由「之前」
  （場景檔的順序）的 extract 或 download 產生——分支與迴圈裡產生的，之後都算「可能有」；
  寫了入參值的動態值（today、now、random）時，說明要改寫在入參

``{{ }}`` 的求值在 M2 的執行引擎；這裡只做不需要執行就能發現的檢查。
"""

from collections.abc import Iterator, Sequence, Set
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final, cast

from jinja2 import TemplateError, nodes
from jinja2.meta import find_undeclared_variables
from jinja2.sandbox import SandboxedEnvironment

from rpa_core.dsl.dynamic import NAMES as DYNAMIC_NAMES
from rpa_core.dsl.dynamic import dynamic_expression
from rpa_core.dsl.steps import (
    BRANCHES,
    MAX_NESTING,
    ClosePageStep,
    Condition,
    ForEachStep,
    IfStep,
    OpenPageStep,
    RepeatStep,
    Step,
    TryStep,
    branches,
    fact_name,
    upload_input_names,
    walk_steps,
)
from rpa_core.dsl.yaml_loader import DataPath

if TYPE_CHECKING:
    from rpa_core.dsl.scenario import Scenario

__all__ = ["FLOW_VARIABLES", "RENAMED", "VARIABLES", "CrossIssue", "cross_check"]

VARIABLES: Final = ("inputs", "secrets", "facts", "env")
"""``{{ }}`` 可以使用的變數。"""

FLOW_VARIABLES: Final = ("loop", "error")
"""流程控制（M7.1）多出的變數：迴圈裡的 ``loop``、``catch`` 裡的 ``error``。
連同 :data:`VARIABLES` 都不能當迴圈變數的名稱。"""

RENAMED: Final = {"params": "inputs"}
"""改過名的欄位與變數：舊名 → 新名，用來提示正確寫法。"""

_JINJA: Final = SandboxedEnvironment()


@dataclass(frozen=True, slots=True)
class CrossIssue:
    """一個跨欄位的問題；code 對應訊息目錄的 ``dsl.<code>``。"""

    path: DataPath
    code: str
    params: dict[str, object] = field(default_factory=dict[str, object])


def cross_check(scenario: "Scenario") -> list[CrossIssue]:
    """回傳場景中所有跨欄位的問題。"""
    issues: list[CrossIssue] = []
    issues.extend(_body(scenario))
    issues.extend(_duplicate_names(scenario))
    issues.extend(_relative_urls(scenario))
    issues.extend(_tabs(scenario))
    issues.extend(_uploads(scenario))
    issues.extend(_flow(scenario))
    issues.extend(_templates(scenario))
    return issues


# ---------------------------------------------------------------- 場景主體與契約


def _body(scenario: "Scenario") -> Iterator[CrossIssue]:
    if scenario.steps is None and scenario.script is None:
        yield CrossIssue((), "one_of.none", {"fields": "steps, script"})
        return
    if scenario.steps is not None and scenario.script is not None:
        yield CrossIssue(("script",), "one_of.many", {"fields": "steps, script"})
        return
    if scenario.script is not None:
        if scenario.script.uses_runtime:
            yield from _runtime_body(scenario)
            return
        if scenario.script.assertion is None:
            yield CrossIssue(("script",), "script.assertion_required")
        if scenario.verify is not None:
            yield CrossIssue(("verify",), "script.verify_not_allowed")
        for name, spec in scenario.outputs.items():
            if spec.from_ is not None:
                yield CrossIssue(("outputs", name, "from"), "script.output_from_not_allowed")
        return
    yield from _from_and_verify(scenario)


def _runtime_body(scenario: "Scenario") -> Iterator[CrossIssue]:
    """運行環境模式的 Python 節點：不開瀏覽器；斷言是 assertion.py 或 verify。"""
    script = scenario.script
    assert script is not None
    for key in ("browser", "login"):
        if key in scenario.model_fields_set:
            yield CrossIssue((key,), "script.runtime_no_browser", {"field": key})
    if script.assertion is not None and scenario.verify is not None:
        yield CrossIssue(("verify",), "script.assertion_and_verify")
        return
    if script.assertion is not None:
        for name, spec in scenario.outputs.items():
            if spec.from_ is not None:
                yield CrossIssue(("outputs", name, "from"), "script.output_from_not_allowed")
        return
    if scenario.outputs and scenario.verify is None:
        yield CrossIssue(("outputs",), "script.assertion_or_verify")
        return
    yield from _from_and_verify(scenario)


def _from_and_verify(scenario: "Scenario") -> Iterator[CrossIssue]:
    """出參取自事實（from），有出參就要有獨立斷言 verify。"""
    for name, spec in scenario.outputs.items():
        if spec.from_ is None:
            yield CrossIssue(("outputs", name), "output.from_required", {"name": name})
    if scenario.outputs and scenario.verify is None:
        yield CrossIssue(("outputs",), "verify.required_for_outputs")


def _duplicate_names(scenario: "Scenario") -> Iterator[CrossIssue]:
    seen_secrets: dict[str, int] = {}
    for index, name in enumerate(scenario.secrets):
        if name in seen_secrets:
            yield CrossIssue(("secrets", index), "secret.duplicate", {"name": name})
        else:
            seen_secrets[name] = index
    seen_steps: dict[str, DataPath] = {}
    seen_facts: dict[str, tuple[DataPath, bool]] = {}
    for path, step, _ in walk_steps(scenario.steps):
        if step.id in seen_steps:
            first = _number(seen_steps[step.id])
            yield CrossIssue((*path, "id"), "step.duplicate_id", {"id": step.id, "first": first})
        else:
            seen_steps[step.id] = path
        fact = fact_name(step)
        if fact is None:
            continue
        append = getattr(step, "append", None) is True  # extract、call 的累積寫法
        if fact not in seen_facts:
            seen_facts[fact] = (path, append)
            continue
        first_path, first_append = seen_facts[fact]
        if append and first_append:
            continue
        code = "extract.duplicate_as_append" if append or first_append else "extract.duplicate_as"
        yield CrossIssue((*path, "as"), code, {"name": fact, "first": _number(first_path)})


def _number(path: DataPath) -> int:
    """路徑所在的最外層步驟是第幾步（從 1 開始），給訊息用。"""
    return int(path[1]) + 1 if len(path) > 1 and isinstance(path[1], int) else 0


def _relative_urls(scenario: "Scenario") -> Iterator[CrossIssue]:
    if scenario.browser.base_url is not None:
        return
    for path, step, _ in walk_steps(scenario.steps):
        url = getattr(step, "url", None) if step.action in ("goto", "openPage") else None
        if isinstance(url, str) and url.startswith("/"):
            yield CrossIssue((*path, "url"), "url.relative_without_base", {"value": url})


def _tabs(scenario: "Scenario") -> Iterator[CrossIssue]:
    """分頁名稱（M7b 的 popup、M7.1 的 openPage）依場景檔的順序：先開過才能用、不能重複；
    最外層的 closePage 之後不能再用（區塊裡的關閉要執行才知道，執行時才指出）。"""
    opened: dict[str, DataPath] = {}
    closed: set[str] = set()

    def use(path: DataPath, name: str | None) -> Iterator[CrossIssue]:
        if name is None:
            return
        if name not in opened:
            yield CrossIssue(path, "page.undefined", {"name": name})
        elif name in closed:
            yield CrossIssue(path, "page.closed", {"name": name})

    for path, step, depth in walk_steps(scenario.steps):
        yield from use((*path, "page"), step.page)
        for key, condition in _conditions(step):
            yield from use((*path, key, "page"), condition.page)
        if isinstance(step, OpenPageStep):
            name, key = step.as_, "as"
        else:
            popup = getattr(step, "popup", None)
            name, key = (popup, "popup") if isinstance(popup, str) else (None, "")
        if name is not None:
            if name in opened:
                first = _number(opened[name])
                yield CrossIssue((*path, key), "popup.duplicate", {"name": name, "first": first})
            else:
                opened[name] = path
        if isinstance(step, ClosePageStep) and depth == 0 and step.page is not None:
            closed.add(step.page)


def _conditions(step: Step) -> list[tuple[str, Condition]]:
    """區塊步驟的條件：(YAML 的鍵, Condition)。"""
    if isinstance(step, IfStep):
        return [("condition", step.condition)]
    if isinstance(step, RepeatStep):
        found: list[tuple[str, Condition]] = []
        if step.while_ is not None:
            found.append(("while", step.while_))
        if step.until is not None:
            found.append(("until", step.until))
        return found
    return []


def _uploads(scenario: "Scenario") -> Iterator[CrossIssue]:
    # 運行環境模式的 Python 節點從 RPA_INPUT_FILES 拿到檔案路徑（ADR 0020）；相容模式還不行
    if scenario.script is not None and not scenario.script.uses_runtime:
        for name, spec in scenario.inputs.items():
            if spec.type == "file":
                yield CrossIssue(("inputs", name, "type"), "script.file_input", {"name": name})
        for name, spec in scenario.outputs.items():
            if spec.type == "file":
                yield CrossIssue(("outputs", name, "type"), "script.file_output", {"name": name})
    for path, step, _ in walk_steps(scenario.steps):
        if step.action != "upload":
            continue
        for position, name in enumerate(upload_input_names(step.files)):
            spec = scenario.inputs.get(name)
            # 沒有宣告的入參由 {{ }} 的檢查指出，這裡只看型別
            if spec is not None and spec.type != "file":
                yield CrossIssue(
                    (*path, "files", position),
                    "upload.not_file_input",
                    {"name": name, "type": spec.type},
                )


# ---------------------------------------------------------------- 流程控制（M7.1）


def _flow(scenario: "Scenario") -> Iterator[CrossIssue]:
    """區塊的巢狀層數；forEach 的迴圈變數名稱。"""
    yield from _flow_steps(scenario.steps or (), ("steps",), 0, ())


def _flow_steps(
    steps: Sequence[Step], path: DataPath, depth: int, loop_names: tuple[str, ...]
) -> Iterator[CrossIssue]:
    for index, step in enumerate(steps):
        here = (*path, index)
        children = branches(step)
        if not children:
            continue
        if depth + 1 > MAX_NESTING:
            yield CrossIssue((*here, "action"), "block.too_deep", {"max": MAX_NESTING})
            continue
        names = loop_names
        if isinstance(step, ForEachStep):
            name = step.as_
            if name in VARIABLES or name in FLOW_VARIABLES:
                yield CrossIssue((*here, "as"), "forEach.reserved_name", {"name": name})
            elif name in loop_names:
                yield CrossIssue((*here, "as"), "forEach.shadowed_name", {"name": name})
            names = (*loop_names, name)
        for key, inner in children:
            yield from _flow_steps(inner, (*here, key), depth + 1, names)


# ---------------------------------------------------------------- {{ }}


@dataclass(frozen=True, slots=True)
class _Scope:
    inputs: Set[str]
    secrets: Set[str]
    facts_before: Set[str] | None
    """這個位置之前已產生的 facts；None 代表這裡不能用 facts。"""
    all_facts: Set[str] | None
    """整個場景會產生的 facts；None 代表執行才知道（Python 節點），不檢查名稱。"""
    extra: Set[str] = frozenset()
    """這個位置多出的變數（M7.1）：外層 forEach 的迴圈變數、迴圈裡的 loop、catch 裡的 error。"""


def _templates(scenario: "Scenario") -> Iterator[CrossIssue]:
    data = scenario.model_dump(mode="json", by_alias=True, exclude_unset=True)
    inputs, secrets = set(scenario.inputs), set(scenario.secrets)
    # Python 節點寫出哪些事實要執行才知道：不檢查事實的名稱，執行時找不到才報錯
    all_facts: Set[str] | None = (
        None
        if scenario.script is not None
        else {name for _, step, _ in walk_steps(scenario.steps) if (name := fact_name(step))}
    )

    def scope(facts_before: Set[str] | None, extra: Set[str] = frozenset()) -> _Scope:
        return _Scope(inputs, secrets, facts_before, all_facts, frozenset(extra))

    every_fact = all_facts if all_facts is not None else frozenset[str]()

    browser = cast("dict[str, object]", data.get("browser", {}))
    for path, text in _strings(browser, ("browser",)):
        yield from _check_template(path, text, scope(None))
    produced: set[str] = set()

    def visit(steps: Sequence[Step], path: DataPath, extra: frozenset[str]) -> Iterator[CrossIssue]:
        for index, step in enumerate(steps):
            here = (*path, index)
            raw = step.model_dump(mode="json", by_alias=True, exclude_unset=True)
            own = {key: value for key, value in raw.items() if key not in BRANCHES}
            # forEach 的 items 在迴圈外求值，repeat 的 while／until 看得到 loop
            own_extra = extra | {"loop"} if isinstance(step, RepeatStep) else extra
            for field_path, text in _strings(own, here):
                if field_path[len(here) :] != ("name",):
                    yield from _check_template(
                        field_path, text, scope(frozenset(produced), own_extra)
                    )
            fact = fact_name(step)
            if fact is not None:
                produced.add(fact)
            for key, inner in branches(step):
                inner_extra = extra
                if isinstance(step, ForEachStep):
                    inner_extra = extra | {step.as_, "loop"}
                elif isinstance(step, RepeatStep):
                    inner_extra = extra | {"loop"}
                elif isinstance(step, TryStep) and key == "catch":
                    inner_extra = extra | {"error"}
                yield from visit(inner, (*here, key), inner_extra)

    yield from visit(scenario.steps or (), ("steps",), frozenset())
    for index, raw in enumerate(_list(data, "verify")):
        for path, text in _strings(raw, ("verify", index)):
            if path[2:] != ("name",):
                yield from _check_template(path, text, scope(every_fact))
    for name, spec in scenario.outputs.items():
        if spec.from_ is not None:
            yield from _check_template(("outputs", name, "from"), spec.from_, scope(every_fact))


def _list(data: dict[str, object], key: str) -> list[object]:
    value = data.get(key)
    return cast("list[object]", value) if isinstance(value, list) else []


def _strings(value: object, path: DataPath) -> Iterator[tuple[DataPath, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in cast("dict[str, object]", value).items():
            yield from _strings(item, (*path, key))
    elif isinstance(value, list):
        for index, item in enumerate(cast("list[object]", value)):
            yield from _strings(item, (*path, index))


def _check_template(path: DataPath, text: str, scope: _Scope) -> Iterator[CrossIssue]:
    if "{{" not in text and "{%" not in text:
        return
    try:
        tree = _JINJA.parse(text)
        _JINJA.compile(text)
    except TemplateError as error:
        # 入參值的動態值（例如 {{random:10:30}}）寫在步驟裡：Jinja 讀不懂，說明要改寫在入參
        expression = dynamic_expression(text)
        if expression is not None:
            yield CrossIssue(path, "template.dynamic_in_step", {"name": expression})
        else:
            yield _syntax_issue(path, text, error)
        return
    for name in sorted(find_undeclared_variables(tree)):
        if name in scope.extra:
            continue
        if name in RENAMED:
            yield CrossIssue(path, "template.renamed", {"old": name, "new": RENAMED[name]})
        elif name.lower() in DYNAMIC_NAMES:
            expression = dynamic_expression(text) or name
            yield CrossIssue(path, "template.dynamic_in_step", {"name": expression})
        elif name not in VARIABLES:
            choices = ", ".join((*VARIABLES, *sorted(scope.extra)))
            yield CrossIssue(path, "template.unknown_variable", {"name": name, "choices": choices})
    for root, key in _references(tree):
        yield from _check_reference(path, root, key, scope)


def _syntax_issue(path: DataPath, text: str, error: TemplateError) -> CrossIssue:
    stripped = text.replace(" ", "")
    if "{{}}" in stripped:
        return CrossIssue(path, "template.empty")
    if text.count("{{") > text.count("}}"):
        return CrossIssue(path, "template.unclosed")
    return CrossIssue(path, "template.syntax", {"detail": error.message or str(error)})


def _references(tree: nodes.Template) -> Iterator[tuple[str, str]]:
    """``變數.名稱`` 與 ``變數["名稱"]`` 形式的引用，依出現順序、不重複。"""
    found: dict[tuple[str, str], None] = {}
    for node in tree.find_all((nodes.Getattr, nodes.Getitem)):
        target = node.node
        if not isinstance(target, nodes.Name) or target.name not in VARIABLES:
            continue
        if isinstance(node, nodes.Getattr):
            found[(target.name, node.attr)] = None
        elif isinstance(node.arg, nodes.Const) and isinstance(node.arg.value, str):
            found[(target.name, node.arg.value)] = None
    return iter(found)


def _check_reference(path: DataPath, root: str, key: str, scope: _Scope) -> Iterator[CrossIssue]:
    match root:
        case "inputs" if key not in scope.inputs:
            yield CrossIssue(path, "template.undeclared_inputs", {"name": key})
        case "secrets" if key not in scope.secrets:
            yield CrossIssue(path, "template.undeclared_secrets", {"name": key})
        case "facts":
            if scope.facts_before is None:
                yield CrossIssue(path, "template.facts_unavailable")
            elif scope.all_facts is None:
                pass
            elif key not in scope.all_facts:
                yield CrossIssue(path, "template.unknown_fact", {"name": key})
            elif key not in scope.facts_before:
                yield CrossIssue(path, "template.fact_not_yet", {"name": key})
        case _:
            pass
