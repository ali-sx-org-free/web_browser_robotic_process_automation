"""運行回看（M12，ADR 0016）：回看頁需要的資料。

- 影片：執行目錄的 video.json（開始時間、長度、畫面大小）＋ runs 的錄影狀態
  （釘選、刪除、保留到何時）。
- 步驟：result.json（或執行中的 steps.json）每一步的開始、結束時間換算成影片裡的毫秒；再加上
  執行目錄裡場景快照的那一段原文與行號、定位器、填入的值（場景檔的寫法，不是代入後的值）、抽到的事實。
  錄影時每一步做完的截圖（2026-10-29，rpa_runner.stepshots）：``shot`` 是網址、``shotMs`` 是開始拍
  的那一刻在影片裡的毫秒；錄影刪了截圖還在，回看頁照樣顯示步驟的縮圖。
- 斷言與階段：result.json。影片只涵蓋自動化階段，斷言與出參在瀏覽器關閉後才執行。
- 前後：同一個場景的上一次、下一次、上一次沒通過的運行；組合場景的各個節點。
- Python 節點（ADR 0020）沒有錄影：用 rpa_script 記下的步驟當章節（步驟時間軸）。每一步附上腳本
  那幾行（標出那一步的行號）、第幾次、那一步的檔案變化與資料預覽，以及到那一步為止的主控台
  （rpa_script 記下每一步開始、結束時 automation.log 寫到哪裡）；另外有整份主控台的最後幾行與事實。
"""

import bisect
import contextlib
import json
import re
from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import Final, cast
from urllib.parse import quote

from sqlalchemy import select
from sqlalchemy.orm import Session

from rpa_core.dsl import validate_file, validate_text
from rpa_core.dsl.calls import MAX_CALL_DEPTH, call_file
from rpa_core.dsl.steps import BRANCHES, CallStep, walk_steps
from rpa_core.dsl.yaml_loader import Position, YamlLoadError, load_yaml
from rpa_core.dsl.yaml_writer import flow
from rpa_runner.files import (
    AUTOMATION_LOG,
    FACTS,
    PREVIEWS_DIR,
    RESULT,
    SCENARIO_DIR,
    STEP_SHOTS,
    STEPS,
    read_json_or,
)
from rpa_runner.video import clips, read_info
from rpa_server.models import Run
from rpa_server.storage import Storage
from rpa_server.videos import VideoSettings, retention_basis, video_details

__all__ = ["NOT_PASSED", "build_replay", "step_sources", "step_targets"]

NOT_PASSED: Final = ("failed", "timed_out", "cancelled", "needs_login")
_DETAIL_FIELDS: Final = (
    "value",
    "key",
    "option",
    "files",
    "as",
    "text",
    "url",
    "title",
    "count",
    "state",
    "scenario",
    "revision",
    "inputs",
)


def _moment(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo is not None else None
    except ValueError:
        return None


def _offset(moment: datetime | None, start: datetime | None) -> int | None:
    if moment is None or start is None:
        return None
    return round((moment - start).total_seconds() * 1000)


def step_sources(text: str) -> list[tuple[int, str]]:
    """場景檔裡最外層每一步的原文：(第一行的行號, 那一段文字)，依步驟的順序。讀不懂時回傳空清單。"""
    try:
        _, positions = load_yaml(text)
    except YamlLoadError:
        return []
    lines = text.splitlines()
    found: list[tuple[int, str]] = []
    # 用 values 直接查：locate 找不到時會往上找祖先，永遠不是 None
    while (source := _source_at(lines, positions.values, ("steps", len(found)))) is not None:
        found.append(source)
    return found


type _Path = tuple[str | int, ...]


def _source_at(
    lines: Sequence[str], values: Mapping[_Path, Position], path: _Path
) -> tuple[int, str] | None:
    """路徑那一步的原文：從那一步的「-」開始，到縮排回到同一層或更外層為止（區塊的原文包含
    裡面的步驟，M7.1）。"""
    position = values.get(path)
    if position is None:
        return None
    line, dash = position.line, max(0, position.column - 3)
    block = [lines[line - 1]] if 0 < line <= len(lines) else []
    for text_line in lines[line:]:
        stripped = text_line.strip()
        indent = len(text_line) - len(text_line.lstrip())
        if stripped and indent <= dash:
            break
        block.append(text_line)
    while len(block) > 1 and not block[-1].strip():
        block.pop()
    return line, "\n".join(block)


def _snapshot(folder: Path) -> Path | None:
    """執行目錄裡的場景快照（scenario/ 下的場景檔）。"""
    directory = folder / SCENARIO_DIR
    preferred = directory / "scenario.yaml"
    if preferred.is_file():
        return preferred
    candidates = sorted(directory.glob("*.yaml"))
    return candidates[0] if candidates else None


def _definitions(
    snapshot: Path | None,
) -> tuple[dict[_Path, dict[str, object]], dict[_Path, tuple[int, str]]]:
    """快照裡各步驟（含區塊裡的，M7.1）的定義（JSON，不含裡面的步驟）與原文，以路徑為鍵。

    子場景（M7.2）：``call`` 的子場景在快照的 ``calls/`` 裡；它的步驟的紀錄路徑是 call 的路徑
    加上 ``"call"`` 再接子場景裡的位置（例如 ``("steps", 2, "call", 0)``），原文取自子場景檔。
    """
    steps: dict[_Path, dict[str, object]] = {}
    sources: dict[_Path, tuple[int, str]] = {}
    if snapshot is not None:
        _collect(snapshot, snapshot.parent, None, steps, sources, 0)
    return steps, sources


def _collect(
    file: Path,
    base: Path,
    prefix: _Path | None,
    steps: dict[_Path, dict[str, object]],
    sources: dict[_Path, tuple[int, str]],
    depth: int,
) -> None:
    """把一個場景檔的步驟加進 ``steps``、``sources``；``prefix`` 是外層 call 的路徑加 ``"call"``
    （最外層的場景是 None），``base`` 是快照的資料夾。"""
    text = ""
    with contextlib.suppress(OSError, UnicodeDecodeError):
        text = file.read_text(encoding="utf-8-sig")
    # 子場景檔旁邊沒有 calls/（都平放在快照的 calls/ 裡）：只校驗文字，子場景由下面接著走
    found = validate_file(file) if prefix is None else validate_text(text)
    scenario = found.scenario
    values: Mapping[_Path, Position] = {}
    with contextlib.suppress(YamlLoadError):
        values = load_yaml(text)[1].values
    lines = text.splitlines()
    for path, step, _ in walk_steps(scenario.steps if scenario is not None else None):
        key = path if prefix is None else (*prefix, *path[1:])
        dumped = step.model_dump(mode="json", by_alias=True, exclude_unset=True)
        steps[key] = {name: value for name, value in dumped.items() if name not in BRANCHES}
        source = _source_at(lines, values, path)
        if source is not None:
            sources[key] = source
        if isinstance(step, CallStep) and depth < MAX_CALL_DEPTH:
            inner = base / call_file(step.scenario, step.revision)
            _collect(inner, base, (*key, "call"), steps, sources, depth + 1)


def _record_path(record: Mapping[str, object], index: int) -> _Path:
    """紀錄對應的定義路徑：M7.1 起的紀錄有 path；之前的紀錄一步一筆，依順序對應。"""
    raw = record.get("path")
    if isinstance(raw, list) and raw:
        return tuple(cast("list[str | int]", raw))
    return ("steps", index)


def _describe(definition: Mapping[str, object]) -> tuple[str | None, str | None]:
    """(定位器或網址, 其他重點)：例如 ``{ label: 標題 }`` 與 ``value: '{{ inputs.title }}'``。"""
    # upload 用 trigger（點了才開選擇檔案視窗的元素）或 dropzone（拖放區）定位（M7c）
    target = next(
        (definition[key] for key in ("target", "trigger", "dropzone") if key in definition), None
    )
    where = flow(target) if target is not None else None
    if where is None and isinstance(definition.get("url"), str):
        where = str(definition["url"])
    details = [
        f"{name}: {flow(definition[name])}"
        for name in _DETAIL_FIELDS
        if name in definition and not (name == "url" and where == definition[name])
    ]
    return where, "  ".join(details) or None


def step_targets(folder: Path, records: Sequence[Mapping[str, object]]) -> list[str | None]:
    """每一筆步驟紀錄在場景快照裡的定位器或網址（場景檔的寫法），依紀錄的順序；組合運行的報告用。"""
    definitions, _ = _definitions(_snapshot(folder))
    return [
        _describe(definitions.get(_record_path(record, index), {}))[0]
        for index, record in enumerate(records)
    ]


_PYTHON_SOURCE: Final = re.compile(
    r"(?P<file>(?:[A-Za-z0-9_][A-Za-z0-9_.-]*/)*[A-Za-z0-9_][A-Za-z0-9_.-]*\.py):(?P<line>\d+)"
)
"""rpa_script 記的步驟位置（``automation.py:12``）。"""
_CONTEXT_LINES: Final = 4
"""Python 節點的步驟顯示那一行前後各幾行（後面多一倍）。"""
_PREVIEW_ROWS: Final = 10
"""回看裡每份資料預覽顯示幾列。"""
_PREVIEW: Final = re.compile(rf"{PREVIEWS_DIR}/\d{{3,4}}\.json")
_CONSOLE_LINES: Final = 200
"""Python 節點的主控台顯示最後幾行。"""
_STEP_CONSOLE_LINES: Final = 40
"""每一步顯示到那一步為止的最後幾行主控台。"""
_CONSOLE_LINE_CHARS: Final = 500
_CONSOLE_MAX_BYTES: Final = 16 * 1024 * 1024
"""比這大的 automation.log 不逐步對應（只顯示整份的最後幾行）。"""


def _script_lines(folder: Path, name: str, cache: dict[str, list[str]]) -> list[str]:
    """場景快照裡的腳本（每一行）；不在快照裡或讀不到時是空的。"""
    if name not in cache:
        root = (folder / SCENARIO_DIR).resolve()
        path = (root / name).resolve()
        lines: list[str] = []
        if path.is_relative_to(root) and path.is_file():
            with contextlib.suppress(OSError, UnicodeDecodeError):
                lines = path.read_text(encoding="utf-8").splitlines()
        cache[name] = lines
    return cache[name]


def _preview(folder: Path, relative: object) -> dict[str, object] | None:
    if not isinstance(relative, str) or not _PREVIEW.fullmatch(relative):
        return None
    data = read_json_or(folder / relative, None)
    if not isinstance(data, dict):
        return None
    preview = dict(cast("dict[str, object]", data))
    rows = preview.get("rows")
    if isinstance(rows, list):
        preview["rows"] = cast("list[object]", rows)[:_PREVIEW_ROWS]
    text = preview.get("text")
    if isinstance(text, str):
        preview["text"] = text[:4000]
    return preview


class _Console:
    """Python 節點的主控台（automation.log），依位元組位置找出每一步的輸出。

    用到時才讀（DSL 場景的回看不需要）。
    """

    def __init__(self, folder: Path) -> None:
        self._path = folder / AUTOMATION_LOG
        self._loaded = False
        self.exists = False
        self.size = 0
        self.mapped = False
        self._breaks: list[int] = []
        self.lines: list[str] = []

    def _load(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        try:
            data = self._path.read_bytes()
        except OSError:
            return
        self.exists = True
        self.size = len(data)
        self.mapped = self.size <= _CONSOLE_MAX_BYTES
        text = data.decode("utf-8", errors="replace")
        self.lines = [line.removesuffix("\r") for line in text.split("\n")]
        if self.mapped:
            self._breaks = [match.start() for match in re.finditer(b"\n", data)]

    def tail(self) -> str | None:
        """整份的最後幾行。"""
        self._load()
        if not self.exists:
            return None
        lines = self.lines[:-1] if self.lines and not self.lines[-1] else self.lines
        return "\n".join(lines[-_CONSOLE_LINES:])

    def step(self, span: object) -> dict[str, object] | None:
        """到這一步為止的最後幾行；``own`` 是這一步自己寫的那幾行（從 1 起算，含頭尾）。

        ``span`` 是 rpa_script 記的 ``[開始, 結束]``（位元組）；遠端 Worker 上傳的執行目錄不完全
        可信，不合理的值不採用。
        """
        self._load()
        if not self.mapped or not isinstance(span, list):
            return None
        bounds = cast("list[object]", span)
        if len(bounds) != 2 or not all(type(value) is int for value in bounds):
            return None
        start, end = cast("list[int]", bounds)
        if not 0 <= start <= end <= self.size:
            return None
        first = bisect.bisect_left(self._breaks, start)
        upto = bisect.bisect_left(self._breaks, end - 1) + 1 if end > 0 else 0
        shown = max(0, upto - _STEP_CONSOLE_LINES)
        return {
            "line": shown + 1,
            "text": "\n".join(line[:_CONSOLE_LINE_CHARS] for line in self.lines[shown:upto]),
            "own": [first + 1, upto] if end > start else None,
        }


def _python_step(
    folder: Path,
    record: Mapping[str, object],
    cache: dict[str, list[str]],
    console: _Console,
) -> dict[str, object]:
    """Python 節點的一步（rpa_script）：腳本那幾行、第幾次、檔案變化、資料預覽、主控台。"""
    details: dict[str, object] = {
        "files": [],
        "previews": [],
        "console": console.step(record.get("console")),
    }
    source = record.get("source")
    match = _PYTHON_SOURCE.fullmatch(source) if isinstance(source, str) else None
    if isinstance(source, str):
        details["target"] = source
    if match is not None:
        lines = _script_lines(folder, match["file"], cache)
        focus = int(match["line"])
        if 1 <= focus <= len(lines):
            start = max(1, focus - _CONTEXT_LINES)
            end = min(len(lines), focus + _CONTEXT_LINES * 2)
            details.update(
                line=start,
                focusLine=focus,
                source="\n".join(lines[start - 1 : end]),
                editFile=match["file"],
            )
    occurrence = record.get("occurrence")
    if isinstance(occurrence, int) and occurrence > 1:
        details["occurrence"] = occurrence
    changes = record.get("files")
    if isinstance(changes, dict):
        details["changes"] = {
            kind: [str(item) for item in cast("list[object]", items)]
            for kind, items in cast("dict[str, object]", changes).items()
            if kind in ("added", "changed", "removed") and isinstance(items, list)
        }
    previews = record.get("previews")
    if isinstance(previews, list):
        found = [_preview(folder, item) for item in cast("list[object]", previews)]
        details["previews"] = [item for item in found if item is not None]
    return details


def _chapters(steps: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    """步驟時間軸的章節：最外層的步驟，寬度依耗時（太短的至少佔總長的 1/40）。"""
    top = [step for step in steps if step.get("parent") is None]
    durations = [
        value if isinstance(value := step.get("durationMs"), int) and value > 0 else 0
        for step in top
    ]
    floor = max(sum(durations), 1) / 40
    return [
        {
            "index": step.get("index"),
            "label": step.get("name") or step.get("id"),
            "status": step.get("status"),
            "durationMs": step.get("durationMs"),
            "weight": round(max(duration, floor), 1),
        }
        for step, duration in zip(top, durations, strict=True)
    ]


_SHOT: Final = re.compile(rf"{STEP_SHOTS}/\d{{3,4}}\.jpg")
"""steps.json 的 shot 只接受 Runner 產生的檔名（遠端 Worker 上傳的執行目錄不完全可信）。"""


def _shot(folder: Path, run_id: str, value: object) -> str | None:
    if not isinstance(value, str) or not _SHOT.fullmatch(value) or not (folder / value).is_file():
        return None
    return f"/runs/{run_id}/files/{value}"


def _steps(
    folder: Path,
    run_id: str,
    result: Mapping[str, object] | None,
    start: datetime | None,
    console: _Console,
) -> list[dict[str, object]]:
    raw = result.get("steps") if result is not None else None
    if not isinstance(raw, list):
        raw = read_json_or(folder / STEPS, [])
    records = [
        cast("dict[str, object]", item)
        for item in cast("list[object]", raw if isinstance(raw, list) else [])
        if isinstance(item, dict)
    ]
    definitions, sources = _definitions(_snapshot(folder))
    facts_raw = read_json_or(folder / FACTS, {})
    facts = cast("dict[str, object]", facts_raw) if isinstance(facts_raw, dict) else {}
    steps: list[dict[str, object]] = []
    scripts: dict[str, list[str]] = {}
    for index, record in enumerate(records):
        if record.get("action") == "python":
            steps.append(
                {
                    "index": index + 1,
                    "id": record.get("id"),
                    "name": record.get("name"),
                    "action": "python",
                    "status": record.get("status"),
                    "durationMs": record.get("durationMs"),
                    "error": record.get("error"),
                    "startedAt": record.get("startedAt"),
                    "endedAt": record.get("endedAt"),
                    "startMs": None,
                    "endMs": None,
                    "shot": None,
                    "shotMs": None,
                    "parent": record.get("parent"),
                    "pageId": "page-1",
                    "notes": [],
                    "artifacts": [],
                    **_python_step(folder, record, scripts, console),
                }
            )
            continue
        path = _record_path(record, index)
        definition = definitions.get(path, {})
        line, text = sources.get(path, (None, None))
        where, detail = _describe(definition)
        # 子場景裡的步驟（M7.2）的事實是子場景自己的，不在這次執行的 facts.json 裡
        name = None if "call" in path[::2] else definition.get("as")
        steps.append(
            {
                "index": index + 1,
                "id": record.get("id"),
                "name": record.get("name"),
                "action": record.get("action"),
                "status": record.get("status"),
                "durationMs": record.get("durationMs"),
                "error": record.get("error"),
                "url": record.get("url"),
                "pageId": record.get("pageId")
                or ("missing:" + str(definition["page"]) if definition.get("page") else "page-1"),
                "createdPageId": record.get("createdPageId"),
                "startedAt": record.get("startedAt"),
                "endedAt": record.get("endedAt"),
                "startMs": _offset(_moment(record.get("startedAt")), start),
                "endMs": _offset(_moment(record.get("endedAt")), start),
                "shot": _shot(folder, run_id, record.get("shot")),
                "shotMs": _offset(_moment(record.get("shotAt")), start),
                "target": where,
                "detail": detail,
                "fact": facts.get(name) if isinstance(name, str) and name in facts else None,
                "hasFact": isinstance(name, str) and name in facts,
                "line": line,
                "source": text,
                "artifacts": record.get("artifacts") or [],
                # 上傳的檔案（網頁看到的檔名）與提醒，例如攔下的選擇檔案視窗（M7c）
                "files": record.get("files") or [],
                "notes": record.get("notes") or [],
                # 流程控制（M7.1）：巢狀、第幾輪、分支、重試與失敗後繼續
                "path": list(path),
                "parent": record.get("parent"),
                "iteration": record.get("iteration"),
                "attempts": record.get("attempts"),
                "handled": record.get("handled"),
                "condition": record.get("condition"),
                "branch": record.get("branch"),
                "iterations": record.get("iterations"),
                "caught": record.get("caught"),
                # 子場景（M7.2）：call 呼叫的場景版本、它的獨立斷言與出參名稱
                "call": record.get("call"),
            }
        )
    _add_depths(steps)
    return steps


def _add_depths(steps: list[dict[str, object]]) -> None:
    """每一步在第幾層（depth）：DSL 的 parent 是紀錄編號，Python 節點的是外層步驟的 id。"""
    ids: dict[str, int] = {}
    for index, step in enumerate(steps):
        parent = step.get("parent")
        outer: int | None = None
        if isinstance(parent, int) and not isinstance(parent, bool) and 1 <= parent <= index:
            outer = parent - 1
        elif isinstance(parent, str) and parent in ids:
            outer = ids[parent]
        step["depth"] = cast("int", steps[outer]["depth"]) + 1 if outer is not None else 0
        ids.setdefault(str(step.get("id")), index)


def _neighbors(session: Session, run: Run) -> dict[str, str | None]:
    """同一個場景的上一次、下一次、上一次沒通過的運行。"""
    same = Run.scene_id == run.scene_id
    earlier = (Run.created_at < run.created_at) | (
        (Run.created_at == run.created_at) & (Run.id < run.id)
    )
    later = (Run.created_at > run.created_at) | (
        (Run.created_at == run.created_at) & (Run.id > run.id)
    )
    newest_first = (Run.created_at.desc(), Run.id.desc())
    previous = session.scalar(select(Run.id).where(same, earlier).order_by(*newest_first).limit(1))
    following = session.scalar(
        select(Run.id).where(same, later).order_by(Run.created_at, Run.id).limit(1)
    )
    failed = session.scalar(
        select(Run.id)
        .where(same, earlier, Run.status.in_(NOT_PASSED))
        .order_by(*newest_first)
        .limit(1)
    )
    return {"previous": previous, "next": following, "previousFailed": failed}


def _workflow(session: Session, run: Run) -> dict[str, object] | None:
    """組合場景的序列執行：各節點的運行（依開始的順序）。"""
    if run.workflow_run_id is None:
        return None
    nodes = session.scalars(
        select(Run).where(Run.workflow_run_id == run.workflow_run_id).order_by(Run.created_at)
    ).all()
    return {
        "id": run.workflow_run_id,
        "nodes": [
            {
                "nodeId": node.node_id,
                "runId": node.id,
                "sceneId": node.scene_id,
                "status": node.status,
                "video": node.video_seconds is not None and node.video_deleted_at is None,
            }
            for node in nodes
        ],
    }


def build_replay(
    session: Session, storage: Storage, run: Run, settings: VideoSettings
) -> dict[str, object]:
    """回看頁的資料（API 與頁面共用）。"""
    folder = storage.run_dir(run.id)
    result_raw = read_json_or(folder / RESULT, None)
    result = cast("dict[str, object]", result_raw) if isinstance(result_raw, dict) else None
    info = read_info(folder) or {}
    state = video_details(run, settings, retention_basis(session, run))
    playable = state is not None and state.get("url") is not None and info.get("file") is not None
    recordings = clips(info)
    origins = [
        value for clip in recordings if (value := _moment(clip.get("startedAt"))) is not None
    ]
    start = min(origins) if origins and playable else None
    entries: list[dict[str, object]] = []
    for clip in recordings:
        entries.append(
            {
                **clip,
                "startMs": _offset(_moment(clip.get("startedAt")), start),
                "url": f"/runs/{run.id}/files/{clip['file']}"
                if playable and (folder / str(clip["file"])).is_file()
                else None,
            }
        )
    video: dict[str, object] | None = None
    if state is not None:
        video = {
            **state,
            "playable": playable,
            "startedAt": start.isoformat(timespec="milliseconds").replace("+00:00", "Z")
            if start
            else None,
            "clips": entries,
            "durationMs": info.get("durationMs"),
            "width": info.get("width"),
            "height": info.get("height"),
            "complete": info.get("complete"),
            "repaired": info.get("repaired"),
        }
    elif info:
        # 有錄但沒存下來（例如還沒開瀏覽器就取消）：頁面照樣顯示原因，不能因為少了 url 出錯
        video = {"playable": False, "url": None, "error": info.get("error")}
    console = _Console(folder)
    steps = _steps(folder, run.id, result, start, console)
    if video is not None and playable:
        # 開頁步驟可能比第一格畫面更早；保留這段等待，不把它壓到零點。
        moments = [
            moment for step in steps if (moment := _moment(step.get("startedAt"))) is not None
        ]
        if start is not None and moments and min(moments) < start:
            earlier = min(moments)
            shift = round((start - earlier).total_seconds() * 1000)
            video["startedAt"] = earlier.isoformat(timespec="milliseconds").replace("+00:00", "Z")
            for item in entries:
                if isinstance(item.get("startMs"), int):
                    item["startMs"] = cast("int", item["startMs"]) + shift
            for step in steps:
                for key in ("startMs", "endMs", "shotMs"):
                    if isinstance(step.get(key), int):
                        step[key] = cast("int", step[key]) + shift
        ends = [
            float(cast("int", c["startMs"])) + float(cast("int | float", c["durationMs"]))
            for c in entries
            if isinstance(c.get("startMs"), int) and isinstance(c.get("durationMs"), int | float)
        ]
        ends.extend(
            float(cast("int", s["endMs"])) for s in steps if isinstance(s.get("endMs"), int)
        )
        video["durationMs"] = round(max(ends, default=0))
        page_ids = {
            c.get("pageId") for c in entries if c.get("url") and c.get("startMs") is not None
        }
        video["missingPages"] = any(
            s.get("pageId") not in page_ids for s in steps if s.get("startedAt")
        )
    # 讓執行停下的那一步：沒有被接住、不是區塊本身（M7.1）；都沒有時退回第一個失敗的
    unhandled = [step for step in steps if step["status"] == "failed" and not step.get("handled")]
    leaf = next(
        (
            step
            for step in unhandled
            if step.get("action") not in ("if", "forEach", "repeat", "try", "call")
        ),
        None,
    )
    chosen = leaf or next(iter(unhandled), None)
    failed = chosen["index"] if chosen is not None else None
    python = any(step.get("action") == "python" for step in steps)
    if python:
        base = f"/scenes/{run.scene_id}/edit?revision={run.revision_number}&file="
        for step in steps:
            name = step.pop("editFile", None)
            if isinstance(name, str):
                step["editUrl"] = base + quote(name)
    facts_raw = read_json_or(folder / FACTS, None) if python else None
    return {
        "kind": (result or {}).get("kind"),
        "python": {
            "console": console.tail(),
            "facts": facts_raw if isinstance(facts_raw, dict) else None,
            "chapters": _chapters(steps),
        }
        if python
        else None,
        "video": video,
        "steps": steps,
        "failedStep": failed,
        "checks": cast("Sequence[object]", (result or {}).get("checks") or []),
        "stages": cast("Sequence[object]", (result or {}).get("stages") or []),
        "error": run.error,
        "neighbors": _neighbors(session, run),
        "workflow": _workflow(session, run),
        "editUrl": f"/scenes/{run.scene_id}/edit?revision={run.revision_number}&file=scenario.yaml",
    }


def dumps(data: Mapping[str, object]) -> str:
    """嵌進頁面的 JSON：``</`` 換成 ``<\\/``，不會提前結束 ``<script>``。"""
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
