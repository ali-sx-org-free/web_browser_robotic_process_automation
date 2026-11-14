"""automation.log 的內容：自動化階段的逐步紀錄（DSL 場景），給人讀。

自動化子程序（child.py）把這些行寫到標準輸出，父程序把標準輸出與標準錯誤一起存成
automation.log；Playwright 印出的訊息也會夾在中間。格式（目前語言）：

    自動化日誌：ba-001 新增紀錄
    這份檔案逐步記下……
    執行編號 … · 瀏覽器 Chromium · 有頭（顯示視窗）· 起始網址 http://…
    開始時間 2026-10-25 21:30:12（這台電腦的時間，UTC−07:00）

    21:30:13.902  瀏覽器已開啟，共 5 步
    21:30:14.714  第 1/5 步  打開首頁（goto）  通過  812 ms
                  網址 http://127.0.0.1:8765/
    21:30:45.100  第 3/5 步  送出（click）  失敗  30000 ms
                  錯誤 TimeoutError: Locator.click: Timeout 30000ms exceeded.
                  略過 第 4～5 步（前一步失敗）

    21:30:45.120  失敗：第 3 步「送出」，……

時間是執行這次運行的那台電腦的當地時間。網址與錯誤都遮罩 Secrets 的值；不寫入參的值
（在 input.json）。每寫一行就 flush，執行到一半也看得到進度。

區塊步驟（M7.1）開始時先寫一行，結束時再寫結果（走哪個分支、跑了幾輪、接住了什麼）；
區塊裡的步驟縮排，以「›」開頭，迴圈裡的標出第幾輪::

    21:30:14.900  第 3/6 步  each（forEach）  開始
    21:30:15.310    › 填寫標題（fill）（第 1 輪）  通過  402 ms
    21:30:16.020  第 3/6 步  each（forEach）  通過  1120 ms
                  共執行 2 輪
"""

import time
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timedelta
from typing import Final, TextIO

from rpa_core.dsl import Scenario
from rpa_runner.browser import StepRecord
from rpa_runner.i18n import t
from rpa_runner.installed import DISPLAY_NAMES
from rpa_runner.secrets import mask

__all__ = ["StepLog"]

_INDENT: Final = " " * 14
"""明細行對齊時間後面的文字（「HH:MM:SS.mmm」加兩個空白）。"""
_BLOCKS: Final = frozenset({"if", "forEach", "repeat", "try"})
_NESTED: Final = "  "
"""區塊裡每多一層多縮排的空白。"""


def _offset(moment: datetime) -> str:
    """UTC 偏移，例如 UTC−07:00、UTC+08:00（減號用 U+2212，和文件的寫法一致）。"""
    delta = moment.utcoffset() or timedelta(0)
    minutes = int(delta.total_seconds() // 60)
    sign = "+" if minutes >= 0 else "−"
    minutes = abs(minutes)
    return f"UTC{sign}{minutes // 60:02d}:{minutes % 60:02d}"


class StepLog:
    """寫 automation.log 的一行行內容；``stream`` 通常是子程序的標準輸出。"""

    def __init__(
        self,
        stream: TextIO,
        *,
        secrets: Mapping[str, str],
        clock: Callable[[], float] = time.time,
    ) -> None:
        self.stream = stream
        self.secrets = secrets
        self.clock = clock
        self.started = clock()
        self.logged = 0
        self._started: set[int] = set()
        self._ended: set[int] = set()
        self._total = 0

    # ------------------------------------------------------------ 輸出

    def _write(self, *lines: str) -> None:
        self.stream.write("".join(line + "\n" for line in lines))
        self.stream.flush()

    def _now(self, moment: float | None = None) -> str:
        local = datetime.fromtimestamp(self.clock() if moment is None else moment).astimezone()
        return local.strftime("%H:%M:%S.") + f"{local.microsecond // 1000:03d}"

    def _mask(self, text: str) -> str:
        return mask(text, self.secrets)

    # ------------------------------------------------------------ 段落

    def header(
        self,
        scenario: Scenario,
        *,
        run_id: str,
        engine: str,
        headed: bool,
        base_url: str | None,
    ) -> None:
        """檔案開頭：這是什麼、這次的設定、開始時間。"""
        start = datetime.fromtimestamp(self.started).astimezone()
        window = t("steplog.window_headed") if headed else t("steplog.window_headless")
        url = self._mask(base_url) if base_url else t("steplog.no_url")
        self._write(
            t("steplog.title", id=scenario.id, name=scenario.name),
            t("steplog.about"),
            t(
                "steplog.meta",
                run_id=run_id,
                engine=DISPLAY_NAMES.get(engine, engine),
                window=window,
                url=url,
            ),
            t(
                "steplog.started",
                time=start.strftime("%Y-%m-%d %H:%M:%S"),
                offset=_offset(start),
            ),
            "",
        )

    def browser_ready(self, total: int) -> None:
        self._write(f"{self._now()}  " + t("steplog.browser", total=total))

    def progress(self, records: Sequence[StepRecord]) -> None:
        """記下剛開始的區塊與剛結束的步驟（run_steps 每一步開始區塊、結束時呼叫），依時間排序。"""
        view = _View(records)
        self._total = view.total
        events: list[tuple[float, int, int, StepRecord]] = []
        for position, record in enumerate(records):
            key = id(record)
            started = record.started_at
            if record.action in _BLOCKS and started is not None and key not in self._started:
                events.append((started, 0, position, record))
            if record.ended_at is not None and key not in self._ended:
                events.append((record.ended_at, 1, position, record))
        events.sort(key=lambda event: event[:3])
        for _, kind, _, record in events:
            if kind == 0:
                self._started.add(id(record))
                self._block_start(view, record)
            else:
                self._ended.add(id(record))
                if record.parent is None:
                    self.logged += 1
                self._step(view, record)

    def _head(self, view: "_View", record: StepRecord, status: str, ms: int | None) -> str:
        name = record.name or record.id
        depth = view.depth(record)
        if depth == 0:
            if ms is None:
                return t(
                    "steplog.block_start",
                    n=view.ordinal(record),
                    total=view.total,
                    name=name,
                    action=record.action,
                )
            return t(
                "steplog.step",
                n=view.ordinal(record),
                total=view.total,
                name=name,
                action=record.action,
                status=status,
                ms=ms,
            )
        round_ = t("steplog.round", n=record.iteration) if record.iteration is not None else ""
        prefix = _NESTED * depth
        if ms is None:
            return prefix + t(
                "steplog.nested_block_start", name=name, action=record.action, round=round_
            )
        return prefix + t(
            "steplog.nested_step",
            name=name,
            action=record.action,
            round=round_,
            status=status,
            ms=ms,
        )

    def _block_start(self, view: "_View", record: StepRecord) -> None:
        line = self._head(view, record, "", None)
        self._write(f"{self._now(record.started_at)}  {line}")

    def _step(self, view: "_View", record: StepRecord) -> None:
        if record.status == "passed":
            status = t("steplog.passed")
        elif record.handled == "continued":
            status = t("steplog.failed_continued")
        elif record.handled == "caught":
            status = t("steplog.failed_caught")
        else:
            status = t("steplog.failed")
        indent = _INDENT + _NESTED * view.depth(record)
        head = self._head(view, record, status, record.duration_ms)
        lines = [f"{self._now(record.ended_at)}  {head}"]
        if record.error:
            lines.append(indent + t("steplog.error", error=self._mask(record.error)))
        if record.url and (record.action == "goto" or record.status != "passed"):
            # 每一步都印網址太吵：只在打開網頁與出錯時印（每一步的網址在 steps.json）
            lines.append(indent + t("steplog.url", url=self._mask(record.url)))
        for name in record.artifacts:
            lines.append(indent + t("steplog.artifact", file=name))
        if record.files:
            lines.append(indent + t("steplog.files", files=", ".join(record.files)))
        for note in record.notes:
            lines.append(indent + t("steplog.note", note=self._mask(note)))
        if record.attempts > 1 and record.status == "passed":
            lines.append(indent + t("steplog.attempts", n=record.attempts))
        lines.extend(indent + line for line in self._summary(record))
        number = view.ordinal(record)
        if (
            record.parent is None
            and record.status != "passed"
            and record.handled is None
            and number < view.total
        ):
            first, last = number + 1, view.total
            key = "steplog.skipped_one" if first == last else "steplog.skipped"
            lines.append(indent + t(key, first=first, last=last))
        self._write(*lines)

    def _summary(self, record: StepRecord) -> list[str]:
        """區塊的結果：走哪個分支、跑了幾輪、接住了什麼（M7.1）。"""
        lines: list[str] = []
        if record.action == "if" and record.condition is not None:
            if record.branch == "then":
                lines.append(t("steplog.branch_then"))
            elif record.branch == "else":
                lines.append(t("steplog.branch_else"))
            else:
                lines.append(t("steplog.branch_none"))
        if record.iterations is not None:
            lines.append(t("steplog.iterations", n=record.iterations))
        if record.caught is not None:
            lines.append(
                t(
                    "steplog.caught",
                    step=record.caught.get("step", "?"),
                    error=self._mask(record.caught.get("error", "")),
                )
            )
        return lines

    def finished(self, facts: Mapping[str, object]) -> None:
        """全部步驟通過：總結、抽取到哪些事實、下一階段。"""
        seconds = f"{self.clock() - self.started:.1f}"
        lines = ["", f"{self._now()}  " + t("steplog.done", total=self._total, seconds=seconds)]
        if facts:
            lines.append(_INDENT + t("steplog.facts", names=", ".join(facts)))
        lines.append(_INDENT + t("steplog.next"))
        self._write(*lines)

    def failed(
        self, records: Sequence[StepRecord], error: BaseException, *, timed_out: bool
    ) -> None:
        """失敗或逾時：停在哪一步、證據在哪裡；最後附上完整的錯誤原文。"""
        self.progress(records)
        seconds = f"{self.clock() - self.started:.1f}"
        view = _View(records)
        # 讓整次執行停下的那一步：沒有被接住、不是區塊本身（區塊裡的失敗算到最內層那一步）
        unhandled = [r for r in records if r.status == "failed" and r.handled is None]
        leaf = next((r for r in unhandled if r.action not in _BLOCKS), None)
        culprit = leaf or next(iter(unhandled), None)
        failed = (view.ordinal(view.root(culprit)), culprit) if culprit is not None else None
        if failed is None:
            key = "steplog.timed_out_before" if timed_out else "steplog.failed_before"
            summary = t(key, seconds=seconds)
        else:
            number, record = failed
            key = "steplog.timed_out_step" if timed_out else "steplog.failed_step"
            summary = t(key, n=number, name=record.name or record.id, seconds=seconds)
        detail = self._mask(f"{type(error).__name__}: {error}")
        self._write(
            "",
            f"{self._now()}  {summary}",
            _INDENT + t("steplog.evidence"),
            "",
            t("steplog.details"),
            detail,
        )


class _View:
    """步驟紀錄的巢狀關係（M7.1）：最外層第幾步、第幾層。"""

    def __init__(self, records: Sequence[StepRecord]) -> None:
        self.records = records
        top = [record for record in records if record.parent is None]
        self.total = len(top)
        self._ordinals = {id(record): number for number, record in enumerate(top, 1)}

    def parent(self, record: StepRecord) -> StepRecord | None:
        number = record.parent
        if number is None or not 1 <= number <= len(self.records):
            return None
        return self.records[number - 1]

    def root(self, record: StepRecord) -> StepRecord:
        current = record
        while (outer := self.parent(current)) is not None:
            current = outer
        return current

    def depth(self, record: StepRecord) -> int:
        depth, current = 0, record
        while (outer := self.parent(current)) is not None:
            depth, current = depth + 1, outer
        return depth

    def ordinal(self, record: StepRecord) -> int:
        """最外層的第幾步（區塊裡的步驟算它所在的最外層步驟）。"""
        return self._ordinals.get(id(self.root(record)), 0)
