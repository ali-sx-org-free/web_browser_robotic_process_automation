"""子場景的檔案入參與出參（M7.2 收尾，2026-11-14）。

``call`` 給子場景 ``type: file`` 入參的值一律是 ``{{ }}``（rpa_core.dsl.calls 檢查），執行時是：

- **呼叫場景自己的檔案入參**（``{{ inputs.名稱 }}``，或多檔入參的其中一個、迴圈變數）：表達式
  看到的是 ``{"name", "size", "sha256"}``，依 sha256 與檔名找回呼叫場景準備好的檔案；
- **共用工作資料夾裡的檔案** ``{"workspace": …}``：download 步驟的事實，或前一個子場景的檔案出參。

子場景的檔案不另外複製：upload 直接用這些檔案（檔名就是網頁看到的檔名）。子場景的
``type: file`` 出參要是共用工作資料夾裡的檔案，值換成 ``{"workspace", "name", "size", "sha256"}``，
呼叫場景可以再交給下一個子場景，或當成自己的檔案出參（出參階段照常複製進 ``outputs/``）。
"""

from collections.abc import Mapping, MutableMapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

from rpa_core.dsl import Scenario
from rpa_core.dsl.files import (
    MAX_FILE_BYTES,
    accepts,
    file_meta,
    format_size,
    inside_folders,
    is_workspace_ref,
)
from rpa_runner.contract import Problem
from rpa_runner.i18n import t
from rpa_runner.outputfiles import workspace_file

__all__ = ["CalleeFiles", "callee_file_outputs", "callee_files", "caller_index"]

FileIndex = dict[tuple[str, str], Path]
"""(sha256, 檔名) → 呼叫場景準備好的檔案。"""


@dataclass(slots=True)
class CalleeFiles:
    """準備好給子場景的檔案入參。"""

    meta: dict[str, object] = field(default_factory=dict[str, object])
    """入參名稱 → ``{"name", "size", "sha256"}``（多檔時是清單）：子場景的 ``inputs``。"""
    paths: dict[str, list[Path]] = field(default_factory=dict[str, list[Path]])
    """入參名稱 → 檔案：子場景 upload 步驟用。"""
    problems: list[Problem] = field(default_factory=list[Problem])


def caller_index(inputs: Mapping[str, object], files: Mapping[str, Sequence[Path]]) -> FileIndex:
    """呼叫場景的檔案入參：表達式看到的說明（``inputs``）與準備好的檔案（``files``）依序對應。"""
    index: FileIndex = {}
    for name, paths in files.items():
        shown = inputs.get(name)
        metas = cast("list[object]", shown) if isinstance(shown, list) else [shown]
        for meta, path in zip(metas, paths, strict=False):
            if isinstance(meta, Mapping):
                data = cast("Mapping[str, object]", meta)
                digest, label = data.get("sha256"), data.get("name")
                if isinstance(digest, str) and isinstance(label, str):
                    index[digest, label] = path
    return index


def _items(value: object) -> list[object]:
    """給的值 → 一個個檔案；清單裡的清單（多檔入參整個交進來）攤平一層。"""
    if not isinstance(value, list):
        return [value]
    found: list[object] = []
    for item in cast("list[object]", value):
        found.extend(cast("list[object]", item) if isinstance(item, list) else [item])
    return found


def _locate(item: object, index: FileIndex, workspace: Path | None) -> Path | None:
    if not isinstance(item, Mapping):
        return None
    data = cast("Mapping[str, object]", item)
    ref = data.get("workspace")
    if isinstance(ref, str):
        if workspace is None or not is_workspace_ref(ref):
            return None
        path = workspace / ref
        return path if inside_folders(path, [workspace]) and path.is_file() else None
    digest, label = data.get("sha256"), data.get("name")
    if isinstance(digest, str) and isinstance(label, str):
        return index.get((digest, label))
    return None


def _label(item: object) -> str:
    if isinstance(item, Mapping):
        data = cast("Mapping[str, object]", item)
        for key in ("name", "workspace"):
            text = data.get(key)
            if isinstance(text, str):
                return text
    return str(cast("object", item))


def callee_files(
    callee: Scenario, given: Mapping[str, object], index: FileIndex, workspace: Path | None
) -> CalleeFiles:
    """把 ``call`` 給子場景檔案入參的值（已經代入過 ``{{ }}``）換成檔案，檢查類型與大小。"""
    prepared = CalleeFiles()
    for name, spec in callee.inputs.items():
        if spec.type != "file":
            continue
        if name not in given:
            prepared.problems.append(Problem(name, t("contract.input_missing", name=name)))
            continue
        items = _items(given[name])
        if not spec.multiple and len(items) != 1:
            prepared.problems.append(
                Problem(name, t("browser.call_file_single", name=name, count=len(items)))
            )
            continue
        limit = min(spec.max_bytes or MAX_FILE_BYTES, MAX_FILE_BYTES)
        metas: list[object] = []
        paths: list[Path] = []
        for item in items:
            path = _locate(item, index, workspace)
            if path is None:
                prepared.problems.append(
                    Problem(name, t("browser.call_file_unknown", name=name, file=_label(item)))
                )
                continue
            size = path.stat().st_size
            if size > limit:
                prepared.problems.append(
                    Problem(
                        name,
                        t(
                            "contract.file_too_large",
                            name=name,
                            file=path.name,
                            size=format_size(size),
                            limit=format_size(limit),
                        ),
                    )
                )
                continue
            if not accepts(spec.accept, path.name):
                prepared.problems.append(
                    Problem(
                        name,
                        t(
                            "contract.file_type",
                            name=name,
                            file=path.name,
                            accept=", ".join(spec.accept or ()),
                        ),
                    )
                )
                continue
            metas.append(file_meta(path, path.name).to_json())
            paths.append(path)
        prepared.meta[name] = metas if spec.multiple else (metas[0] if metas else None)
        prepared.paths[name] = paths
    return prepared


def callee_file_outputs(
    callee: Scenario, outputs: MutableMapping[str, object], workspace: Path | None
) -> list[Problem]:
    """子場景的 ``type: file`` 出參 → 共用工作資料夾裡的檔案說明；有問題時不改 ``outputs``。"""
    problems: list[Problem] = []
    found: dict[str, object] = {}
    for name, spec in callee.outputs.items():
        if spec.type != "file" or name not in outputs:
            continue
        if workspace is None:
            problems.append(Problem(name, t("contract.file_output_outside", name=name)))
            continue
        path, problem = workspace_file(outputs[name], workspace)
        if path is None:
            problems.append(Problem(name, t(problem or "contract.file_output_value", name=name)))
            continue
        ref = path.relative_to(workspace.resolve()).as_posix()
        found[name] = {"workspace": ref, **file_meta(path, path.name).to_json()}
    if not problems:
        outputs.update(found)
    return problems
