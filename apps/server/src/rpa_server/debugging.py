"""調試工作階段（M4）：一個場景版本、一個瀏覽器，一次執行一個步驟。

- 子程序 ``python -m rpa_runner.debug`` 握有瀏覽器；有圖形介面時視窗開在這台電腦上（有頭模式），
  沒有時用無頭模式，每一步之後的截圖顯示在頁面上。
- 每個場景同一時間最多一個工作階段；閒置 15 分鐘自動關閉；伺服器關閉時全部關閉。
- **有副作用的步驟**（點擊、填寫、選擇、勾選、按鍵）執行過一次後，再執行要使用者明確確認，
  「執行到這一步」只會執行還沒執行過的步驟，不會自動重複任何步驟。
- 修改 YAML 存成新版本後可以換到新版本繼續（瀏覽器與 facts 保留，執行過的步驟依 id 對應）。
  換版本的命令直接帶場景內容與入參，不帶伺服器上的路徑：子程序在錄製端時讀不到伺服器的檔案
  （v0.6.3 修正；錄製端的 App 要支援 ``debugInlineLoad``）。
- 只支援 DSL 場景；Python 腳本場景請用驗證執行。
- 在錄製端調試時，場景用到錄製端的 App 看不懂的 DSL 擴充（例如 iframe 的 frame，M7a）就不開始，
  直接說明要更新 RPA 錄製端（見 :meth:`rpa_server.devices.RecorderHub.check`）。
- 對外 Agent API（M14）開的工作階段記下用戶端（``client_id``）；讀頁面結構（``snapshot``）要錄製端的
  App 支援 ``debugSnapshot``。
"""

import json
import shutil
import threading
import time
import uuid
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Final, cast

from rpa_core.dsl import Scenario, Step
from rpa_core.dsl.calls import is_call_path
from rpa_core.dsl.dynamic import escape
from rpa_core.dsl.features import input_features
from rpa_core.dsl.steps import CallStep, branches
from rpa_core.dsl.yaml_writer import flow
from rpa_core.i18n import Locale, use_locale
from rpa_runner.browser import DEFAULT_STEP_TIMEOUT_MS
from rpa_runner.commands import module_command
from rpa_runner.contract import prepare_inputs
from rpa_runner.debug import COMMAND_SECONDS
from rpa_runner.run import ENV_STORAGE_STATE
from rpa_server.context import Via, use_recorder
from rpa_server.domain import now
from rpa_server.errors import ServiceError, conflict, invalid, not_found
from rpa_server.i18n import t
from rpa_server.processes import ChildProcess, Launch, Lines, child_env, launch, send, stop
from rpa_server.roles import parse_locator
from rpa_server.storage import SCENARIO_FILE, Storage

if TYPE_CHECKING:
    from rpa_server.devices import RecorderHub
    from rpa_server.roles import RoleService
    from rpa_server.services import Services

__all__ = [
    "IDLE_SECONDS",
    "INLINE_LOAD",
    "SIDE_EFFECTS",
    "SNAPSHOT",
    "DebugManager",
    "DebugSession",
]

IDLE_SECONDS: Final = 15 * 60.0
"""閒置這麼久就關閉工作階段。"""
START_SECONDS: Final = 180.0
"""等瀏覽器啟動最多這麼久（第一次用 Firefox 要建立預熱設定檔）。"""
SIDE_EFFECTS: Final = frozenset({"click", "fill", "select", "check", "press", "call"})
"""有副作用的動作：執行過之後再執行要確認。子場景（call，M7.2）裡多半有點擊與填寫，
整個算有副作用。"""
ENGINES: Final = ("chromium", "firefox")
_ACTIVE: Final = frozenset({"starting", "ready", "busy"})
SNAPSHOT: Final = "debugSnapshot"
"""讀頁面結構：錄製端的 App 要回報支援這個功能（M14，見 rpa_worker.environment.CAPABILITIES）。"""
CALLS_FILE: Final = "calls.json"
"""工作階段資料夾裡交給子程序的子場景檔（M7.2）：``calls/…`` 的相對路徑 → 內容。"""
INLINE_LOAD: Final = "debugInlineLoad"
"""換版本的 ``load`` 命令直接帶場景內容（v0.6.3）：在錄製端調試時，那台的 App 要支援。"""
_SNAPSHOT_KEYS: Final = ("url", "title", "tabs", "frames", "fields", "aria", "truncated")


@dataclass(slots=True)
class StepState:
    index: int
    """最外層的第幾步（從 0 起）；區塊裡的步驟（M7.1）是它所在的最外層步驟。"""
    id: str
    action: str
    name: str | None
    target: str | None
    status: str = "pending"
    """pending（還沒執行）、passed、failed。"""
    runs: int = 0
    error: str | None = None
    duration_ms: int = 0
    files: list[str] = field(default_factory=list[str])
    """upload 交給網頁的檔名（M7c）。"""
    notes: list[str] = field(default_factory=list[str])
    """提醒，例如攔下的選擇檔案視窗（M7c）。"""
    path: tuple[str | int, ...] = ()
    """在場景檔裡的位置（M7.1），例如 ``("steps", 2, "steps", 0)``。"""
    key: str | None = None
    """區塊裡的步驟在哪個分支（then、else、steps、catch）；最外層的是 None。"""
    depth: int = 0
    children: list["StepState"] = field(default_factory=list["StepState"])
    """區塊裡的步驟（M7.1），依場景檔的順序。"""
    iterations: int | None = None
    branch: str | None = None
    handled: str | None = None

    @property
    def side_effect(self) -> bool:
        """有副作用：再執行一次要確認。區塊裡有任何有副作用的步驟，整塊就算有（M7.1）。"""
        return self.action in SIDE_EFFECTS or any(child.side_effect for child in self.children)

    @property
    def loop(self) -> bool:
        return self.action in ("forEach", "repeat")

    @property
    def path_key(self) -> str:
        """迴圈的目前項用的鍵：``steps/2``、``steps/2/then/0``。"""
        return "/".join(str(part) for part in self.path)

    def walk(self) -> Iterator["StepState"]:
        yield self
        for child in self.children:
            yield from child.walk()

    def to_json(self) -> dict[str, object]:
        return {
            "index": self.index,
            "id": self.id,
            "action": self.action,
            "name": self.name,
            "target": self.target,
            "status": self.status,
            "runs": self.runs,
            "error": self.error,
            "durationMs": self.duration_ms,
            "sideEffect": self.side_effect,
            "files": self.files,
            "notes": self.notes,
            "path": list(self.path),
            "key": self.key,
            "depth": self.depth,
            "loop": self.loop,
            "iterations": self.iterations,
            "branch": self.branch,
            "handled": self.handled,
            "children": [child.to_json() for child in self.children],
        }


def _state(
    step: Step, index: int, path: tuple[str | int, ...], key: str | None, depth: int
) -> StepState:
    # upload 可以用 trigger（點了才開視窗的元素）或 dropzone（拖放區）定位（M7c）
    target = next(
        (
            found
            for name in ("target", "trigger", "dropzone")
            if (found := getattr(step, name, None)) is not None
        ),
        None,
    )
    text = (
        flow(target.model_dump(mode="json", by_alias=True, exclude_none=True)) if target else None
    )
    if text is None and step.action in ("goto", "openPage"):
        text = cast("str | None", getattr(step, "url", None))
    if isinstance(step, CallStep):
        text = f"{step.scenario} v{step.revision}"  # 子場景整個一起執行（M7.2）
    state = StepState(index, step.id, step.action, step.name, text, path=path, key=key, depth=depth)
    for branch, inner in branches(step):
        for position, child in enumerate(inner):
            state.children.append(
                _state(child, index, (*path, branch, position), branch, depth + 1)
            )
    return state


def _steps(scenario: Scenario) -> list[StepState]:
    return [
        _state(step, index, ("steps", index), None, 0)
        for index, step in enumerate(scenario.steps or [])
    ]


def _find(states: list[StepState], path: tuple[str | int, ...]) -> StepState | None:
    for state in states:
        for found in state.walk():
            if found.path == path:
                return found
    return None


def _apply(state: StepState, record: Mapping[str, object]) -> None:
    """把一筆步驟紀錄寫進狀態；迴圈裡同一步的好幾筆依序寫入，最後一筆為準、執行次數累加。"""
    state.runs += 1
    status = record.get("status")
    state.status = "passed" if status == "passed" else "failed"
    state.error = cast("str | None", record.get("error"))
    state.duration_ms = int(cast("int", record.get("durationMs") or 0))
    state.files += [str(item) for item in cast("list[object]", record.get("files") or [])]
    state.notes += [str(item) for item in cast("list[object]", record.get("notes") or [])]
    iterations = record.get("iterations")
    state.iterations = iterations if isinstance(iterations, int) else None
    branch = record.get("branch")
    state.branch = branch if isinstance(branch, str) else None
    handled = record.get("handled")
    state.handled = handled if isinstance(handled, str) else None


def _timeout(scenario: Scenario, step: Step) -> float:
    """等子程序回覆多久：這一步的逾時加上餘裕；區塊（M7.1）裡面可能有很多步，用整個命令的上限。"""
    if branches(step) or isinstance(step, CallStep):
        return COMMAND_SECONDS + 30
    milliseconds = step.timeout or scenario.defaults.timeout or DEFAULT_STEP_TIMEOUT_MS
    return milliseconds / 1000 + 30


@dataclass(slots=True)
class DebugSession:
    id: str
    scene_id: str
    revision: int
    engine: str
    headless: bool
    base_url: str | None
    inputs: dict[str, object]
    folder: Path
    scenario: Scenario
    steps: list[StepState]
    process: ChildProcess | None = None
    lines: Lines | None = None
    device: str | None = None
    """瀏覽器開在哪台錄製端（M10.2）；伺服器這台是 None。"""
    launcher: Launch | None = None
    status: str = "starting"
    """starting → ready ⇄ busy → closed／failed。"""
    message: str | None = None
    next_index: int = 0
    url: str | None = None
    title: str | None = None
    screenshot: str | None = None
    facts: dict[str, object] = field(default_factory=dict[str, object])
    located: dict[str, object] | None = None
    role: str | None = None
    client_id: str | None = None
    """由哪個 API 用戶端開的（M14）；Portal 開的是 None。"""
    created_at: datetime = field(default_factory=now)
    last_used: float = field(default_factory=time.monotonic)
    lock: threading.Lock = field(default_factory=threading.Lock)
    counter: int = 0
    files: list[tuple[str, Path]] = field(default_factory=list[tuple[str, Path]])
    """檔案入參（M7c）：在工作階段資料夾以原始檔名準備好的檔案，給子程序的 --file。"""
    choices: dict[str, int] = field(default_factory=dict[str, int])
    """迴圈的目前項（M7.1）：迴圈步驟的路徑（``steps/2``）→ 第幾項（從 0 起）；單獨執行迴圈裡的
    一步時，迴圈變數用這一項。"""
    file_inputs: dict[str, object] = field(default_factory=dict[str, object])
    """檔案入參原本的值（上傳檔、附件或路徑）；inputs 裡的是名稱、大小、sha256，
    重新開始時用這個。"""

    @property
    def active(self) -> bool:
        return self.status in _ACTIVE

    def to_json(self) -> dict[str, object]:
        return {
            "id": self.id,
            "sceneId": self.scene_id,
            "revision": self.revision,
            "engine": self.engine,
            "headless": self.headless,
            "baseUrl": self.base_url,
            "inputs": self.inputs,
            "status": self.status,
            "message": self.message,
            "nextIndex": self.next_index,
            "url": self.url,
            "title": self.title,
            "screenshotUrl": (
                f"/debug/{self.id}/files/{self.screenshot}" if self.screenshot else None
            ),
            "facts": self.facts,
            "located": self.located,
            "role": self.role,
            "deviceId": self.device,
            "clientId": self.client_id,
            "steps": [step.to_json() for step in self.steps],
            "choices": self.choices,
            "createdAt": self.created_at.isoformat(timespec="seconds"),
            "idleSeconds": int(time.monotonic() - self.last_used),
        }


class DebugManager:
    def __init__(
        self,
        storage: Storage,
        services: "Services",
        roles: "RoleService",
        *,
        display: bool,
        locale: Locale,
        launcher: Launch | None = None,
        idle_seconds: float = IDLE_SECONDS,
        hosts: "RecorderHub | None" = None,
    ) -> None:
        self.storage = storage
        self.services = services
        self.roles = roles
        self.display = display
        self.locale: Locale = locale
        self.launcher: Launch = launcher or launch
        self.hosts = hosts
        """錄製端（M10.2）：請求透過錄製端時，瀏覽器開在那台。"""
        self.idle_seconds = idle_seconds
        self._lock = threading.Lock()
        self._sessions: dict[str, DebugSession] = {}
        self._stopping = threading.Event()
        self._reaper: threading.Thread | None = None

    # ------------------------------------------------------------ 查詢

    def get(self, session_id: str) -> DebugSession:
        with self._lock:
            session = self._sessions.get(session_id)
        if session is None:
            raise not_found("debug_not_found", t("error.debug_not_found", id=session_id))
        return session

    def for_scene(self, scene_id: str) -> DebugSession | None:
        """這個場景進行中的工作階段。"""
        with self._lock:
            return next(
                (s for s in self._sessions.values() if s.scene_id == scene_id and s.active), None
            )

    def sessions(self) -> list[DebugSession]:
        with self._lock:
            return [session for session in self._sessions.values() if session.active]

    # ------------------------------------------------------------ 開始

    def start(
        self,
        scene_id: str,
        *,
        revision: int | None = None,
        inputs: Mapping[str, object] | None = None,
        engine: str | None = None,
        headless: bool | None = None,
        base_url: str | None = None,
        restart: bool = False,
        client_id: str | None = None,
    ) -> DebugSession:
        scene = self.services.get_scene(scene_id)
        if scene.archived:
            raise conflict("scene_archived", t("error.scene_archived", id=scene_id))
        existing = self.for_scene(scene_id)
        via = self.hosts.current() if self.hosts is not None else None
        here = via.id if via is not None else None
        if existing is not None and not restart and existing.device == here:
            return existing  # 進行中的工作階段在別台時，關掉它、在操作的這台重新開始
        number = revision or scene.latest_number
        scenario = self.services.revision_scenario(scene_id, number)
        if scenario.script is not None:
            raise invalid("debug_script", t("error.debug_script"))
        display = self.display if via is None or self.hosts is None else self.hosts.display(via)
        if headless is None:
            headless = not display
        elif not headless and not display:
            raise invalid("display_unavailable", t("error.display_unavailable"))
        engine = engine or scenario.browser.engine
        if engine not in ENGINES:
            raise invalid("engine_invalid", t("error.role_engine_invalid", engine=engine))
        launcher = self.launcher
        if via is not None and self.hosts is not None:
            self.hosts.check(
                via,
                engine=engine,
                headed=not headless,
                features=self.services.revision_features(scene_id, number) | input_features(inputs),
            )
            launcher = self.hosts.launcher(via)
        if inputs is None:
            inputs = {n: s.default for n, s in scenario.inputs.items() if s.default is not None}
        resolved, problems = prepare_inputs(scenario, inputs)
        if problems:
            raise invalid(
                "inputs_invalid",
                t("error.inputs_invalid", count=len(problems)),
                problems=[{"name": item.name, "message": item.message} for item in problems],
            )
        # 檔案入參（M7c）：上傳檔在不在、大小與類型（同執行）
        uploads = self.services.uploads
        inputs = uploads.require(scenario, inputs, self.storage.attachments(scene_id, number))
        if existing is not None:
            self.close(existing.id)
        session_id = uuid.uuid4().hex[:12]
        folder = self.storage.debug_dir(session_id)
        folder.mkdir(parents=True)
        files = self.services.revision_files(scene_id, number)
        (folder / SCENARIO_FILE).write_text(files[SCENARIO_FILE], encoding="utf-8")
        # 子場景（M7.2）：calls/ 的檔案包成一個 JSON 檔交給子程序（在錄製端時跟著命令送過去）
        calls = {path: text for path, text in files.items() if is_call_path(path)}
        if calls:
            (folder / CALLS_FILE).write_text(
                json.dumps(calls, ensure_ascii=False), encoding="utf-8"
            )
        prepared = uploads.prepare(
            scenario,
            inputs,
            self.storage.revision_dir(scene_id, number),
            folder / "input-files",
        )
        uploads.touch(inputs.values())
        raw = {
            name: spec.default for name, spec in scenario.inputs.items() if spec.default is not None
        }
        raw.update(inputs)
        (folder / "input.json").write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
        session = DebugSession(
            id=session_id,
            scene_id=scene_id,
            revision=number,
            engine=engine,
            headless=headless,
            base_url=(base_url or "").strip() or scene.base_url,
            inputs=resolved,
            folder=folder,
            scenario=scenario,
            steps=_steps(scenario),
            role=scenario.login.role if scenario.login is not None else None,
            device=via.id if via is not None else None,
            launcher=launcher,
            client_id=client_id,
            files=prepared,
            file_inputs={
                name: value
                for name, value in inputs.items()
                if name in scenario.inputs and scenario.inputs[name].type == "file"
            },
        )
        with self._lock:
            self._sessions[session_id] = session
        try:
            self._launch(session)
        except ServiceError:
            with self._lock:
                self._sessions.pop(session_id, None)
            raise
        return session

    def _launch(self, session: DebugSession) -> None:
        scenario = session.scenario
        command = module_command(
            "rpa_runner.debug",
            [
                "--scenario",
                str(session.folder / SCENARIO_FILE),
                "--input",
                str(session.folder / "input.json"),
                "--out",
                str(session.folder),
                "--engine",
                session.engine,
            ],
        )
        command += [] if session.headless else ["--headed"]
        command += ["--base-url", session.base_url] if session.base_url else []
        for name, path in session.files:  # 檔案入參（M7c）
            command += ["--file", name, str(path)]
        if (session.folder / CALLS_FILE).is_file():  # 子場景（M7.2）
            command += ["--calls", str(session.folder / CALLS_FILE)]
        extra = self.roles.secret_values(scenario.secrets)
        if session.role is not None:
            state = self.storage.role_state(session.role)
            if state.is_file():
                command += ["--storage-state", str(state)]
                extra[ENV_STORAGE_STATE] = str(state)
        launcher = session.launcher or self.launcher
        env = child_env(self.locale, extra)
        process = launcher(command, env=env, log=session.folder / "debug.log")
        session.process = process
        session.lines = Lines(process)
        threading.Thread(target=self._wait_ready, args=(session,), daemon=True).start()

    def _wait_ready(self, session: DebugSession) -> None:
        lines = session.lines
        if lines is None:
            return
        with use_locale(self.locale):
            try:
                line = lines.get(timeout=START_SECONDS)
            except TimeoutError:
                line = None
            event = _parse(line)
            if event.get("event") == "ready":
                resolved = event.get("inputs")
                if isinstance(resolved, dict):
                    session.inputs = cast("dict[str, object]", resolved)
                    (session.folder / "input.json").write_text(
                        json.dumps(resolved, ensure_ascii=False), encoding="utf-8"
                    )
                session.status = "ready"
                session.last_used = time.monotonic()
                return
            detail = str(event.get("error") or _tail(session.folder / "debug.log"))
            session.status = "failed"
            session.message = t("debug.start_failed", detail=detail)
            if session.process is not None:
                stop(session.process, grace=1)

    # ------------------------------------------------------------ 命令

    def _command(
        self, session: DebugSession, timeout: float, **command: object
    ) -> dict[str, object]:
        """送一個命令並等回覆；同一個工作階段一次只處理一個命令。"""
        if session.status == "starting":
            raise conflict("debug_starting", t("error.debug_starting"))
        if not session.active:
            raise conflict("debug_closed", t("error.debug_closed", id=session.id))
        if not session.lock.acquire(blocking=False):
            raise conflict("debug_busy", t("error.debug_busy"))
        try:
            session.status = "busy"
            session.counter += 1
            process, lines = session.process, session.lines
            if (
                process is None
                or lines is None
                or not send(process, json.dumps({"id": session.counter, **command}))
            ):
                self._crashed(session)
                raise conflict("debug_closed", t("error.debug_closed", id=session.id))
            while True:
                try:
                    line = lines.get(timeout=timeout)
                except TimeoutError:
                    self._crashed(session, t("debug.no_reply"))
                    raise conflict("debug_closed", t("error.debug_closed", id=session.id)) from None
                if line is None:
                    self._crashed(session)
                    raise conflict("debug_closed", t("error.debug_closed", id=session.id))
                reply = _parse(line)
                if reply.get("id") == session.counter:
                    break
            if reply.get("url") is not None:
                session.url = cast("str", reply.get("url"))
                session.title = cast("str | None", reply.get("title"))
            if reply.get("screenshot"):
                session.screenshot = cast("str", reply["screenshot"])
            facts = reply.get("facts")
            if isinstance(facts, dict):
                session.facts = cast("dict[str, object]", facts)
            return reply
        finally:
            if session.status == "busy":
                session.status = "ready"
            session.last_used = time.monotonic()
            session.lock.release()

    def _crashed(self, session: DebugSession, detail: str | None = None) -> None:
        session.status = "failed"
        session.message = t("debug.crashed", detail=detail or _tail(session.folder / "debug.log"))

    def run_step(
        self,
        session_id: str,
        index: int,
        *,
        force: bool = False,
        path: Sequence[str | int] | None = None,
        choices: Mapping[str, int] | None = None,
    ) -> DebugSession:
        """執行一步；有副作用而且執行過的步驟要 force（使用者確認）才再執行。

        區塊整塊執行（M7.1）；``path`` 單獨執行區塊裡的一步，``choices`` 是迴圈的目前項
        （記在工作階段，之後沿用）。
        """
        session = self.get(session_id)
        if not 0 <= index < len(session.steps):
            raise invalid("step_not_found", t("error.step_not_found", number=index + 1))
        state = session.steps[index]
        target = tuple(path) if path is not None else state.path
        if path is not None:
            found = _find(session.steps, target)
            if found is None or found.index != index:
                raise invalid("step_not_found", t("error.step_not_found", number=index + 1))
            state = found
        if choices:
            session.choices.update({key: max(0, value) for key, value in choices.items()})
        if state.runs and state.side_effect and not force:
            raise conflict(
                "confirm_required",
                t("error.debug_confirm", number=index + 1, id=state.id),
                step=index,
            )
        self._execute(session, index, None if path is None else target)
        return session

    def _execute(
        self, session: DebugSession, index: int, path: tuple[str | int, ...] | None = None
    ) -> bool:
        steps = session.scenario.steps or []
        command: dict[str, object] = {"cmd": "step", "index": index}
        state = session.steps[index]
        if path is not None:
            command = {"cmd": "step", "path": list(path), "choices": session.choices}
            state = _find(session.steps, path) or state
        reply = self._command(session, _timeout(session.scenario, steps[index]), **command)
        if not reply.get("ok"):
            state.status = "failed"
            state.error = str(reply.get("error") or "")
            return False
        record = cast("dict[str, object]", reply.get("record") or {})
        records = [
            cast("dict[str, object]", item)
            for item in cast("list[object]", reply.get("records") or [record])
            if isinstance(item, dict)
        ]
        # 區塊裡的步驟（M7.1）：每一筆紀錄依 path 找到它的狀態；迴圈裡同一步會有好幾筆
        touched: set[int] = set()
        for item in records or [record]:
            raw_path = item.get("path")
            found = (
                _find(session.steps, tuple(cast("list[str | int]", raw_path)))
                if isinstance(raw_path, list) and raw_path
                else state
            )
            if found is None:
                continue
            if id(found) not in touched:
                found.files, found.notes = [], []
                touched.add(id(found))
            _apply(found, item)
        if path is None:
            session.next_index = index + 1
        return state.status == "passed"

    def run_to(self, session_id: str, index: int) -> DebugSession:
        """從下一個還沒執行的步驟執行到第 index 步；遇到失敗就停。已經執行過的步驟不會再執行。"""
        session = self.get(session_id)
        if not 0 <= index < len(session.steps):
            raise invalid("step_not_found", t("error.step_not_found", number=index + 1))
        if index < session.next_index:
            raise conflict("already_executed", t("error.debug_already_executed", number=index + 1))
        for current in range(session.next_index, index + 1):
            if session.steps[current].runs:
                continue
            if not self._execute(session, current):
                break
        return session

    def locate(self, session_id: str, text: object) -> DebugSession:
        session = self.get(session_id)
        locator = parse_locator(text)
        reply = self._command(session, 60, cmd="locate", locator=locator)
        session.located = {
            "locator": flow(locator),
            "ok": bool(reply.get("ok")),
            "count": reply.get("count"),
            "matches": reply.get("matches") or [],
            "error": reply.get("error"),
        }
        return session

    def snapshot(self, session_id: str, within: object = None) -> dict[str, object]:
        """目前頁面的結構（M14）：無障礙樹、表單欄位、iframe 與分頁；``within`` 只看一部分。

        在錄製端調試時，那台的 App 要支援（舊版說明要更新 RPA 錄製端）。
        """
        session = self.get(session_id)
        if session.device is not None and self.hosts is not None:
            name = self.hosts.get_recorder(session.device).name
            self.hosts.require(Via(session.device, name), SNAPSHOT)
        command: dict[str, object] = {"cmd": "snapshot"}
        if within is not None:
            command["within"] = parse_locator(within)
        reply = self._command(session, 60, **command)
        if not reply.get("ok"):
            raise invalid(
                "snapshot_failed",
                t("error.debug_snapshot_failed", detail=str(reply.get("error") or "")),
            )
        return {key: reply.get(key) for key in _SNAPSHOT_KEYS}

    def screenshot(self, session_id: str) -> DebugSession:
        session = self.get(session_id)
        self._command(session, 60, cmd="screenshot")
        return session

    def reset(self, session_id: str) -> DebugSession:
        """從頭開始：開新的頁面（重新載入登入狀態），每一步都回到還沒執行。"""
        session = self.get(session_id)
        self._command(session, 120, cmd="reset")
        session.steps = _steps(session.scenario)
        session.next_index = 0
        session.screenshot = None
        session.located = None
        return session

    def reload(self, session_id: str, revision: int) -> DebugSession:
        """換到同一個場景的另一個版本；執行過的步驟依 id 保留狀態，瀏覽器與 facts 不變。"""
        session = self.get(session_id)
        scenario = self.services.revision_scenario(session.scene_id, revision)
        if scenario.script is not None:
            raise invalid("debug_script", t("error.debug_script"))
        # 已求值的舊值跳脫；新增預設值保留寫法，交給開瀏覽器的裝置依當地時間求值。
        raw = {
            name: spec.default for name, spec in scenario.inputs.items() if spec.default is not None
        }
        raw.update(
            {
                name: escape(value)
                for name, value in session.inputs.items()
                if name in scenario.inputs
            }
        )
        if session.device is not None and self.hosts is not None:
            via = self.hosts.current()
            if via is None or via.id != session.device:
                via = Via(session.device, self.hosts.get_recorder(session.device).name)
            self.hosts.check(
                via,
                headed=False,
                features=self.services.revision_features(session.scene_id, revision)
                | input_features(raw),
            )
            # 錄製端在另一台電腦：要能接受直接帶內容的 load 命令（v0.6.3），舊版說明要更新
            self.hosts.require(via, INLINE_LOAD)
        files = self.services.revision_files(session.scene_id, revision)
        text = files[SCENARIO_FILE]
        # 子場景（M7.2）：新版本用到的 calls/ 檔案跟著命令送過去
        calls = {path: content for path, content in files.items() if is_call_path(path)}
        extra: dict[str, object] = {"calls": calls} if calls else {}
        # 留一份在伺服器的工作階段資料夾，方便查問題；子程序用的是命令裡的內容
        (session.folder / f"scenario-{revision}.yaml").write_text(text, encoding="utf-8")
        # 既有入參已求值；只讓新版本新增的預設值求值，保留跳脫後的字面文字。
        resolved, problems = prepare_inputs(scenario, raw)
        if problems:
            # 新版本的入參對不上時保留舊值；新增動態值仍交給子程序求值
            defaults, _ = prepare_inputs(scenario, {})
            resolved = defaults | {k: v for k, v in session.inputs.items() if k in scenario.inputs}
        inputs = session.folder / f"input-{revision}.json"
        inputs.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
        # 子程序可能在錄製端（另一台電腦），讀不到伺服器的檔案：場景內容與入參直接放在命令裡
        reply = self._command(
            session, 60, cmd="load", revision=revision, scenarioText=text, inputs=raw, **extra
        )
        if not reply.get("ok"):
            details: dict[str, object] = {}
            issues = reply.get("issues")
            if isinstance(issues, list):
                details["issues"] = cast("list[object]", issues)
            raise invalid("revision_invalid", str(reply.get("error") or ""), **details)
        actual = reply.get("inputs")
        if isinstance(actual, dict):
            resolved = cast("dict[str, object]", actual)
        inputs.write_text(json.dumps(resolved, ensure_ascii=False), encoding="utf-8")
        previous = {found.id: found for state in session.steps for found in state.walk()}
        session.scenario = scenario
        session.revision = revision
        session.inputs = resolved
        session.steps = _steps(scenario)
        for state in session.steps:
            for found in state.walk():
                old = previous.get(found.id)
                if old is not None:
                    found.status, found.runs, found.error = old.status, old.runs, old.error
        executed = [state.index for state in session.steps if state.runs]
        session.next_index = max(executed) + 1 if executed else 0
        return session

    def restart(self, session_id: str, revision: int) -> DebugSession:
        """用指定的版本重新開始這個工作階段（換版本失敗時，調試頁的「用新版本重新開始調試」）。

        沿用瀏覽器、有頭／無頭、網址與入參；已求過值的入參跳脫，不再求一次值；新版本沒有的入參不帶。
        瀏覽器開在原本那台（錄製端或伺服器），不看這次請求從哪裡來。
        會關掉目前的瀏覽器，從第 1 步開始。
        """
        session = self.get(session_id)
        scenario = self.services.revision_scenario(session.scene_id, revision)
        inputs = {
            name: escape(value) for name, value in session.inputs.items() if name in scenario.inputs
        }
        # 檔案入參（M7c）：用原本的值（inputs 裡的是名稱、大小、sha256）；新版本不再是檔案的不帶
        for name, value in session.file_inputs.items():
            spec = scenario.inputs.get(name)
            if spec is not None and spec.type == "file":
                inputs[name] = value
            else:
                inputs.pop(name, None)
        via: Via | None = None
        if session.device is not None and self.hosts is not None:
            via = Via(session.device, self.hosts.get_recorder(session.device).name)
        with use_recorder(via):
            return self.start(
                session.scene_id,
                revision=revision,
                inputs=inputs,
                engine=session.engine,
                headless=session.headless,
                base_url=session.base_url,
                restart=True,
                client_id=session.client_id,
            )

    # ------------------------------------------------------------ 結束

    def close(self, session_id: str) -> None:
        session = self.get(session_id)
        self._close(session, "closed")

    def _close(self, session: DebugSession, status: str, message: str | None = None) -> None:
        session.status = status
        session.message = message
        process = session.process
        if process is not None:
            send(process, json.dumps({"cmd": "close"}))
            stop(process, grace=5)
        with self._lock:
            self._sessions.pop(session.id, None)
        shutil.rmtree(session.folder, ignore_errors=True)

    def start_reaper(self, interval: float = 30.0) -> None:
        """背景執行緒：關閉閒置太久的工作階段。"""
        if self._reaper is not None:
            return

        def loop() -> None:
            while not self._stopping.wait(interval):
                self.reap()

        self._reaper = threading.Thread(target=loop, name="debug-reaper", daemon=True)
        self._reaper.start()

    def reap(self) -> int:
        idle = [
            session
            for session in self.sessions()
            if session.status == "ready"
            and time.monotonic() - session.last_used > self.idle_seconds
        ]
        with self._lock:
            failed = [s for s in self._sessions.values() if s.status == "failed"]
        for session in idle:
            self._close(session, "closed", t("debug.idle_closed"))
        for session in failed:
            if time.monotonic() - session.last_used > self.idle_seconds:
                self._close(session, "failed", session.message)
        return len(idle)

    def close_all(self) -> None:
        self._stopping.set()
        with self._lock:
            sessions = list(self._sessions.values())
        for session in sessions:
            self._close(session, "closed")

    def remove_leftovers(self) -> None:
        """伺服器啟動時：清掉上次沒關掉的工作階段目錄。"""
        for folder in self.storage.debug.glob("*"):
            if folder.is_dir():
                shutil.rmtree(folder, ignore_errors=True)


def _parse(line: str | None) -> dict[str, object]:
    if not line:
        return {}
    try:
        data: object = json.loads(line)
    except ValueError:
        return {}
    return cast("dict[str, object]", data) if isinstance(data, dict) else {}


def _tail(log: Path, size: int = 2000) -> str:
    try:
        text = log.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    lines = [line.strip() for line in text[-size:].splitlines() if line.strip()]
    return lines[-1] if lines else ""
