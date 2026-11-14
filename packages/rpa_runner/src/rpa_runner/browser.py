"""在瀏覽器中執行 DSL 步驟，留下頁面事實。在子程序裡執行（見 child.py）。

- 每次執行用獨立的瀏覽器與 BrowserContext，結束就關閉。
- 每一步的逾時 = min(步驟 timeout 或 defaults.timeout 或 30 秒, 總期限剩下的時間)。
- 步驟欄位中的 ``{{ }}`` 在執行該步驟前才代入，所以可以用前面步驟抽到的 facts。
- 有副作用的動作（點擊、填寫、勾選、按鍵）不會因為逾時自動重試。
- 新分頁（M7b）：步驟有 ``popup`` 時，執行動作時等它開出新分頁，以這個名稱記在 :class:`Tabs`；
  步驟有 ``page`` 時在那個分頁執行。逐步調試整個工作階段用同一個 Tabs。
- 上傳檔案（M7c）：``upload`` 把檔案入參準備好的檔案交給上傳框（``target``）、點擊後開出的
  選擇檔案視窗（``trigger``），或拖放到元素上（``dropzone``）。每個分頁一開始就監聽選擇檔案的
  視窗（:class:`Tabs`）：有頭模式不會跳出系統的視窗卡在畫面上；不是 upload 開出的，這一步照樣
  通過，紀錄多一條提醒（D6）。
- 下載檔案（ADR 0020）：``download`` 點擊並等待下載完成，存到共用工作資料夾的 ``downloads/``
  （``workspace``），事實是 ``{"workspace", "name", "size", "sha256"}``。
- 流程控制（M7.1，ADR 0021，見 :class:`_Flow`）：區塊步驟遞迴執行；區塊裡的步驟執行到才新增
  紀錄，緊接在區塊後面（``path``、``parent``、``iteration``）。條件不成立不算失敗，判斷出錯算失敗。
  ``retry`` 失敗時再試；``onError: continue`` 記下失敗、繼續下一步；``try`` 接住裡面的失敗改走
  ``catch``。總期限到了、紀錄超過上限不能被接住或繼續。
"""

import base64
import contextlib
import re
import time
import weakref
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Final, Literal, cast

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import FileChooser, FrameLocator, Page, expect
from playwright.sync_api import Locator as PwLocator
from pydantic import TypeAdapter

from rpa_core.dsl import (
    CheckStep,
    ClickStep,
    DownloadStep,
    ExpectStep,
    ExtractField,
    ExtractStep,
    FillStep,
    GotoStep,
    Locator,
    PressStep,
    Scenario,
    ScreenshotStep,
    SelectStep,
    Step,
    UploadStep,
    WaitForStep,
)
from rpa_core.dsl.calls import CallKey, CallTable
from rpa_core.dsl.files import (
    MAX_DROP_BYTES,
    clean_name,
    file_meta,
    format_size,
    guess_media_type,
)
from rpa_core.dsl.steps import (
    MAX_ITERATIONS,
    CallStep,
    ClosePageStep,
    Condition,
    ForEachStep,
    IfStep,
    OpenPageStep,
    RepeatStep,
    StepPath,
    TryStep,
    upload_input_names,
)
from rpa_runner.contract import build_outputs, check_inputs, run_verify
from rpa_runner.files import DOWNLOADS_DIR
from rpa_runner.i18n import t
from rpa_runner.templates import Context, render_native, render_tree

__all__ = [
    "DEFAULT_STEP_TIMEOUT_MS",
    "MAX_RECORDS",
    "Deadline",
    "DeadlineExceeded",
    "FlowLimitExceeded",
    "StepRecord",
    "Tabs",
    "plan_records",
    "resolve",
    "run_step",
    "run_steps",
]

DEFAULT_STEP_TIMEOUT_MS: Final = 30_000
MAX_RECORDS: Final = 10_000
"""一次執行最多幾筆步驟紀錄（M7.1，D4）；超過算失敗。"""
_STEP: Final = TypeAdapter[Step](Step)
_POLL_MS: Final = 100
"""條件等待時多久再看一次。"""
_VISIBLE_SCAN: Final = 20
"""條件 visible／hidden 最多看前幾個符合的元素。"""
_CHECK_TIMEOUT_MS: Final = 1_000
"""條件讀元素的狀態、文字時，元素已經找到，只給一小段時間。"""
_MAY_OPEN_CHOOSER: Final = frozenset({"click", "press", "check"})
_CHOOSER_WAITS_MS: Final = (0, 10, 20)
"""點擊後等選擇檔案視窗事件的幾段時間（合計最多 30 ms）：Playwright 收到視窗後還要向瀏覽器查元素
才送出事件。只等、不碰頁面（在頁面裡執行程式碼會卡在換頁中）。"""
"""可能開出選擇檔案視窗的動作（M7c）：結束時確認有沒有沒人處理的視窗。"""
_NOT_RENDERED: Final = frozenset({"name", "files"})
_CONTAINERS: Final = frozenset({"if", "forEach", "repeat", "try", "call"})
"""裡面還有步驟的動作：區塊（M7.1）與 call（M7.2）。"""
"""步驟裡不代入 {{ }} 的欄位：name 是給人看的；upload 的 files 是入參的引用（M7c）。"""
_TABLE_JS: Final = """
(table) => {
  const rows = [...table.querySelectorAll('tr')];
  if (!rows.length) return [];
  const headerRow = table.querySelector('thead tr') || rows[0];
  const headers = [...headerRow.querySelectorAll('th,td')].map((cell) => cell.innerText.trim());
  const body = rows.filter((row) => row !== headerRow && row.querySelector('td'));
  return body.map((row) => Object.fromEntries(
    [...row.querySelectorAll('td,th')].map(
      (cell, i) => [headers[i] || `column${i + 1}`, cell.innerText.trim()]
    )
  ));
}
"""


class DeadlineExceeded(Exception):  # noqa: N818 - 與 TimeoutError 區分，名稱照語意
    """總期限已到。"""


class FlowLimitExceeded(Exception):  # noqa: N818 - 名稱照語意
    """步驟紀錄超過上限（M7.1）：不能被 try 接住，也不能 onError: continue。"""


@dataclass(frozen=True, slots=True)
class Deadline:
    """以單調時鐘計算的總期限。"""

    expires_at: float

    @classmethod
    def after(cls, seconds: float) -> "Deadline":
        return cls(time.monotonic() + seconds)

    def remaining_ms(self) -> int:
        return int((self.expires_at - time.monotonic()) * 1000)

    def budget(self, step_ms: int) -> int:
        """這一步可以用的毫秒數；總期限已到就拋出 DeadlineExceeded。"""
        remaining = self.remaining_ms()
        if remaining <= 0:
            raise DeadlineExceeded
        return max(1, min(step_ms, remaining))


def _utc(moment: float | None) -> str | None:
    """實際時間（time.time() 的秒數）→ UTC、到毫秒的 ISO 8601，例如 2026-10-21T03:30:12.041Z。"""
    if moment is None:
        return None
    text = datetime.fromtimestamp(moment, UTC).isoformat(timespec="milliseconds")
    return text.replace("+00:00", "Z")


@dataclass(slots=True)
class StepRecord:
    """一個步驟的執行紀錄（寫進 steps.json）。

    ``started_at``、``ended_at`` 是實際時間（``time.time()``），回看時和錄影的開始時間相減，
    就是這一步在影片裡的位置（M12）；``url`` 是這一步結束後頁面的網址（影片只錄到網頁內容）。
    """

    id: str
    action: str
    name: str | None
    status: Literal["passed", "failed", "skipped"] = "skipped"
    duration_ms: int = 0
    error: str | None = None
    artifacts: list[str] = field(default_factory=list[str])
    started_at: float | None = None
    ended_at: float | None = None
    url: str | None = None
    page_id: str | None = None
    created_page_id: str | None = None
    files: list[str] = field(default_factory=list[str])
    """upload 交給網頁的檔名（M7c）。"""
    notes: list[str] = field(default_factory=list[str])
    """不影響結果的提醒，例如開出了沒有指定檔案的選擇檔案視窗（M7c）。"""
    shot: str | None = None
    """錄影時這一步做完的縮小截圖（執行目錄裡的相對路徑，見 stepshots.py）。"""
    shot_at: float | None = None
    """開始拍那張截圖的實際時間。"""
    path: StepPath = ()
    """這一步在場景檔裡的位置（M7.1），例如 ``("steps", 2, "steps", 0)``；回看依此找原文。"""
    parent: int | None = None
    """外層區塊是第幾筆紀錄（從 1 起，M7.1）；最外層的步驟是 None。"""
    iteration: int | None = None
    """迴圈的第幾項／第幾輪（從 1 起，M7.1）；只有迴圈直接包著的步驟有。"""
    attempts: int = 0
    """試了幾次（retry，M7.1）；沒執行是 0。"""
    handled: Literal["continued", "caught"] | None = None
    """失敗但沒有讓整次執行停下（M7.1）：onError: continue，或被 try 的 catch 接住。"""
    condition: bool | None = None
    """if 的條件結果（M7.1）。"""
    branch: Literal["then", "else"] | None = None
    """if 走了哪個分支（M7.1）；條件不成立又沒有 else 時是 None。"""
    iterations: int | None = None
    """迴圈跑完幾輪（forEach、repeat，M7.1）。"""
    caught: dict[str, str] | None = None
    """try 接住的失敗：``{"step": 失敗的步驟 id, "error": 錯誤}``（M7.1）。"""
    call: dict[str, object] | None = None
    """call 呼叫的子場景（M7.2）：``{"scenario", "revision", "name"}``，跑到獨立斷言時加上
    ``checks``（每一條的名稱與結果），通過後加上 ``outputs``（出參的名稱）。"""
    number: int = 0
    """第幾筆紀錄（從 1 起）；不寫進 steps.json（順序就是編號）。"""

    def to_json(self) -> dict[str, object]:
        return {
            "id": self.id,
            "action": self.action,
            "name": self.name,
            "status": self.status,
            "durationMs": self.duration_ms,
            "error": self.error,
            "artifacts": self.artifacts,
            "startedAt": _utc(self.started_at),
            "endedAt": _utc(self.ended_at),
            "url": self.url,
            "pageId": self.page_id,
            "createdPageId": self.created_page_id,
            "files": self.files,
            "notes": self.notes,
            "shot": self.shot,
            "shotAt": _utc(self.shot_at),
            "path": list(self.path),
            "parent": self.parent,
            "iteration": self.iteration,
            "attempts": self.attempts,
            "handled": self.handled,
            "condition": self.condition,
            "branch": self.branch,
            "iterations": self.iterations,
            "caught": self.caught,
            "call": self.call,
        }


# ---------------------------------------------------------------- 定位器


def resolve(scope: Page | PwLocator | FrameLocator, locator: Locator) -> PwLocator:
    """DSL 定位器 → Playwright Locator（不含 fallback）。

    有 frame 時先進入那個 iframe 載入的頁面；within 與元素本身都在那個頁面裡找。
    anyFrame 在頁面與所有 iframe 裡找（Playwright 的 ``frame_locator()``，不帶引數）；
    只能從頁面開始找，不能相對於另一個元素（例如 extract 的 fields）。
    """
    if locator.any_frame:
        if not isinstance(scope, Page):
            raise ValueError(t("browser.any_frame_scope"))
        scope = scope.frame_locator()
    if locator.frame is not None:
        scope = resolve(scope, locator.frame).content_frame
    base: Page | PwLocator | FrameLocator = (
        resolve(scope, locator.within) if locator.within else scope
    )
    exact = bool(locator.exact)
    match locator.strategy:
        case "testId":
            result = base.get_by_test_id(cast("str", locator.test_id))
        case "role":
            result = base.get_by_role(
                cast("Literal['button']", locator.role), name=locator.name, exact=exact
            )
        case "label":
            result = base.get_by_label(cast("str", locator.label), exact=exact)
        case "placeholder":
            result = base.get_by_placeholder(cast("str", locator.placeholder), exact=exact)
        case "text":
            result = base.get_by_text(cast("str", locator.text), exact=exact)
        case "altText":
            result = base.get_by_alt_text(cast("str", locator.alt_text), exact=exact)
        case "title":
            result = base.get_by_title(cast("str", locator.title), exact=exact)
        case "css":
            result = base.locator(f"css={locator.css}")
        case _:
            result = base.locator(f"xpath={locator.xpath}")
    if locator.has_text is not None:
        result = result.filter(has_text=locator.has_text)
    if locator.nth is not None:
        result = result.nth(locator.nth)
    return result


def _inherit_frame(item: Locator, primary: Locator) -> Locator:
    """備用定位器沒寫 frame 時，沿用主要定位器的 frame。"""
    if item.frame is not None or primary.frame is None:
        return item
    return item.model_copy(update={"frame": primary.frame})


def locate(page: Page, locator: Locator, timeout_ms: int) -> PwLocator:
    """有 fallback 時，在逾時內輪流找第一個存在的候選；都找不到就回傳主要定位器。"""
    primary = resolve(page, locator)
    if not locator.fallback:
        return primary
    candidates = [
        primary,
        *(resolve(page, _inherit_frame(item, locator)) for item in locator.fallback),
    ]
    ends = time.monotonic() + timeout_ms / 1000
    while time.monotonic() < ends:
        for candidate in candidates:
            if candidate.count() > 0:
                return candidate
        time.sleep(0.1)
    return primary


# ---------------------------------------------------------------- 步驟


def _matcher(text: str, match: str) -> str | re.Pattern[str]:
    match match:
        case "equals":
            return text
        case "regex":
            return re.compile(text)
        case _:
            return re.compile(re.escape(text))


def _url_predicate(text: str, match: str) -> Callable[[str], bool]:
    match match:
        case "equals":
            return lambda url: url == text
        case "regex":
            pattern = re.compile(text)
            return lambda url: pattern.search(url) is not None
        case _:
            return lambda url: text in url


def _read(element: PwLocator, get: str, attribute: str | None, timeout: int) -> object:
    match get:
        case "value":
            return element.input_value(timeout=timeout)
        case "html":
            return element.inner_html(timeout=timeout)
        case "attribute":
            return element.get_attribute(cast("str", attribute), timeout=timeout) or ""
        case "table":
            return element.evaluate(_TABLE_JS, timeout=timeout)  # pyright: ignore[reportUnknownMemberType]
        case _:
            return element.inner_text(timeout=timeout).strip()


def _read_field(element: PwLocator, spec: ExtractField, timeout: int) -> object:
    target = resolve(element, spec.target).first if spec.target else element
    return _read(target, spec.get, spec.attribute, timeout)


def _extract(page: Page, step: ExtractStep, timeout: int) -> object:
    located = locate(page, step.target, timeout)
    located.first.wait_for(state="attached", timeout=timeout)
    elements = located.all() if step.multiple else [located.first]

    def one(element: PwLocator) -> object:
        if step.fields is not None:
            return {name: _read_field(element, spec, timeout) for name, spec in step.fields.items()}
        return _read(element, step.get, step.attribute, timeout)

    values = [one(element) for element in elements]
    return values if step.multiple else values[0]


def _expect(page: Page, step: ExpectStep, timeout: int) -> None:
    if step.target is None:
        if step.url is not None:
            expect(page).to_have_url(_matcher(step.url, step.match), timeout=timeout)
        else:
            expect(page).to_have_title(
                _matcher(cast("str", step.title), step.match), timeout=timeout
            )
        return
    target = locate(page, step.target, timeout)
    assertions = expect(target)
    if step.count is not None:
        assertions.to_have_count(step.count, timeout=timeout)
    elif step.text is not None:
        if step.match == "contains":
            assertions.to_contain_text(step.text, timeout=timeout)
        else:
            assertions.to_have_text(_matcher(step.text, step.match), timeout=timeout)
    elif step.value is not None:
        assertions.to_have_value(_matcher(step.value, step.match), timeout=timeout)
    else:
        match step.state:
            case "hidden":
                assertions.to_be_hidden(timeout=timeout)
            case "enabled":
                assertions.to_be_enabled(timeout=timeout)
            case "disabled":
                assertions.to_be_disabled(timeout=timeout)
            case "checked":
                assertions.to_be_checked(timeout=timeout)
            case "unchecked":
                assertions.to_be_checked(checked=False, timeout=timeout)
            case "editable":
                assertions.to_be_editable(timeout=timeout)
            case _:
                assertions.to_be_visible(timeout=timeout)


def _url(base_url: str | None, url: str) -> str:
    if url.startswith("/") and base_url:
        return base_url.rstrip("/") + url
    return url


_GUARDS: "weakref.WeakKeyDictionary[Page, Tabs]" = weakref.WeakKeyDictionary()
"""已經在監聽選擇檔案視窗的分頁 → 目前負責記錄的 Tabs（同一個分頁只監聽一次）。"""


def _on_chooser(chooser: FileChooser) -> None:
    tabs = _GUARDS.get(chooser.page)
    if tabs is not None and not tabs.expecting:
        tabs.choosers += 1


@dataclass(slots=True)
class Tabs:
    """場景的分頁（M7b）：一開始的分頁，加上步驟的 popup 開出來的；記得最後用到哪個分頁。

    每個分頁都監聽選擇檔案的視窗（M7c）：``choosers`` 是不是 upload 開出的視窗數。
    """

    main: Page
    named: dict[str, Page] = field(default_factory=dict[str, Page])
    last: Page | None = None
    identify: Callable[[Page], str] | None = None
    choosers: int = 0
    expecting: bool = False
    """upload 的 trigger 正在等選擇檔案的視窗：那個視窗不算提醒。"""
    trigger: "StepRecord | None" = None
    """最近一個可能開出選擇檔案視窗的步驟（click、press、check）：之後的步驟才收到的視窗算它的。"""

    def __post_init__(self) -> None:
        self.guard(self.main)

    def guard(self, page: Page) -> None:
        """開始監聽這個分頁的選擇檔案視窗；有監聽時 Playwright 攔下視窗，不跳出系統的對話框。"""
        first = page not in _GUARDS
        _GUARDS[page] = self
        if first:
            page.on("filechooser", _on_chooser)

    def release(self) -> None:
        """不再監聽選擇檔案的視窗（例如接著錄製：錄製時使用者要能在系統的視窗選檔）。"""
        for page in [page for page, owner in _GUARDS.items() if owner is self]:
            with contextlib.suppress(Exception):
                page.remove_listener("filechooser", _on_chooser)
            _GUARDS.pop(page, None)

    def get(self, name: str | None) -> Page:
        """步驟的 page 指的分頁；沒寫是一開始的分頁。"""
        if name is None:
            return self.main
        page = self.named.get(name)
        if page is None:
            raise LookupError(t("browser.tab_missing", name=name))
        if page.is_closed():
            raise LookupError(t("browser.tab_closed", name=name))
        return page

    @property
    def active(self) -> Page:
        """最後用到的分頁（剛開出的新分頁也算）；它關掉了或還沒執行過時，是一開始的分頁。"""
        page = self.last
        return self.main if page is None or page.is_closed() else page


@dataclass(slots=True)
class _Run:
    tabs: Tabs
    scenario: Scenario
    base_url: str | None
    artifacts: Path
    facts: dict[str, object]
    files: Mapping[str, Sequence[Path]] = field(default_factory=dict[str, Sequence[Path]])
    """檔案入參 → 準備好的檔案（M7c）。"""
    workspace: Path | None = None
    """共用工作資料夾（ADR 0020）：download 步驟存檔的地方。"""
    calls: CallTable = field(default_factory=dict[CallKey, Scenario])
    """``call`` 用到的子場景（M7.2，見 rpa_core.dsl.calls）。"""
    prefix: str = ""
    """截圖檔名的開頭（M7.2）：子場景裡的截圖加上 call 步驟的 id，不和呼叫場景的同名檔案相撞。"""

    def execute(self, step: Step, timeout: int, record: StepRecord) -> None:
        page = self.tabs.get(step.page)
        self.tabs.last = page
        self.tabs.choosers = 0
        if self.tabs.identify is not None:
            record.page_id = self.tabs.identify(page)
        try:
            popup = getattr(step, "popup", None)
            if not isinstance(popup, str):
                self._act(page, step, timeout, record)
                return
            with page.expect_popup(timeout=timeout) as opened:
                self._act(page, step, timeout, record)
            tab = opened.value
            self.tabs.guard(tab)
            if self.tabs.identify is not None:
                record.created_page_id = self.tabs.identify(tab)
            tab.wait_for_load_state("domcontentloaded", timeout=timeout)
            self.tabs.named[popup] = tab
            self.tabs.last = tab
        finally:
            opener = step.action in _MAY_OPEN_CHOOSER
            if opener and not self.tabs.choosers:
                self._flush_choosers(page)
            if self.tabs.choosers:
                # 這一步不會開視窗時，是前面那一步開的（事件晚到）
                owner = record if opener or self.tabs.trigger is None else self.tabs.trigger
                owner.notes.append(t("browser.chooser_unhandled"))
                self.tabs.choosers = 0
            if opener:
                self.tabs.trigger = record

    def _flush_choosers(self, page: Page) -> None:
        """選擇檔案視窗的事件常在點擊回傳之後才到：等一小段時間，到了就停。"""
        with contextlib.suppress(Exception):
            for wait in _CHOOSER_WAITS_MS:
                if page.is_closed() or self.tabs.choosers:
                    return
                page.wait_for_timeout(wait)

    def _upload_paths(self, step: UploadStep) -> list[Path]:
        paths: list[Path] = []
        for name in upload_input_names(step.files):
            prepared = self.files.get(name)
            if prepared is None:
                raise LookupError(t("browser.upload_not_prepared", name=name))
            paths.extend(prepared)
        return paths

    def _upload(self, page: Page, step: UploadStep, timeout: int, record: StepRecord) -> None:
        paths = self._upload_paths(step)
        record.files = [path.name for path in paths]
        try:
            if step.target is not None:
                locate(page, step.target, timeout).set_input_files(paths, timeout=timeout)
            elif step.trigger is not None:
                self.tabs.expecting = True
                try:
                    with page.expect_file_chooser(timeout=timeout) as chooser:
                        locate(page, step.trigger, timeout).click(timeout=timeout)
                    chooser.value.set_files(paths, timeout=timeout)
                finally:
                    self.tabs.expecting = False
            elif step.dropzone is not None:
                _drop(locate(page, step.dropzone, timeout), paths, timeout)
        except PlaywrightError as error:
            friendly = _upload_error(str(error))
            if friendly is None:
                raise
            raise ValueError(friendly) from error

    def _download(self, page: Page, step: DownloadStep, timeout: int, record: StepRecord) -> None:
        """點擊並等待下載完成，存到共用工作資料夾的 downloads/；事實是檔案的說明。"""
        if self.workspace is None:
            raise LookupError(t("browser.download_no_workspace"))
        with page.expect_download(timeout=timeout) as info:
            locate(page, step.target, timeout).click(timeout=timeout)
        download = info.value
        folder = self.workspace / DOWNLOADS_DIR
        folder.mkdir(parents=True, exist_ok=True)
        name = clean_name(step.file_name or download.suggested_filename or "download")
        target = _unique_path(folder, name)
        download.save_as(target)  # 等到下載完成；失敗時拋出
        meta = file_meta(target, target.name)
        record.files = [target.name]
        self.facts[step.as_] = {
            "workspace": target.relative_to(self.workspace).as_posix(),
            **meta.to_json(),
        }

    def _open_page(self, page: Page, step: OpenPageStep, timeout: int, record: StepRecord) -> None:
        """自己開的新分頁（M7.1）：同一個瀏覽器工作階段；迴圈裡關掉再開可以用同一個名稱。

        這一步的動作（開分頁、載入網址）發生在新分頁上，所以步驟紀錄的 pageId 也是新分頁：
        回看依 pageId 決定播哪個分頁的錄影，記成原分頁時新分頁載入的那段看不到（2026-11-13，
        使用者驗收時發現）。點擊開出的 popup（M7b）不同，那一步是在原分頁上點。
        """
        existing = self.tabs.named.get(step.as_)
        if existing is not None and not existing.is_closed():
            raise LookupError(t("browser.tab_already_open", name=step.as_))
        tab = page.context.new_page()
        self.tabs.guard(tab)
        if self.tabs.identify is not None:
            record.created_page_id = self.tabs.identify(tab)
            record.page_id = record.created_page_id
        self.tabs.named[step.as_] = tab
        self.tabs.last = tab
        if step.url is not None:
            tab.goto(_url(self.base_url, step.url), wait_until=step.wait_until, timeout=timeout)

    def _act(self, page: Page, step: Step, timeout: int, record: StepRecord) -> None:
        match step:
            case GotoStep():
                page.goto(
                    _url(self.base_url, step.url), wait_until=step.wait_until, timeout=timeout
                )
            case ClickStep():
                try:
                    locate(page, step.target, timeout).click(
                        button=step.button,
                        click_count=step.click_count,
                        modifiers=step.modifiers,
                        timeout=timeout,
                    )
                except PlaywrightError:
                    # 點了之後頁面自己關掉（例如按鈕執行 window.close()）：Playwright 有時在點擊收尾
                    # 時才發現頁面已關，回報「Target page … has been closed」，點擊其實已經完成
                    # （2026-10-28，回看切換分頁的測試在 CI 與每晚測試偶爾失敗）
                    if not page.is_closed():
                        raise
            case FillStep():
                locate(page, step.target, timeout).fill(step.value, timeout=timeout)
            case SelectStep():
                locate(page, step.target, timeout).select_option(step.option, timeout=timeout)
            case CheckStep():
                locate(page, step.target, timeout).set_checked(step.checked, timeout=timeout)
            case PressStep():
                if step.target is None:
                    page.keyboard.press(step.key)
                else:
                    locate(page, step.target, timeout).press(step.key, timeout=timeout)
            case WaitForStep():
                if step.target is not None:
                    locate(page, step.target, timeout).wait_for(state=step.state, timeout=timeout)
                elif step.url is not None:
                    page.wait_for_url(_url_predicate(step.url, step.match), timeout=timeout)
                else:
                    page.wait_for_load_state(step.load_state, timeout=timeout)
            case ExpectStep():
                _expect(page, step, timeout)
            case ExtractStep():
                value = _extract(page, step, timeout)
                if step.append:
                    # 迴圈裡累積（M7.1）：清單攤平加入
                    previous = self.facts.get(step.as_)
                    kept = cast("list[object]", previous) if isinstance(previous, list) else []
                    added = cast("list[object]", value) if isinstance(value, list) else [value]
                    value = [*kept, *added]
                self.facts[step.as_] = value
            case OpenPageStep():
                self._open_page(page, step, timeout, record)
            case ClosePageStep():
                page.close()
            case UploadStep():
                self._upload(page, step, timeout, record)
            case DownloadStep():
                self._download(page, step, timeout, record)
            case ScreenshotStep():
                name = f"{self.prefix}{step.file or step.id}.png"
                path = self.artifacts / name
                if step.target is not None:
                    locate(page, step.target, timeout).screenshot(path=path, timeout=timeout)
                else:
                    page.screenshot(path=path, full_page=step.full_page, timeout=timeout)
                record.artifacts.append(name)
            case (
                IfStep() | ForEachStep() | RepeatStep() | TryStep() | CallStep()
            ):  # pragma: no cover
                raise TypeError(step.action)  # 區塊與 call 由 _Flow 執行，不會走到這裡


_DROP_JS: Final = """
(element, files) => {
  const data = new DataTransfer();
  for (const file of files) {
    const bytes = Uint8Array.from(atob(file.data), (c) => c.charCodeAt(0));
    data.items.add(new File([bytes], file.name, { type: file.type }));
  }
  for (const type of ['dragenter', 'dragover', 'drop']) {
    const init = { bubbles: true, cancelable: true, dataTransfer: data };
    element.dispatchEvent(new DragEvent(type, init));
  }
}
"""


def _unique_path(folder: Path, name: str) -> Path:
    """``folder/name``；已經有同名的檔案（例如同一次組合運行下載過）時加上 -2、-3…。"""
    target = folder / name
    stem, suffix = Path(name).stem, Path(name).suffix
    number = 2
    while target.exists():
        target = folder / f"{stem}-{number}{suffix}"
        number += 1
    return target


def _drop(element: PwLocator, paths: Sequence[Path], timeout: int) -> None:
    """拖拽區：在頁面裡做出 DataTransfer，對元素依序發出 dragenter、dragover、drop。"""
    total = sum(path.stat().st_size for path in paths)
    if total > MAX_DROP_BYTES:
        raise ValueError(
            t("browser.drop_too_large", size=format_size(total), limit=format_size(MAX_DROP_BYTES))
        )
    files = [
        {
            "name": path.name,
            "type": guess_media_type(path.name),
            "data": base64.b64encode(path.read_bytes()).decode("ascii"),
        }
        for path in paths
    ]
    element.evaluate(_DROP_JS, files, timeout=timeout)


def _upload_error(message: str) -> str | None:
    """Playwright 的上傳錯誤 → 看得懂的說明；不認得時回傳 None（照原本的錯誤）。"""
    if "Non-multiple file input" in message:
        return t("browser.upload_single")
    if "HTMLInputElement" in message or "input[type=file]" in message or "Not an input" in message:
        return t("browser.upload_not_input")
    return None


def plan_records(scenario: Scenario) -> list[StepRecord]:
    """最外層的每個步驟一筆紀錄，初始狀態是略過；區塊裡的步驟執行到才新增（M7.1）。"""
    return [
        StepRecord(step.id, step.action, step.name, path=("steps", index))
        for index, step in enumerate(scenario.steps or [])
    ]


def _first_line(error: BaseException) -> str:
    return f"{type(error).__name__}: {error}".splitlines()[0]


def _recoverable(error: BaseException) -> bool:
    """可以被 try 接住、onError: continue 的失敗：總期限到了、紀錄超過上限不行。"""
    return isinstance(error, Exception) and not isinstance(
        error, DeadlineExceeded | FlowLimitExceeded
    )


def _text_matches(actual: str, expected: str, match: str) -> bool:
    """條件的文字比對：contains（預設）、equals、regex；文字的空白先壓成一個（同 expect）。"""
    actual = " ".join(actual.split())
    if match == "equals":
        return actual == " ".join(expected.split())
    if match == "regex":
        return re.search(expected, actual) is not None
    return " ".join(expected.split()) in actual


def _check(page: Page, condition: Condition) -> bool:
    """條件現在成立嗎（不含 not，不等待）；讀不到時拋出，算這個區塊失敗。"""
    if condition.target is not None:
        located = locate(page, condition.target, 0)
        count = located.count()
        if condition.count is not None:
            return count == condition.count
        state = condition.state
        if state == "attached":
            return count > 0
        if state == "detached":
            return count == 0
        if state in ("visible", "hidden"):
            visible = any(located.nth(i).is_visible() for i in range(min(count, _VISIBLE_SCAN)))
            return visible if state == "visible" else not visible
        if count == 0:
            return False
        first = located.first
        match state:
            case "enabled":
                return first.is_enabled(timeout=_CHECK_TIMEOUT_MS)
            case "disabled":
                return first.is_disabled(timeout=_CHECK_TIMEOUT_MS)
            case "checked":
                return first.is_checked(timeout=_CHECK_TIMEOUT_MS)
            case "unchecked":
                return not first.is_checked(timeout=_CHECK_TIMEOUT_MS)
            case "editable":
                return first.is_editable(timeout=_CHECK_TIMEOUT_MS)
            case _:
                pass
        if condition.text is not None:
            text = first.inner_text(timeout=_CHECK_TIMEOUT_MS)
            return _text_matches(text, condition.text, condition.match)
        if condition.value is not None:
            value = first.input_value(timeout=_CHECK_TIMEOUT_MS)
            return _text_matches(value, condition.value, condition.match)
        return False
    if condition.url is not None:
        return _text_matches(page.url, condition.url, condition.match)
    if condition.title is not None:
        return _text_matches(page.title(), condition.title, condition.match)
    return False


@dataclass(frozen=True, slots=True)
class _Scope:
    """執行到這裡時多出的變數（迴圈變數、loop、error）與所在的區塊。"""

    variables: Mapping[str, object] = field(default_factory=dict[str, object])
    parent: int | None = None
    """外層區塊的紀錄編號。"""
    iteration: int | None = None
    catching: bool = False
    """在 try 的 steps 裡：失敗會被接住（紀錄先標上 caught，日誌才寫得對）。"""

    def inside(self, parent: StepRecord, *, iteration: int | None = None) -> "_Scope":
        return _Scope(self.variables, parent.number, iteration, self.catching)

    def with_variables(self, **variables: object) -> "_Scope":
        return _Scope({**self.variables, **variables}, self.parent, self.iteration, self.catching)


@dataclass(slots=True)
class _Flow:
    """依場景執行步驟（含區塊，M7.1），維護步驟紀錄。

    ``records`` 一開始是最外層每一步一筆（:func:`plan_records`）；區塊裡的步驟執行到才插在
    ``cursor``（上一筆執行過的紀錄後面），所以紀錄的順序就是執行的順序，已開始的紀錄編號不會變。
    """

    run: _Run
    records: list[StepRecord]
    context: Mapping[str, object]
    deadline: Deadline
    on_progress: Callable[[], None]
    after_step: Callable[[Page, StepRecord, int], None] | None
    cursor: int = 0

    # ------------------------------------------------------------ 走訪

    def top(self, steps: Sequence[Step]) -> None:
        planned = list(self.records)
        for step, record in zip(steps, planned, strict=True):
            self.cursor = self._position(record) + 1
            record.number = self.cursor
            self.execute(step, record, _Scope())

    def _position(self, record: StepRecord) -> int:
        for index in range(self.cursor, len(self.records)):
            if self.records[index] is record:
                return index
        return next(i for i, item in enumerate(self.records) if item is record)

    def _new_record(
        self, step: Step, path: StepPath, scope: _Scope, iteration: int | None
    ) -> StepRecord:
        if len(self.records) >= MAX_RECORDS:
            raise FlowLimitExceeded(t("browser.too_many_records", max=MAX_RECORDS))
        record = StepRecord(
            step.id, step.action, step.name, path=path, parent=scope.parent, iteration=iteration
        )
        self.records.insert(self.cursor, record)
        self.cursor += 1
        record.number = self.cursor
        return record

    def _list(
        self,
        steps: Sequence[Step],
        block: StepRecord,
        scope: _Scope,
        key: str,
        *,
        iteration: int | None = None,
    ) -> None:
        inner = scope.inside(block, iteration=iteration)
        for index, step in enumerate(steps):
            record = self._new_record(step, (*block.path, key, index), inner, iteration)
            self.execute(step, record, inner)

    # ------------------------------------------------------------ 一步

    def execute(self, step: Step, record: StepRecord, scope: _Scope) -> None:
        """執行一步（含區塊）並更新紀錄；失敗時拋出，onError: continue 的不拋出。"""
        started = time.monotonic()
        record.started_at = time.time()
        block = isinstance(step, IfStep | ForEachStep | RepeatStep | TryStep | CallStep)
        try:
            if block:
                self.on_progress()  # 讓進度先看到區塊開始了
                self._block(step, record, scope)
            else:
                self._leaf(step, record, scope)
            record.status = "passed"
        except BaseException as error:
            record.status = "failed"
            record.error = _first_line(error)
            if not _recoverable(error):
                raise
            if step.on_error == "continue":
                record.handled = "continued"
            else:
                if scope.catching:
                    record.handled = "caught"  # 外層的 try 會接住
                raise
        finally:
            record.duration_ms = int((time.monotonic() - started) * 1000)
            record.ended_at = time.time()
            with contextlib.suppress(Exception):  # 頁面已經關閉時沒有網址
                record.url = self.run.tabs.active.url
            if not block and self.after_step is not None:
                with contextlib.suppress(Exception):
                    self.after_step(self.run.tabs.active, record, record.number)
            self.on_progress()

    def _values(self, scope: _Scope) -> Context:
        return {**self.context, "facts": self.run.facts, **scope.variables}

    def _leaf(self, step: Step, record: StepRecord, scope: _Scope) -> None:
        default_ms = self.run.scenario.defaults.timeout or DEFAULT_STEP_TIMEOUT_MS
        attempts = 1 + (step.retry.times if step.retry is not None else 0)
        for attempt in range(1, attempts + 1):
            record.attempts = attempt
            try:
                timeout = self.deadline.budget(step.timeout or default_ms)
                raw = step.model_dump(mode="json", by_alias=True, exclude_unset=True)
                values = self._values(scope)
                rendered = _STEP.validate_python(render_tree(raw, values, skip=_NOT_RENDERED))
                self.run.execute(rendered, timeout, record)
                return
            except BaseException as error:
                if attempt >= attempts or not _recoverable(error) or step.retry is None:
                    raise
                record.notes.append(
                    t("browser.retry_failed", attempt=attempt, error=_first_line(error))
                )
                if self.deadline.remaining_ms() <= step.retry.delay:
                    raise
                self._pause(step.retry.delay)

    def _pause(self, milliseconds: int) -> None:
        """等一下；用頁面等待，期間照樣處理瀏覽器的事件。"""
        if milliseconds <= 0:
            return
        try:
            self.run.tabs.active.wait_for_timeout(milliseconds)
        except PlaywrightError:
            time.sleep(milliseconds / 1000)

    # ------------------------------------------------------------ 區塊

    def _block(self, step: Step, record: StepRecord, scope: _Scope) -> None:
        match step:
            case IfStep():
                passed = self._condition(step.condition, scope)
                record.condition = passed
                if passed:
                    record.branch = "then"
                    self._list(step.then, record, scope, "then")
                elif step.else_ is not None:
                    record.branch = "else"
                    self._list(step.else_, record, scope, "else")
            case ForEachStep():
                self._for_each(step, record, scope)
            case RepeatStep():
                self._repeat(step, record, scope)
            case TryStep():
                self._try(step, record, scope)
            case CallStep():
                self._call(step, record, scope)
            case _:  # pragma: no cover - 只有上面幾種區塊
                raise TypeError(step.action)

    def _condition(self, condition: Condition, scope: _Scope) -> bool:
        values = self._values(scope)
        if condition.expression is not None:
            return bool(render_native(condition.expression, values)) != condition.not_
        raw = condition.model_dump(mode="json", by_alias=True, exclude_unset=True)
        rendered = Condition.model_validate(render_tree(raw, values))
        page = self.run.tabs.get(rendered.page)
        wait = self.deadline.budget(rendered.wait) if rendered.wait else 0
        ends = time.monotonic() + wait / 1000
        while True:
            result = _check(page, rendered) != rendered.not_
            if result or time.monotonic() >= ends:
                return result
            page.wait_for_timeout(_POLL_MS)

    def _for_each(self, step: ForEachStep, record: StepRecord, scope: _Scope) -> None:
        if isinstance(step.items, list):
            items: list[object] = list(step.items)
        else:
            value = render_native(step.items, self._values(scope))
            if not isinstance(value, list | tuple):
                raise TypeError(t("browser.items_not_list", type=type(value).__name__))
            items = list(cast("list[object] | tuple[object, ...]", value))
        if len(items) > MAX_ITERATIONS:
            raise ValueError(t("browser.too_many_items", count=len(items), max=MAX_ITERATIONS))
        record.iterations = 0
        count = len(items)
        for index, item in enumerate(items):
            last = index == count - 1
            loop = {"index": index + 1, "count": count, "first": index == 0, "last": last}
            inner = scope.with_variables(**{step.as_: item, "loop": loop})
            self._list(step.steps, record, inner, "steps", iteration=index + 1)
            record.iterations = index + 1

    def _repeat(self, step: RepeatStep, record: StepRecord, scope: _Scope) -> None:
        limit = step.times or step.max_ or 1
        record.iterations = 0
        inner = scope
        for round_ in range(1, limit + 1):
            loop: dict[str, object] = {"index": round_, "first": round_ == 1}
            if step.times is not None:
                loop |= {"count": step.times, "last": round_ == step.times}
            inner = scope.with_variables(loop=loop)
            if step.while_ is not None and not self._condition(step.while_, inner):
                return
            self._list(step.steps, record, inner, "steps", iteration=round_)
            record.iterations = round_
            if step.until is not None and self._condition(step.until, inner):
                return
        if step.times is not None:
            return
        if step.while_ is not None and not self._condition(step.while_, inner):
            return
        key = "browser.repeat_while_max" if step.while_ is not None else "browser.repeat_until_max"
        raise RuntimeError(t(key, max=limit))

    def _try(self, step: TryStep, record: StepRecord, scope: _Scope) -> None:
        first = self.cursor
        try:
            self._list(step.steps, record, replace(scope, catching=True), "steps")
        except BaseException as error:
            if not _recoverable(error):
                raise
            failed = "?"
            for item in self.records[first : self.cursor]:
                if item.status != "failed" or item.handled == "continued":
                    continue
                item.handled = "caught"
                # 優先記最內層失敗的那一步；只有區塊失敗（例如條件出錯）時記那個區塊
                if failed == "?" or item.action not in _CONTAINERS:
                    failed = item.id
            message = _first_line(error)
            record.caught = {"step": failed, "error": message}
            inner = scope.with_variables(error={"step": failed, "message": message})
            self._list(step.catch, record, inner, "catch")

    # ------------------------------------------------------------ 子場景（M7.2）

    def _call(self, step: CallStep, record: StepRecord, scope: _Scope) -> None:
        """在同一個瀏覽器裡接著執行子場景：入參照它的契約 → 它的步驟 → 它的獨立斷言 → 出參存成事實。

        子場景有自己的事實、分頁名稱與截圖檔名的開頭，看不到呼叫場景的迴圈變數；總期限、取消、
        步驟紀錄的上限都和呼叫場景共用。子場景開了沒關的分頁在結束時關掉。任何一段不通過，
        這一步失敗（可以被外層的 try 接住或 onError: continue）。
        """
        outer, outer_context = self.run, self.context
        callee = outer.calls.get((step.scenario, step.revision))
        if callee is None or callee.steps is None:
            raise LookupError(
                t("browser.call_missing", scenario=step.scenario, revision=step.revision)
            )
        record.call = {"scenario": step.scenario, "revision": step.revision, "name": callee.name}
        values = self._values(scope)
        given: dict[str, object] = {}
        for name, raw in (step.inputs or {}).items():
            value = render_native(raw, values) if isinstance(raw, str) else render_tree(raw, values)
            spec = callee.inputs.get(name)
            if (
                spec is not None
                and spec.type == "string"
                and isinstance(value, int | float)
                and not isinstance(value, bool)
            ):
                value = str(value)  # {{ loop.index }} 這類數字給文字入參時不用再轉
            given[name] = value
        inputs, problems = check_inputs(callee, given)
        if problems:
            raise ValueError(
                t("browser.call_inputs", problems="；".join(item.message for item in problems))
            )
        tabs = outer.tabs
        page = tabs.get(step.page)
        secrets = cast("Mapping[str, object]", outer_context.get("secrets") or {})
        context: dict[str, object] = {
            "inputs": inputs,
            "secrets": {name: secrets[name] for name in callee.secrets if name in secrets},
            "env": outer_context.get("env") or {},
        }
        # 執行時另外指定了網址（環境）就全部用它；否則子場景用自己的 baseUrl，沒寫用呼叫場景的
        overridden = outer.base_url != outer.scenario.browser.base_url
        base_url = outer.base_url if overridden else callee.browser.base_url or outer.base_url
        facts: dict[str, object] = {}
        main, named = tabs.main, tabs.named
        tabs.main, tabs.named = page, {}
        self.run = _Run(
            tabs,
            callee,
            base_url,
            outer.artifacts,
            facts,
            {},
            outer.workspace,
            outer.calls,
            f"{outer.prefix}{step.id}.",
        )
        self.context = context
        try:
            self._list(callee.steps, record, _Scope(catching=scope.catching), "call")
        finally:
            for tab in tabs.named.values():
                if not tab.is_closed():
                    with contextlib.suppress(Exception):
                        tab.close()
            tabs.main, tabs.named = main, named
            if not page.is_closed():
                tabs.last = page
            self.run, self.context = outer, outer_context
        full: Context = {**context, "facts": facts}
        checks = run_verify(callee, full)
        record.call["checks"] = [
            {"name": check.name, "passed": check.passed, "error": check.error} for check in checks
        ]
        failed = [check.name for check in checks if not check.passed]
        if failed:
            raise AssertionError(t("browser.call_verify_failed", names="、".join(failed)))
        outputs, output_problems = build_outputs(callee, full)
        if output_problems:
            raise ValueError(
                t(
                    "browser.call_outputs",
                    problems="；".join(item.message for item in output_problems),
                )
            )
        record.call["outputs"] = list(outputs)
        if step.as_ is not None and step.append:
            # 迴圈裡逐筆呼叫（同 extract 的 append）：每一次的出參加到清單尾端
            previous = outer.facts.get(step.as_)
            kept = cast("list[object]", previous) if isinstance(previous, list) else []
            outer.facts[step.as_] = [*kept, outputs]
        elif step.as_ is not None:
            outer.facts[step.as_] = outputs


def run_steps(
    page: Page,
    scenario: Scenario,
    *,
    records: list[StepRecord],
    context: Mapping[str, object],
    base_url: str | None,
    artifacts: Path,
    deadline: Deadline,
    on_progress: Callable[[], None] = lambda: None,
    tabs: Tabs | None = None,
    files: Mapping[str, Sequence[Path]] | None = None,
    after_step: Callable[[Page, StepRecord, int], None] | None = None,
    workspace: Path | None = None,
    calls: CallTable | None = None,
) -> dict[str, object]:
    """依序執行步驟並更新 records，回傳頁面事實；某一步失敗就拋出，後面的步驟維持略過。

    ``records`` 是 :func:`plan_records` 的結果；區塊裡的步驟執行到才插進去（M7.1）。
    ``tabs`` 給了時用它（呼叫的人之後要知道最後在哪個分頁，例如失敗截圖）；``page`` 是一開始的分頁。
    ``files`` 是檔案入參準備好的檔案（M7c，見 inputfiles.py）；``workspace`` 是共用工作資料夾
    （download 步驟存檔的地方，ADR 0020）。
    ``after_step`` 在每一步（通過或失敗，不含區塊本身）之後、寫出進度之前呼叫：
    (最後用到的分頁, 紀錄, 第幾筆紀錄)，錄影時拍那一步做完的截圖（見 stepshots.py）；
    它出錯不影響步驟的結果。``calls`` 是 ``call`` 用到的子場景（M7.2），由
    rpa_core.dsl.calls.load_calls 解析。
    """
    facts: dict[str, object] = {}
    run = _Run(
        tabs or Tabs(page),
        scenario,
        base_url,
        artifacts,
        facts,
        files or {},
        workspace,
        calls or {},
    )
    _Flow(run, records, context, deadline, on_progress, after_step).top(scenario.steps or [])
    return facts


def run_step(
    page: Page,
    scenario: Scenario,
    step: Step,
    *,
    facts: dict[str, object],
    context: Mapping[str, object],
    base_url: str | None,
    artifacts: Path,
    deadline: Deadline,
    tabs: Tabs | None = None,
    files: Mapping[str, Sequence[Path]] | None = None,
    workspace: Path | None = None,
    path: StepPath = (),
    variables: Mapping[str, object] | None = None,
    collected: list[StepRecord] | None = None,
    calls: CallTable | None = None,
) -> StepRecord:
    """只執行一步（調試工作階段用）：facts 就地更新；失敗不拋出，記在回傳的紀錄裡。

    ``tabs`` 是整個工作階段的分頁（M7b），新分頁在步驟之間一直都在；``files``、``workspace``
    見 run_steps。區塊整塊執行（M7.1）；``path`` 是這一步在場景檔裡的位置，``variables`` 是
    外層迴圈的變數（迴圈變數、loop、error），``collected`` 給了時收到這一步與區塊裡全部的紀錄。
    ``call`` 整個子場景一起執行（M7.2）；``calls`` 見 run_steps。
    """
    record = StepRecord(step.id, step.action, step.name, path=path, number=1)
    records = [record]
    run = _Run(
        tabs or Tabs(page),
        scenario,
        base_url,
        artifacts,
        facts,
        files or {},
        workspace,
        calls or {},
    )
    flow = _Flow(run, records, context, deadline, lambda: None, None, cursor=1)
    with contextlib.suppress(Exception):
        flow.execute(step, record, _Scope(dict(variables or {})))
    if collected is not None:
        collected.extend(records)
    return record
