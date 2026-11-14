"""子場景（M7.2，ADR 0023）：``call`` 步驟引用的場景版本放在哪裡、怎麼解析與檢查。

``call`` 在同一個瀏覽器裡接著執行另一個場景的固定版本。那個版本的場景檔跟著呼叫場景的版本
存放，所以呼叫場景自己就能執行（遠端 Worker、錄製端、``rpa run`` 都不用另外找子場景），
子場景之後出新版本、封存或不見都不影響已經存好的呼叫場景::

    <版本目錄>/
      scenario.yaml                 呼叫場景
      calls/<子場景代號>/<版本>.yaml   子場景那個版本的場景檔，原樣複製

- 子場景自己再呼叫的場景也平放在同一個 ``calls/``（不巢狀）。
- 這些檔案算進呼叫場景的內容雜湊（:func:`rpa_core.dsl.sources.scenario_sources`）；沒有用到
  ``call`` 的場景沒有這個資料夾，雜湊和以前相同。
- 管理 Portal 存檔時由伺服器從發布過的版本複製進來；手寫的場景資料夾（例如
  ``scenarios/examples/call/``）自己放。

限制（第一版）：子場景要是 DSL 場景；登入角色和呼叫場景相同或不需要登入；用到的 Secrets
呼叫場景也要宣告；不能有 ``type: file`` 的入參與出參；最多 :data:`MAX_CALL_DEPTH` 層、
:data:`MAX_CALLS` 個不同的子場景版本；不能繞回自己。

這個模組只讀檔與檢查，不依賴瀏覽器；執行在 rpa_runner.browser。
"""

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final, cast

from pydantic import ValidationError

from rpa_core.dsl.checks import CrossIssue
from rpa_core.dsl.dynamic import DynamicValueError
from rpa_core.dsl.features import data_features, scenario_features
from rpa_core.dsl.issues import (
    format_issue,
    issue_from_cross,
    issue_from_yaml_error,
    issues_from_validation_error,
)
from rpa_core.dsl.scenario import CROSS_ISSUES_CONTEXT, Scenario
from rpa_core.dsl.steps import CallStep, Step, walk_steps
from rpa_core.dsl.yaml_loader import DataPath, YamlLoadError, load_yaml

__all__ = [
    "CALLS_DIR",
    "MAX_CALLS",
    "MAX_CALL_DEPTH",
    "CallKey",
    "CallTable",
    "call_file",
    "call_files",
    "call_refs",
    "check_calls",
    "closure_features",
    "data_call_refs",
    "is_call_path",
    "load_calls",
]

CALLS_DIR: Final = "calls"
"""版本目錄裡放子場景的資料夾。"""
MAX_CALL_DEPTH: Final = 3
"""子場景最多幾層：呼叫場景 → 子場景 → 子場景 → 子場景。"""
MAX_CALLS: Final = 10
"""一個場景（含子場景自己呼叫的）最多用到幾個不同的子場景版本。"""

type CallKey = tuple[str, int]
"""(子場景代號, 版本)。"""
type CallTable = Mapping[CallKey, Scenario]
"""解析好的子場景：呼叫場景用到的每一個（含子場景自己呼叫的）。"""


def call_file(scenario_id: str, revision: int) -> str:
    """子場景那個版本的場景檔，相對於呼叫場景的版本目錄。"""
    return f"{CALLS_DIR}/{scenario_id}/{revision}.yaml"


def is_call_path(path: str) -> bool:
    """相對路徑在 ``calls/`` 底下（伺服器管理的檔案，使用者不直接編輯）。"""
    return path == CALLS_DIR or path.startswith(f"{CALLS_DIR}/")


def call_refs(steps: Sequence[Step] | None) -> list[tuple[DataPath, CallStep]]:
    """步驟裡（含區塊裡）的 ``call``：(路徑, 步驟)，依場景檔的順序。"""
    return [(path, step) for path, step, _ in walk_steps(steps) if isinstance(step, CallStep)]


def data_call_refs(data: object) -> list[CallKey]:
    """還沒校驗的場景資料（YAML 讀出來的 dict）裡的 ``call``：(代號, 版本)，不重複、依出現順序。

    給伺服器在存檔前決定要帶入哪些子場景；寫法不對的略過，校驗另外會指出。
    """
    found: dict[CallKey, None] = {}
    steps = cast("dict[str, object]", data).get("steps") if isinstance(data, dict) else None
    pending: list[object] = [steps]
    while pending:
        item = pending.pop(0)
        if isinstance(item, list):
            pending = [*cast("list[object]", item), *pending]
        elif isinstance(item, dict):
            values = cast("dict[str, object]", item)
            scenario, revision = values.get("scenario"), values.get("revision")
            if (
                values.get("action") == "call"
                and isinstance(scenario, str)
                and isinstance(revision, int)
                and not isinstance(revision, bool)
            ):
                found.setdefault((scenario, revision))
            pending = [
                *(value for value in values.values() if isinstance(value, list)),
                *pending,
            ]
    return list(found)


@dataclass(frozen=True, slots=True)
class _Loaded:
    scenario: Scenario | None
    problem: tuple[str, dict[str, object]] | None = None
    """讀不到或沒通過校驗：(訊息代碼, 參數)。"""


def _read(base_dir: Path, key: CallKey) -> _Loaded:
    """讀一個子場景的場景檔並校驗（不含它自己的子場景，那由 :func:`_resolve` 接著走）。"""
    scenario_id, revision = key
    relative = call_file(scenario_id, revision)
    params: dict[str, object] = {"scenario": scenario_id, "revision": revision, "path": relative}
    try:
        text = (base_dir / relative).read_bytes().decode("utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return _Loaded(None, ("call.missing", params))
    try:
        data, source = load_yaml(text)
    except YamlLoadError as error:
        detail = format_issue(issue_from_yaml_error(error))
        return _Loaded(None, ("call.invalid", {**params, "detail": detail}))
    cross: list[CrossIssue] = []
    try:
        scenario = Scenario.model_validate(data, context={CROSS_ISSUES_CONTEXT: cross})
    except ValidationError as error:
        issues = issues_from_validation_error(error, data, source)
        detail = format_issue(issues[0]) if issues else str(error)
        return _Loaded(None, ("call.invalid", {**params, "detail": detail}))
    if cross:
        detail = format_issue(issue_from_cross(cross[0], data, source))
        return _Loaded(None, ("call.invalid", {**params, "detail": detail}))
    if scenario.id != scenario_id:
        return _Loaded(None, ("call.id_mismatch", {**params, "actual": scenario.id}))
    return _Loaded(scenario)


def load_calls(
    base_dir: Path, scenario: Scenario
) -> tuple[dict[CallKey, Scenario], list[CrossIssue]]:
    """解析場景用到的全部子場景（含子場景自己呼叫的），並回傳所有問題。

    ``base_dir`` 是呼叫場景的場景檔所在的資料夾。問題的路徑指向呼叫場景裡的那個 ``call``
    （子場景裡面的問題記在引到它的最外層 ``call`` 上）。
    """
    table: dict[CallKey, Scenario] = {}
    loaded: dict[CallKey, _Loaded] = {}
    issues: list[CrossIssue] = []
    for path, step in call_refs(scenario.steps):
        issues.extend(_resolve(base_dir, scenario, step, path, (), table, loaded, scenario.id))
    if len(table) > MAX_CALLS:
        first = call_refs(scenario.steps)[0][0]
        issues.append(
            CrossIssue(
                (*first, "scenario"), "call.too_many", {"count": len(table), "max": MAX_CALLS}
            )
        )
    return table, issues


def check_calls(base_dir: Path, scenario: Scenario) -> list[CrossIssue]:
    """場景的 ``call`` 有沒有問題（:func:`load_calls` 的問題部分）。"""
    return load_calls(base_dir, scenario)[1]


def _resolve(
    base_dir: Path,
    caller: Scenario,
    step: CallStep,
    path: DataPath,
    stack: tuple[CallKey, ...],
    table: dict[CallKey, Scenario],
    loaded: dict[CallKey, _Loaded],
    root_id: str,
) -> Iterator[CrossIssue]:
    """檢查一個 ``call``，再往它的子場景裡走。``path`` 是最外層那個 ``call`` 的路徑，
    ``stack`` 是從最外層走到這裡經過的子場景，``root_id`` 是最外層呼叫場景的代號。"""
    key: CallKey = (step.scenario, step.revision)
    names: dict[str, object] = {"scenario": step.scenario, "revision": step.revision}
    # 繞回自己：不管哪個版本，經過的場景都不能再呼叫一次
    if step.scenario == root_id or step.scenario in {scenario_id for scenario_id, _ in stack}:
        yield CrossIssue((*path, "scenario"), "call.cycle", dict(names))
        return
    if len(stack) + 1 > MAX_CALL_DEPTH:
        yield CrossIssue((*path, "scenario"), "call.too_deep", {**names, "max": MAX_CALL_DEPTH})
        return
    if key not in loaded:
        loaded[key] = _read(base_dir, key)
    found = loaded[key]
    if found.scenario is None:
        code, params = found.problem or ("call.missing", dict(names))
        yield CrossIssue((*path, "scenario"), code, params)
        return
    callee = found.scenario
    table[key] = callee
    yield from _contract(caller, callee, step, path, nested=bool(stack))
    for _, inner in call_refs(callee.steps):
        yield from _resolve(base_dir, callee, inner, path, (*stack, key), table, loaded, root_id)


def _contract(
    caller: Scenario, callee: Scenario, step: CallStep, path: DataPath, *, nested: bool
) -> Iterator[CrossIssue]:
    """子場景能不能被這個場景呼叫，以及 ``inputs``、``as`` 對不對得上它的契約。"""
    names: dict[str, object] = {"scenario": step.scenario, "revision": step.revision}
    at = (*path, "scenario")
    if callee.script is not None:
        yield CrossIssue(at, "call.script", dict(names))
        return
    role = callee.login.role if callee.login is not None else None
    caller_role = caller.login.role if caller.login is not None else None
    if role is not None and role != caller_role:
        yield CrossIssue(at, "call.login", {**names, "role": role, "caller": caller_role or "—"})
    missing = [name for name in callee.secrets if name not in caller.secrets]
    if missing:
        yield CrossIssue(at, "call.secrets", {**names, "names": ", ".join(missing)})
    files = [name for name, spec in callee.inputs.items() if spec.type == "file"]
    files += [name for name, spec in callee.outputs.items() if spec.type == "file"]
    if files:
        yield CrossIssue(at, "call.files", {**names, "names": ", ".join(files)})
    given = step.inputs or {}
    # 子場景自己呼叫的子場景出了問題時，路徑只能指到最外層的 call，欄位就不往下指
    for name, value in given.items():
        spec = callee.inputs.get(name)
        field: DataPath = at if nested else (*path, "inputs", name)
        if spec is None:
            yield CrossIssue(field, "call.input_unknown", {**names, "name": name})
            continue
        if isinstance(value, str) and "{{" in value:
            continue  # 執行時代入後才知道
        try:
            rules = spec.check_value(value)
        except DynamicValueError as error:  # pragma: no cover - 沒有 {{ 不會走到動態值
            rules = [error.message]
        for rule in rules:
            yield CrossIssue(field, "call.input_invalid", {**names, "name": name, "rule": rule})
    for name, spec in callee.inputs.items():
        if name not in given and spec.default is None:
            yield CrossIssue(
                at if nested else (*path, "inputs"),
                "call.input_missing",
                {**names, "name": name},
            )
    if step.as_ is not None and not callee.outputs:
        yield CrossIssue(at if nested else (*path, "as"), "call.no_outputs", dict(names))


def call_files(base_dir: Path, scenario: Scenario) -> list[str]:
    """場景用到的子場景檔（相對於 ``base_dir``），依路徑排序；讀不到的照樣列出。

    走訪時只讀 YAML 找 ``call``，不做完整校驗：雜湊、快照與「有沒有多餘的檔案」都用它，
    子場景有問題時由 :func:`check_calls` 指出。
    """
    found: dict[CallKey, None] = {}
    pending: list[CallKey] = [
        (step.scenario, step.revision) for _, step in call_refs(scenario.steps)
    ]
    while pending and len(found) <= MAX_CALLS * 4:
        key = pending.pop(0)
        if key in found:
            continue
        found[key] = None
        try:
            text = (base_dir / call_file(*key)).read_bytes().decode("utf-8-sig")
            data, _ = load_yaml(text)
        except (OSError, UnicodeDecodeError, YamlLoadError):
            continue
        pending.extend(data_call_refs(data))
    return sorted(call_file(*key) for key in found)


def closure_features(scenario: Scenario, calls: CallTable) -> frozenset[str]:
    """場景連同它的子場景用到的擴充（派工前比對裝置看不看得懂）。"""
    found = set(scenario_features(scenario))
    for callee in calls.values():
        found |= scenario_features(callee)
    if calls:
        found |= data_features({"action": "call"})
    return frozenset(found)
