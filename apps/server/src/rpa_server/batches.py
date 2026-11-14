"""批次執行（M7.3，ADR 0024）：用一張表的每一列，各正式執行一次發布過的場景版本。

流程：上傳或貼上表格 → 建立批次（draft，可以改欄位對應與選項，每一列先檢查入參）→ 開始
（running）→ 依「同時幾列」排入執行，每一次執行結束（:meth:`BatchService.row_finished`）就
排下一列 → 全部做完是 finished；「一列沒通過就停下」或手動停下是 stopped。之後可以只重跑
沒有通過的列（重跑前可以改那幾列的儲存格）。

每一列是一般的正式執行（runs，目的 execution），各有報告、出參與回看；版本在建立批次時固定。
排程每次都從資料庫重新算（哪幾列在跑、哪幾列還沒跑、這一輪有沒有失敗），同一個通知來兩次、
伺服器重啟後（:meth:`BatchService.recover`）都能接著走。表格的讀入與換算在
:mod:`rpa_server.batch_table`。
"""

import threading
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Final, Literal, cast
from urllib.parse import urlsplit

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from rpa_core.dsl import Scenario
from rpa_server.batch_table import (
    MAX_CELL,
    ExportRow,
    RowProblem,
    Table,
    cells_json,
    default_mapping,
    export_csv,
    export_xlsx,
    row_values,
)
from rpa_server.domain import FINISHED, Engine, RunRecord, Target, now
from rpa_server.errors import ServiceError, conflict, invalid, not_found
from rpa_server.i18n import t
from rpa_server.models import Batch, BatchRow, Run, Scene

if TYPE_CHECKING:
    from rpa_server.services import Services

__all__ = [
    "MAX_CONCURRENCY",
    "BatchRecord",
    "BatchRowRecord",
    "BatchService",
    "BatchStatus",
    "OnFailure",
]

BatchStatus = Literal["draft", "running", "finished", "stopped"]
OnFailure = Literal["continue", "stop"]
MAX_CONCURRENCY: Final = 10
_ACTIVE: Final = frozenset({"queued", "running"})
_NOT_PASSED: Final = FINISHED - {"passed"}
"""結束了卻沒有通過：失敗、逾時、取消、需要登入。"""


@dataclass(frozen=True, slots=True)
class BatchRowRecord:
    """批次的一列。``status``：pending（等待中）、invalid（資料有問題）、skipped（批次停下、
    沒有執行）、failed（排不進去，見 error），其餘是最近一次執行的狀態。"""

    number: int
    cells: dict[str, str]
    inputs: dict[str, object]
    problems: list[RowProblem]
    status: str
    run: RunRecord | None
    attempts: int
    error: str | None
    history: list[dict[str, object]] = field(default_factory=list[dict[str, object]])
    """這一列的每一次執行（最新的在前）：id、status、createdAt。"""

    @property
    def rerunnable(self) -> bool:
        """批次結束後「重跑沒有通過的列」會包含這一列。"""
        return self.status not in ("passed", "pending", "queued", "running")

    def to_json(self) -> dict[str, object]:
        run = self.run
        return {
            "number": self.number,
            "cells": self.cells,
            "inputs": self.inputs,
            "problems": [problem.to_json() for problem in self.problems],
            "status": self.status,
            "runId": run.id if run is not None else None,
            "output": run.output if run is not None else None,
            "error": self.error,
            "attempts": self.attempts,
            "durationSeconds": run.duration_seconds if run is not None else None,
            "runs": self.history,
        }


@dataclass(frozen=True, slots=True)
class BatchRecord:
    id: str
    scene_id: str
    scene_name: str
    revision: int
    status: BatchStatus
    on_failure: OnFailure
    concurrency: int
    engine: str | None
    base_url: str | None
    headless: bool | None
    target: str | None
    source: str | None
    columns: list[str]
    mapping: dict[str, str | None]
    error: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    client_id: str | None
    counts: dict[str, int]
    """每種狀態幾列（列表只有 total、passed、failed、active、notRun）。"""
    rows: list[BatchRowRecord] = field(default_factory=list[BatchRowRecord])

    @property
    def total(self) -> int:
        return self.counts.get("total", 0)

    def to_json(self, *, rows: bool = True) -> dict[str, object]:
        data: dict[str, object] = {
            "id": self.id,
            "sceneId": self.scene_id,
            "sceneName": self.scene_name,
            "revision": self.revision,
            "status": self.status,
            "onFailure": self.on_failure,
            "concurrency": self.concurrency,
            "engine": self.engine,
            "baseUrl": self.base_url,
            "headless": self.headless,
            "target": self.target,
            "source": self.source,
            "columns": self.columns,
            "mapping": self.mapping,
            "error": self.error,
            "createdAt": _iso(self.created_at),
            "startedAt": _iso(self.started_at),
            "finishedAt": _iso(self.finished_at),
            "clientId": self.client_id,
            "counts": self.counts,
        }
        if rows:
            data["rows"] = [row.to_json() for row in self.rows]
        return data


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def new_batch_id(moment: datetime | None = None) -> str:
    """批次編號：``batch-<UTC 日期>-<時間>-<6 碼亂數>``。"""
    moment = moment or datetime.now(UTC)
    return f"batch-{moment:%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:6]}"


class BatchService:
    def __init__(self, sessions: sessionmaker[Session], services: "Services") -> None:
        self.sessions = sessions
        self.services = services
        self._lock = threading.RLock()

    # ------------------------------------------------------------ 建立與設定

    def create(
        self,
        scene_id: str,
        table: Table,
        *,
        source: str | None = None,
        mapping: Mapping[str, str | None] | None = None,
        on_failure: str = "continue",
        concurrency: int = 1,
        engine: Engine | None = None,
        base_url: str | None = None,
        headless: bool | None = None,
        target: Target | None = None,
        client_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> BatchRecord:
        """建立批次（draft）：固定場景目前發布的版本，欄位沒指定時依標題對應。"""
        key = (idempotency_key or "").strip() or None
        with self.sessions() as session:
            if key is not None:
                found = session.scalars(select(Batch).where(Batch.idempotency_key == key)).first()
                if found is not None:
                    return self.get(found.id)
            scene = session.get(Scene, scene_id)
            if scene is None:
                raise not_found("scene_not_found", t("error.scene_not_found", id=scene_id))
            if scene.missing:
                raise conflict("scene_missing", t("error.scene_missing", id=scene_id))
            if scene.archived:
                raise conflict("scene_archived", t("error.scene_archived", id=scene_id))
            if scene.published_number is None:
                raise conflict("not_published", t("error.not_published", id=scene_id))
            number = scene.published_number
            name = scene.name
        scenario = self.services.revision_scenario(scene_id, number)
        chosen = _check_mapping(scenario, table.columns, mapping)
        moment = now()
        batch_id = new_batch_id()
        with self.sessions() as session:
            session.add(
                Batch(
                    id=batch_id,
                    scene_id=scene_id,
                    revision_number=number,
                    scene_name=name,
                    status="draft",
                    columns=list(table.columns),
                    mapping=dict(chosen),
                    source=(source or "").strip()[:255] or None,
                    on_failure=_check_on_failure(on_failure),
                    concurrency=_check_concurrency(concurrency),
                    engine=engine,
                    base_url=_check_base_url(base_url),
                    headless=headless,
                    target=target,
                    created_at=moment,
                    client_id=client_id,
                    idempotency_key=key,
                )
            )
            session.flush()
            session.add_all(
                BatchRow(
                    batch_id=batch_id,
                    number=index,
                    cells=dict(zip(table.columns, row, strict=True)),
                    attempts=0,
                )
                for index, row in enumerate(table.rows, start=1)
            )
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                found = session.scalars(select(Batch).where(Batch.idempotency_key == key)).first()
                if found is None:
                    raise
                batch_id = found.id
        return self.get(batch_id)

    def update(
        self,
        batch_id: str,
        *,
        mapping: Mapping[str, str | None] | None = None,
        on_failure: str | None = None,
        concurrency: int | None = None,
        engine: Engine | None = None,
        base_url: str | None = None,
        headless: bool | None = None,
        target: Target | None = None,
        fields: frozenset[str] = frozenset(),
    ) -> BatchRecord:
        """改欄位對應與選項（只有還沒開始的批次）。

        ``fields`` 是要求裡有寫的欄位：engine、base_url、headless、target 可以設回 null。
        """
        with self._lock, self.sessions() as session:
            batch = self._batch(session, batch_id)
            if batch.status != "draft":
                raise conflict("batch_not_draft", t("error.batch_not_draft", id=batch_id))
            if mapping is not None:
                scenario = self._scenario(batch)
                batch.mapping = dict(_check_mapping(scenario, batch.columns, mapping))
            if on_failure is not None:
                batch.on_failure = _check_on_failure(on_failure)
            if concurrency is not None:
                batch.concurrency = _check_concurrency(concurrency)
            if "engine" in fields:
                batch.engine = engine
            if "base_url" in fields:
                batch.base_url = _check_base_url(base_url)
            if "headless" in fields:
                batch.headless = headless
            if "target" in fields:
                batch.target = target
            session.commit()
        return self.get(batch_id)

    def delete(self, batch_id: str) -> None:
        """刪除還沒開始的批次。開始過的留著（執行紀錄引用它）。"""
        with self._lock, self.sessions() as session:
            batch = self._batch(session, batch_id)
            if batch.status != "draft":
                raise conflict("batch_not_draft", t("error.batch_not_draft", id=batch_id))
            # 先直接刪掉每一列再刪批次（兩張表之間沒有 relationship，ORM 不會自動排刪除的順序）
            session.execute(delete(BatchRow).where(BatchRow.batch_id == batch_id))
            session.delete(batch)
            session.commit()

    # ------------------------------------------------------------ 執行

    def start(self, batch_id: str) -> BatchRecord:
        """開始：沒有問題的列依「同時幾列」排入；資料有問題的列不執行。"""
        with self._lock:
            with self.sessions() as session:
                batch = self._batch(session, batch_id)
                if batch.status != "draft":
                    raise conflict("batch_not_draft", t("error.batch_not_draft", id=batch_id))
                target = self.services.resolve_target(cast("Target | None", batch.target))
                headless = self.services.resolve_headless(batch.headless, target)
                scenario = self._scenario(batch)
                mapping = _mapping(batch)
                rows = self._rows(session, batch_id)
                ready = [
                    row
                    for row in rows
                    if not row_values(scenario, mapping, cells_json(row.cells))[1]
                ]
                if not ready:
                    raise invalid("batch_no_valid_rows", t("error.batch_no_valid_rows"))
                batch.round_number = 1
                for row in ready:
                    row.round_number = 1
                batch.target = target
                batch.headless = headless
                batch.status = "running"
                batch.started_at = now()
                session.commit()
            self._advance(batch_id)
        return self.get(batch_id)

    def stop(self, batch_id: str) -> BatchRecord:
        """停下：不再排新的列，排隊中與執行中的取消（已經發生的外部動作不會復原）。"""
        with self._lock:
            with self.sessions() as session:
                batch = self._batch(session, batch_id)
                if batch.status != "running":
                    raise conflict("batch_not_running", t("error.batch_not_running", id=batch_id))
                batch.status = "stopped"
                batch.error = t("batch.stopped_by_user")
                batch.finished_at = now()
                active = list(
                    session.scalars(
                        select(Run.id).where(Run.batch_id == batch_id, Run.status.in_(_ACTIVE))
                    )
                )
                session.commit()
            for run_id in active:
                try:
                    self.services.cancel_run(run_id)
                except ServiceError:
                    continue
        return self.get(batch_id)

    def rerun(
        self,
        batch_id: str,
        *,
        rows: Sequence[int] | None = None,
        cells: Mapping[int, Mapping[str, str]] | None = None,
    ) -> BatchRecord:
        """再跑一次：沒指定時是沒有通過的列（失敗、逾時、取消、需要登入、沒有執行、排不進去、
        資料有問題）。``cells`` 先改那幾列的儲存格（只能改表格原有的欄位）；改了之後資料
        還是有問題的列不執行。"""
        with self._lock:
            with self.sessions() as session:
                batch = self._batch(session, batch_id)
                if batch.status not in ("finished", "stopped"):
                    raise conflict("batch_not_finished", t("error.batch_not_finished", id=batch_id))
                scenario = self._scenario(batch)
                mapping = _mapping(batch)
                found = self._rows(session, batch_id)
                by_number = {row.number: row for row in found}
                for number, changes in (cells or {}).items():
                    row = by_number.get(number)
                    if row is None:
                        raise invalid("batch_row_unknown", t("error.batch_row_unknown", row=number))
                    updated = cells_json(row.cells)
                    for column, value in changes.items():
                        if column not in batch.columns:
                            raise invalid(
                                "batch_column_unknown",
                                t("error.batch_column_unknown", column=column),
                            )
                        if len(value) > MAX_CELL:
                            raise invalid(
                                "batch_cell_too_long",
                                t("batch.table_cell", row=number, column=column, max=MAX_CELL),
                            )
                        updated[column] = value
                    row.cells = dict(updated)
                statuses = self._statuses(session, batch, found, scenario, mapping)
                if rows is None:
                    chosen = [row for row in found if statuses[row.number] not in _KEEP]
                else:
                    unknown = [number for number in rows if number not in by_number]
                    if unknown:
                        raise invalid(
                            "batch_row_unknown", t("error.batch_row_unknown", row=unknown[0])
                        )
                    chosen = [by_number[number] for number in sorted(set(rows))]
                ready = [
                    row
                    for row in chosen
                    if not row_values(scenario, mapping, cells_json(row.cells))[1]
                ]
                if not ready:
                    session.rollback()
                    raise invalid("batch_nothing_to_rerun", t("error.batch_nothing_to_rerun"))
                batch.round_number += 1
                for row in ready:
                    row.run_id = None
                    row.error = None
                    row.round_number = batch.round_number
                batch.status = "running"
                batch.error = None
                batch.started_at = now()
                batch.finished_at = None
                session.commit()
            self._advance(batch_id)
        return self.get(batch_id)

    def row_finished(self, run_id: str) -> None:
        """一列的執行結束了：排下一列、停下或完成。結果每次都從資料庫重新算。"""
        with self._lock:
            with self.sessions() as session:
                run = session.get(Run, run_id)
                if run is None or run.batch_id is None or run.status not in FINISHED:
                    return
                batch_id = run.batch_id
            self._advance(batch_id)

    def recover(self) -> int:
        """伺服器啟動時：還在執行中的批次依各列的結果接著走。"""
        with self.sessions() as session:
            running = list(session.scalars(select(Batch.id).where(Batch.status == "running")))
        for batch_id in running:
            with self._lock:
                self._advance(batch_id)
        return len(running)

    def _advance(self, batch_id: str) -> None:
        """依目前的結果往下走（呼叫端持有鎖）。

        只看這一輪（開始或重跑時選的列，round_number 與批次相同）：有沒有通過的列、而且要停下時，
        等在跑的跑完才停；否則補滿「同時幾列」。排不進去的列記下原因、算沒有通過，接著排下一列。
        """
        while True:
            with self.sessions() as session:
                batch = session.get(Batch, batch_id)
                if batch is None or batch.status != "running":
                    return
                scenario = self._scenario(batch)
                mapping = _mapping(batch)
                rows = self._rows(session, batch_id)
                runs = self._latest_runs(session, rows)
                current = [row for row in rows if row.round_number == batch.round_number]
                active = [
                    row
                    for row in rows
                    if row.run_id is not None and runs[row.run_id].status in _ACTIVE
                ]
                failed = [
                    row
                    for row in current
                    if row.error is not None
                    or (row.run_id is not None and runs[row.run_id].status in _NOT_PASSED)
                ]
                todo = [
                    (row.number, row.attempts, row_values(scenario, mapping, cells_json(row.cells)))
                    for row in current
                    if row.run_id is None and row.error is None
                ]
                todo = [item for item in todo if not item[2][1]]
                stop_on_failure = batch.on_failure == "stop"
                slots = batch.concurrency - len(active)
                options = (
                    batch.scene_id,
                    batch.revision_number,
                    cast("Engine | None", batch.engine),
                    batch.base_url,
                    batch.headless,
                    cast("Target | None", batch.target),
                    batch.client_id,
                )
            if stop_on_failure and failed:
                if not active:
                    self._finish(
                        batch_id, "stopped", t("batch.stopped_on_failure", row=failed[0].number)
                    )
                return
            if not todo and not active:
                self._finish(batch_id, "finished", None)
                return
            again = False
            for number, attempts, (values, _) in todo[: max(0, slots)]:
                if not self._queue(batch_id, number, attempts + 1, values, options):
                    again = True  # 排不進去：重新算（可能要停下，也可能換下一列）
                    break
            if not again:
                return

    def _queue(
        self,
        batch_id: str,
        number: int,
        attempt: int,
        values: Mapping[str, object],
        options: tuple[str, int, Engine | None, str | None, bool | None, Target | None, str | None],
    ) -> bool:
        scene_id, revision, engine, base_url, headless, target, client_id = options
        try:
            run = self.services.request_run(
                scene_id,
                purpose="execution",
                number=revision,
                inputs=values,
                engine=engine,
                base_url=base_url,
                idempotency_key=f"{batch_id}-{number}-{attempt}",
                headless=headless,
                target=target,
                client_id=client_id,
                batch=(batch_id, number),
            )
        except ServiceError as error:
            details = error.details.get("problems")
            items = [
                str(cast("dict[str, object]", item).get("message"))
                for item in (cast("list[object]", details) if isinstance(details, list) else [])
                if isinstance(item, dict)
            ]
            message = t("js.list_separator").join(items) if items else error.message
            with self.sessions() as session:
                row = self._row(session, batch_id, number)
                row.error = t("batch.row_not_started", detail=message)
                session.commit()
            return False
        with self.sessions() as session:
            row = self._row(session, batch_id, number)
            row.run_id = run.id
            row.attempts = attempt
            session.commit()
        return True

    def _finish(self, batch_id: str, status: BatchStatus, error: str | None) -> None:
        with self.sessions() as session:
            batch = session.get(Batch, batch_id)
            if batch is None or batch.status != "running":
                return
            batch.status = status
            batch.error = error
            batch.finished_at = now()
            session.commit()

    # ------------------------------------------------------------ 讀取

    def find_by_key(self, key: str) -> str | None:
        """用過這個冪等鍵的批次編號。"""
        with self.sessions() as session:
            return session.scalars(select(Batch.id).where(Batch.idempotency_key == key)).first()

    def get(self, batch_id: str) -> BatchRecord:
        from rpa_server.services import run_record

        with self.sessions() as session:
            batch = self._batch(session, batch_id)
            scenario = self._scenario(batch)
            mapping = _mapping(batch)
            rows = self._rows(session, batch_id)
            runs = self._latest_runs(session, rows)
            history: dict[int, list[dict[str, object]]] = {}
            for run in session.scalars(
                select(Run)
                .where(Run.batch_id == batch_id)
                .order_by(Run.created_at.desc(), Run.id.desc())
            ):
                if run.batch_row is not None:
                    history.setdefault(run.batch_row, []).append(
                        {
                            "id": run.id,
                            "status": run.status,
                            "createdAt": _iso(_aware(run.created_at)),
                        }
                    )
            records: list[BatchRowRecord] = []
            for row in rows:
                cells = cells_json(row.cells)
                values, problems = row_values(scenario, mapping, cells)
                run = runs.get(row.run_id) if row.run_id is not None else None
                records.append(
                    BatchRowRecord(
                        number=row.number,
                        cells=cells,
                        inputs=values,
                        problems=problems,
                        status=_row_status(batch, row, run, problems),
                        run=run_record(run) if run is not None else None,
                        attempts=row.attempts,
                        error=row.error if row.error is not None else run.error if run else None,
                        history=history.get(row.number, []),
                    )
                )
            counts: dict[str, int] = {"total": len(records)}
            for record in records:
                counts[record.status] = counts.get(record.status, 0) + 1
            return _record(batch, counts, records)

    def recent(
        self,
        *,
        scene_id: str | None = None,
        client_id: str | None = None,
        limit: int = 100,
    ) -> list[BatchRecord]:
        """最近的批次（最新的在前），不含每一列。

        counts 只有 total、passed、failed、active、notRun（沒有排入過的列，含資料有問題的）。
        """
        with self.sessions() as session:
            statement = select(Batch).order_by(Batch.created_at.desc(), Batch.id.desc())
            if scene_id is not None:
                statement = statement.where(Batch.scene_id == scene_id)
            if client_id is not None:
                statement = statement.where(Batch.client_id == client_id)
            batches = list(session.scalars(statement.limit(limit)))
            ids = [batch.id for batch in batches]
            tallies: dict[str, dict[str, int]] = {batch_id: {} for batch_id in ids}
            if ids:
                grouped = session.execute(
                    select(BatchRow.batch_id, Run.status, func.count())
                    .select_from(BatchRow)
                    .outerjoin(Run, Run.id == BatchRow.run_id)
                    .where(BatchRow.batch_id.in_(ids))
                    .group_by(BatchRow.batch_id, Run.status)
                )
                for batch_id, found, count in grouped:
                    status = cast("str | None", found)  # 外連接：還沒排入的列是 NULL
                    tally = tallies[batch_id]
                    key = (
                        "passed"
                        if status == "passed"
                        else "active"
                        if status in _ACTIVE
                        else "notRun"
                        if status is None
                        else "failed"
                    )
                    tally[key] = tally.get(key, 0) + count
                    tally["total"] = tally.get("total", 0) + count
            return [_record(batch, tallies[batch.id], []) for batch in batches]

    def export(self, batch_id: str, kind: Literal["csv", "xlsx"]) -> tuple[str, str, bytes]:
        """匯出結果：(檔名, 媒體類型, 內容)。"""
        record = self.get(batch_id)
        scenario = self.services.revision_scenario(record.scene_id, record.revision)
        outputs = list(scenario.outputs)
        rows = [
            ExportRow(
                number=row.number,
                cells=row.cells,
                status=row.status,
                run_id=row.run.id if row.run is not None else None,
                output=row.run.output if row.run is not None else None,
                error=row.error
                or ("；".join(item.message for item in row.problems) if row.problems else None),
                attempts=row.attempts,
            )
            for row in record.rows
        ]
        if kind == "xlsx":
            data = export_xlsx(record.columns, outputs, rows)
            media = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            data = export_csv(record.columns, outputs, rows)
            media = "text/csv; charset=utf-8"
        return f"{record.id}.{kind}", media, data

    # ------------------------------------------------------------ 共用

    def _batch(self, session: Session, batch_id: str) -> Batch:
        batch = session.get(Batch, batch_id)
        if batch is None:
            raise not_found("batch_not_found", t("error.batch_not_found", id=batch_id))
        return batch

    @staticmethod
    def _rows(session: Session, batch_id: str) -> list[BatchRow]:
        return list(
            session.scalars(
                select(BatchRow).where(BatchRow.batch_id == batch_id).order_by(BatchRow.number)
            )
        )

    @staticmethod
    def _row(session: Session, batch_id: str, number: int) -> BatchRow:
        return session.scalars(
            select(BatchRow).where(BatchRow.batch_id == batch_id, BatchRow.number == number)
        ).one()

    @staticmethod
    def _latest_runs(session: Session, rows: Sequence[BatchRow]) -> dict[str, Run]:
        ids = [row.run_id for row in rows if row.run_id is not None]
        found: dict[str, Run] = {}
        for start in range(0, len(ids), 500):
            chunk = ids[start : start + 500]
            found.update(
                (run.id, run) for run in session.scalars(select(Run).where(Run.id.in_(chunk)))
            )
        return found

    def _scenario(self, batch: Batch) -> Scenario:
        return self.services.revision_scenario(batch.scene_id, batch.revision_number)

    def _statuses(
        self,
        session: Session,
        batch: Batch,
        rows: Sequence[BatchRow],
        scenario: Scenario,
        mapping: Mapping[str, str | None],
    ) -> dict[int, str]:
        runs = self._latest_runs(session, rows)
        return {
            row.number: _row_status(
                batch,
                row,
                runs.get(row.run_id) if row.run_id is not None else None,
                row_values(scenario, mapping, cells_json(row.cells))[1],
            )
            for row in rows
        }


_KEEP: Final = frozenset({"passed", "queued", "running", "pending"})
"""沒指定重跑哪幾列時不重跑的狀態。"""


def _row_status(
    batch: Batch, row: BatchRow, run: Run | None, problems: Sequence[RowProblem]
) -> str:
    """一列的狀態：有執行就是那次執行的狀態；還沒開始的批次與這一輪還沒排入的列是 pending；
    沒被選進這一輪、也從來沒有執行的列是 skipped。"""
    if run is not None:
        return run.status
    if row.error is not None:
        return "failed"
    if problems:
        return "invalid"
    if batch.status == "draft" or (
        batch.status == "running" and row.round_number == batch.round_number
    ):
        return "pending"
    return "skipped"


def _record(batch: Batch, counts: dict[str, int], rows: list[BatchRowRecord]) -> BatchRecord:
    return BatchRecord(
        id=batch.id,
        scene_id=batch.scene_id,
        scene_name=batch.scene_name,
        revision=batch.revision_number,
        status=cast("BatchStatus", batch.status),
        on_failure=cast("OnFailure", batch.on_failure),
        concurrency=batch.concurrency,
        engine=batch.engine,
        base_url=batch.base_url,
        headless=batch.headless,
        target=batch.target,
        source=batch.source,
        columns=list(batch.columns),
        mapping=_mapping(batch),
        error=batch.error,
        created_at=_aware(batch.created_at),
        started_at=_aware(batch.started_at) if batch.started_at is not None else None,
        finished_at=_aware(batch.finished_at) if batch.finished_at is not None else None,
        client_id=batch.client_id,
        counts=counts,
        rows=rows,
    )


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


def _mapping(batch: Batch) -> dict[str, str | None]:
    return {
        str(name): column if isinstance(column, str) else None
        for name, column in cast("dict[object, object]", batch.mapping).items()
    }


def _check_mapping(
    scenario: Scenario, columns: Sequence[str], mapping: Mapping[str, str | None] | None
) -> dict[str, str | None]:
    """入參 → 欄位：沒給的入參依標題自動對應；入參與欄位都要存在。"""
    chosen = default_mapping(scenario, columns)
    if mapping is None:
        return chosen
    for name, column in mapping.items():
        if name not in scenario.inputs:
            raise invalid("batch_input_unknown", t("error.batch_input_unknown", name=name))
        if column is not None and column not in columns:
            raise invalid("batch_column_unknown", t("error.batch_column_unknown", column=column))
        chosen[name] = column
    return chosen


def _check_on_failure(value: str) -> OnFailure:
    if value not in ("continue", "stop"):
        raise invalid("batch_on_failure", t("error.batch_on_failure", value=value))
    return value


def _check_concurrency(value: int) -> int:
    if not 1 <= value <= MAX_CONCURRENCY:
        raise invalid(
            "batch_concurrency", t("error.batch_concurrency", value=value, max=MAX_CONCURRENCY)
        )
    return value


def _check_base_url(value: str | None) -> str | None:
    if value is None or not value.strip():
        return None
    value = value.strip()
    parts = urlsplit(value)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise invalid("base_url_invalid", t("error.base_url_invalid", value=value))
    return value
