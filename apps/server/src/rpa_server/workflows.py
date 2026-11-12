"""自由試驗場：組合場景以 DAG 表達依賴，依依賴排程執行。

第 1 版保留原有順序；第 2 版先固定同名匹配，再依依賴排程。畫布位置不影響執行。

組合場景的流程（2026-11-11）：排程由 :func:`rpa_core.workflow.advance` 從每個節點的結果算出，
同時就緒的節點最多 ``concurrency`` 個一起排入佇列；條件連線沒走到的節點略過；重複的節點
一次通過就排下一次，全部次數通過才算通過。``concurrency`` 大於 1 時節點不再全部給同一台
worker，由空著的 worker 各自領取；只有用到上游檔案出參的節點留在跑那個上游的 worker
（共用工作資料夾，ADR 0020），指定了 worker 或從失敗的節點繼續時仍全部給它。

- **組合場景**（workflows）：名稱、說明與 rpa_core.workflow 的定義；每次存檔 version 加一，
  存檔要帶目前的 version，不一致就回 409。定義有問題也可以存（編輯到一半），但不能執行。
- **組合場景的執行**（workflow_runs）：開始時存一份定義的快照；可以開始的節點排入佇列，
  worker 每執行完一個節點就呼叫 :meth:`WorkflowService.node_finished`：通過就取出參、排接下來
  的節點，沒有通過（失敗、逾時、取消、需要登入）就停在那個節點：不再排新的節點，已經在跑的
  跑完。
- **節點的執行**就是一般的執行（runs，目的 workflow）：有自己的執行目錄、報告，也出現在執行報告。
- **重新執行**用同一份快照從頭開始；**從失敗的節點繼續**沿用前面已通過節點的出參，
  不重複前面的操作（例如建立紀錄），適合登入之後接著跑。
- 單機、組合場景執行：節點的執行一個一個排進同一個佇列，與其他執行依建立時間先後執行。

M11 PR 2：組合場景放在領域資料夾的 composites/<代號>/（:mod:`rpa_server.packs`）。

- **版本**：每次改定義都是新版本（version 是最新的版本號碼）；名稱與說明不分版本。
- **驗證與執行**：驗證跑某個版本（預設最新），結束時寫驗證紀錄；執行只跑發布的版本。
- **發布**：有雜湊相符的通過驗證紀錄（每個節點跑的場景版本也相符），而且釘住的場景版本現在
  都還在、雜湊相同。
- **依賴**：最新與發布的版本釘住的場景版本、場景用到的角色與 Secrets；不完整時不能執行。

專案空間（2026-10-23）：組合場景可以屬於一個專案（project_id，只在資料庫），專案頁只列那個專案的
組合場景與它們的執行；還沒分到專案的組合場景在專案管理列出。

對外 Agent API（M14）：組合場景的執行記下觸發的用戶端（client_id），節點的執行也記同一個；
Agent 存的版本說明由呼叫端帶（note）。路由在 :mod:`rpa_server.agent_projects`。

所有改變組合場景執行狀態的操作都在同一把鎖裡（worker 的回報與頁面的取消可能同時發生）。
"""

import logging
import os
import re
import threading
from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Final, Literal, cast

from sqlalchemy import ColumnElement, and_, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from rpa_core.dsl import Scenario
from rpa_core.pack import (
    COMPOSITES_DIR,
    CompositeManifest,
    PublishedRef,
    SceneRequirement,
    parse_timestamp,
    timestamp,
    workflow_text,
)
from rpa_core.workflow import (
    NodeState,
    OutputBinding,
    Progress,
    Workflow,
    WorkflowNode,
    WorkflowProblem,
    advance,
    check_workflow,
    input_sources,
    parse_workflow,
    plan_workflow,
    resolve_inputs,
)
from rpa_runner.run import new_run_id
from rpa_server.domain import (
    FINISHED,
    LOCAL_WORKER,
    CompositeRevisionRecord,
    DependencyItem,
    DependencyStatus,
    Engine,
    NodeStatus,
    RevisionStatus,
    RunRecord,
    Target,
    VerificationRecord,
    WorkflowNodeState,
    WorkflowRecord,
    WorkflowRunRecord,
    WorkflowRunStatus,
    now,
    scene_display_kind,
)
from rpa_server.errors import ServiceError, conflict, invalid, not_found
from rpa_server.i18n import t
from rpa_server.models import Domain, Revision, Role, Run, Scene, WorkflowRevision
from rpa_server.models import Workflow as WorkflowRow
from rpa_server.models import WorkflowRun as WorkflowRunRow

if TYPE_CHECKING:
    from rpa_server.services import Services

__all__ = ["RUN_LIST_LIMIT", "WorkflowService"]

logger = logging.getLogger("rpa_server")

RUN_LIST_LIMIT: Final = 50
"""組合場景執行清單最多顯示的筆數。"""

_NAME_LIMIT: Final = 200
_CODE: Final = re.compile(r"[a-z0-9][a-z0-9_-]{0,63}")
"""組合場景代號的規則（和場景 id 相同）。"""
Purpose = Literal["validation", "execution"]


@dataclass(frozen=True, slots=True)
class _RunStatus:
    """:meth:`WorkflowService._status` 的結果。"""

    states: Mapping[str, NodeState]
    """有結果或在跑的節點；沒列的是還沒開始。"""
    outputs: Mapping[str, Mapping[str, object] | None]
    iterations: Mapping[str, int]
    """節點 → 已經通過幾次。"""
    runs: Mapping[str, list[Run]]
    """節點 → 這次組合場景執行裡的每一次執行。"""
    again: tuple[str, ...]
    """這次通過了、還要再跑的節點。"""
    failed: Run | None
    """最早沒有通過的那次執行。"""
    active: int
    """排隊或執行中的節點數。"""
    progress: Progress


def _run_record(run: Run) -> RunRecord:
    from rpa_server.services import run_record  # services 匯入本模組，執行時才取用避免循環

    return run_record(run)


class WorkflowService:
    def __init__(self, sessions: sessionmaker[Session], services: "Services") -> None:
        self.sessions = sessions
        self.services = services
        self._lock = threading.RLock()
        self._scenarios: dict[tuple[str, int], Scenario | None] = {}
        """(場景, 版本) → 場景；版本內容不可變，可以一直快取。"""

    # ------------------------------------------------------------ 場景版本

    def _scenario(self, scene_id: str, number: int) -> Scenario | None:
        key = (scene_id, number)
        if key not in self._scenarios:
            try:
                self._scenarios[key] = self.services.revision_scenario(scene_id, number)
            except ServiceError:
                return None
        return self._scenarios[key]

    def check(self, workflow: Workflow) -> list[WorkflowProblem]:
        """執行前的檢查：場景存在、沒有封存、固定的版本發布過，再加上 rpa_core 的靜態檢查。"""
        problems: list[WorkflowProblem] = []
        scenarios: dict[str, Scenario | None] = {}
        with self.sessions() as session:
            for node in workflow.nodes:
                problem = self._node_problem(session, node)
                if problem is not None:
                    problems.append(problem)
                    scenarios[node.id] = None
                else:
                    scenarios[node.id] = self._scenario(node.scene_id, node.revision)
        return problems + check_workflow(workflow, scenarios)

    @staticmethod
    def _node_problem(session: Session, node: WorkflowNode) -> WorkflowProblem | None:
        params = {"node": node.id, "scene": node.scene_id, "revision": node.revision}
        scene = session.get(Scene, node.scene_id)
        revision = session.scalars(
            select(Revision).where(
                Revision.scene_id == node.scene_id, Revision.number == node.revision
            )
        ).first()
        if scene is None or scene.missing:
            code = "scene_missing"
        elif scene.archived:
            code = "scene_archived"
        elif revision is None or revision.missing or revision.problem is not None:
            code = "revision_missing"
        elif revision.published_at is None:
            code = "revision_unpublished"
        else:
            return None
        return WorkflowProblem(f"workflow.{code}", t(f"workflow.{code}", **params), node.id)

    def parse(self, data: object) -> tuple[Workflow | None, list[WorkflowProblem]]:
        """API 送來的定義 → (組合場景, 問題)；格式不對時組合場景是 None。"""
        workflow, problems = parse_workflow(data)
        if workflow is None:
            return None, problems
        return workflow, self.check(workflow)

    def library(self) -> list[dict[str, object]]:
        """編輯組合場景時的場景庫：有發布過版本的場景，每個發布過的版本的入參與出參。

        封存的場景也列出（標示 archived），讓組合場景裡已經用到的節點還能顯示；
        場景庫本身不列出它們。
        """
        with self.sessions() as session:
            published = list(
                session.scalars(
                    select(Revision)
                    .where(Revision.published_at.is_not(None), Revision.missing.is_(False))
                    .order_by(Revision.scene_id, Revision.number.desc())
                )
            )
            scenes = {
                scene.id: scene
                for scene in session.scalars(
                    select(Scene).where(Scene.id.in_({row.scene_id for row in published}))
                )
            }
        names = {domain.id: domain.name for domain in self.services.list_domains()}
        entries: dict[str, dict[str, object]] = {}
        for revision in published:
            scene = scenes[revision.scene_id]
            if scene.missing:  # 領域資料夾裡已經沒有這個場景（M11）
                continue
            entry = entries.setdefault(
                scene.id,
                {
                    "id": scene.id,
                    "name": scene.name,
                    "category": scene.category,
                    "createdAt": scene.created_at.isoformat(),
                    "domainId": scene.domain_id,
                    "domainName": names.get(scene.domain_id or ""),
                    "publishedRevision": scene.published_number,
                    "archived": scene.archived,
                    "revisions": [],
                },
            )
            scenario = self._scenario(scene.id, revision.number)
            if scenario is None:
                continue
            cast("list[dict[str, object]]", entry["revisions"]).append(
                {
                    "number": revision.number,
                    "name": scenario.name,
                    "kind": revision.kind,
                    "displayKind": scene_display_kind(scenario),
                    "inputs": _specs(scenario, "inputs"),
                    "outputs": _specs(scenario, "outputs"),
                    "role": scenario.login.role if scenario.login is not None else None,
                }
            )
        return sorted(entries.values(), key=lambda item: str(item["id"]))

    # ------------------------------------------------------------ 組合場景

    @staticmethod
    def _row(session: Session, workflow_id: int) -> WorkflowRow:
        row = session.get(WorkflowRow, workflow_id)
        if row is None:
            raise not_found("workflow_not_found", t("error.workflow_not_found", id=workflow_id))
        return row

    def _record(self, row: WorkflowRow, *, with_last_run: bool = True) -> WorkflowRecord:
        workflow, problems = parse_workflow(row.definition)
        if workflow is None:  # 資料庫裡的定義都經過校驗；萬一壞了也要能打開頁面修正
            workflow = Workflow()
        else:
            problems = self.check(workflow)
        last = None
        if with_last_run:
            runs = self.list_runs(workflow_id=row.id, limit=1)
            last = runs[0] if runs else None
        return WorkflowRecord(
            id=row.id,
            name=row.name,
            description=row.description,
            workflow=workflow,
            version=row.version,
            created_at=row.created_at,
            updated_at=row.updated_at,
            problems=tuple(problems),
            last_run=last,
            code=row.code,
            domain_id=row.domain_id,
            published_number=row.published_number,
            archived=row.archived,
            dependency=_dependency_status(self._dependencies(row)),
            project_id=row.project_id,
        )

    def list_workflows(self, *, project_id: str | None = None) -> list[WorkflowRecord]:
        """全部組合場景；給了 project_id 時只列那個專案的（專案頁）。"""
        statement = select(WorkflowRow).where(WorkflowRow.missing.is_(False))
        if project_id is not None:
            statement = statement.where(WorkflowRow.project_id == project_id)
        with self.sessions() as session:
            rows = list(session.scalars(statement.order_by(WorkflowRow.id)))
        return [self._record(row) for row in rows]

    def unassigned(self) -> list[WorkflowRecord]:
        """還沒分到專案的組合場景（例如從 git 拉來的）：專案管理列出，到組合場景頁選專案。"""
        with self.sessions() as session:
            rows = list(
                session.scalars(
                    select(WorkflowRow)
                    .where(WorkflowRow.missing.is_(False), WorkflowRow.project_id.is_(None))
                    .order_by(WorkflowRow.id)
                )
            )
        return [self._record(row, with_last_run=False) for row in rows]

    def get_workflow(self, workflow_id: int) -> WorkflowRecord:
        with self.sessions() as session:
            row = self._row(session, workflow_id)
        return self._record(row)

    def find(self, code: str) -> int:
        """代號 → 組合場景的編號（對外 API 用代號指定組合場景）；找不到時 404。"""
        with self.sessions() as session:
            found = session.scalars(
                select(WorkflowRow.id).where(
                    WorkflowRow.code == code, WorkflowRow.missing.is_(False)
                )
            ).first()
        if found is None:
            raise not_found("workflow_not_found", t("error.workflow_not_found", id=code))
        return found

    @staticmethod
    def _name(name: str) -> str:
        name = name.strip()
        if not name:
            raise invalid("workflow_name_missing", t("error.workflow_name_missing"))
        return name[:_NAME_LIMIT]

    def _definition(self, data: object) -> Workflow:
        workflow, problems = parse_workflow(data)
        if workflow is None:
            raise invalid(
                "workflow_format",
                t("error.workflow_format", count=len(problems)),
                problems=[problem.to_json() for problem in problems],
            )
        return workflow

    def create_workflow(
        self,
        name: str,
        description: str | None = None,
        definition: object = None,
        *,
        code: str | None = None,
        domain_id: str | None = None,
        project_id: str | None = None,
        note: str | None = None,
    ) -> WorkflowRecord:
        """新增組合場景；可以直接帶定義（匯入匯出的 JSON）。定義就是第 1 版。

        code 沒給時自動取 wf-<數字>；domain_id 沒給時放「組合場景」領域（需要時建立）；
        project_id 是放進哪個專案（專案頁新增的就是那個專案），沒給時還沒分到專案；
        note 是第 1 版的說明（沒給時是「建立」）。
        """
        workflow = (
            self._definition(definition)
            if definition is not None
            else Workflow(version=2, mode="dag")
        )
        name = self._name(name)
        description = (description or "").strip() or None
        code = (code or "").strip() or None
        if code is not None and not _CODE.fullmatch(code):
            raise invalid("workflow_code_invalid", t("error.workflow_code_invalid", code=code))
        domain_id = domain_id or self.services.composites_domain()
        project_id = (project_id or "").strip() or None
        packs = self.services.packs
        with packs.lock, self.sessions() as session:
            if session.get(Domain, domain_id) is None:
                raise not_found("domain_not_found", t("error.domain_not_found", id=domain_id))
            if project_id is not None:
                self.services.projects.check(session, project_id)
            code = code or self._next_code(session)
            if self._code_taken(session, code):
                raise conflict("workflow_code_exists", t("error.workflow_code_exists", code=code))
            moment = now()
            row = WorkflowRow(
                name=name,
                description=description,
                definition=workflow.to_json(),
                version=1,
                created_at=moment,
                updated_at=moment,
                code=code,
                domain_id=domain_id,
                project_id=project_id,
                archived=False,
                missing=False,
            )
            session.add(row)
            session.flush()
            self.services.storage.place_composite(code, domain_id)
            try:
                packs.write_composite(
                    CompositeManifest(id=code, name=name, description=description)
                )
                self._write_revision(
                    session, row, 1, workflow, note or t("workflow.note_created"), moment
                )
                session.commit()
            except BaseException:
                session.rollback()
                packs.discard_composite_revision(code, 1, new=True)
                raise
            session.refresh(row)
        return self._record(row)

    def _next_code(self, session: Session) -> str:
        """新組合場景的代號：wf-<數字>，從目前最大的 id 往後找沒用過的。"""
        number = (session.scalar(select(func.max(WorkflowRow.id))) or 0) + 1
        while self._code_taken(session, f"wf-{number}"):
            number += 1
        return f"wf-{number}"

    def _code_taken(self, session: Session, code: str) -> bool:
        exists = session.scalars(select(WorkflowRow.id).where(WorkflowRow.code == code)).first()
        return exists is not None or self.services.storage.composite_domain(code) is not None

    def _write_revision(
        self,
        session: Session,
        row: WorkflowRow,
        number: int,
        workflow: Workflow,
        note: str | None,
        moment: datetime,
    ) -> None:
        """寫入組合場景的版本：workflow.json、版本說明檔（釘住的場景版本）、資料庫的一列。"""
        packs = self.services.packs
        requires = packs.requirements(session, workflow)
        digest = packs.write_composite_revision(
            row.code,
            number,
            workflow_text(workflow),
            note=note,
            created_at=moment,
            requires=requires,
        )
        session.add(
            WorkflowRevision(
                workflow_id=row.id,
                number=number,
                content_hash=digest,
                status="draft",
                verified=False,
                missing=False,
                note=note,
                created_at=moment,
            )
        )
        if row.domain_id is not None:
            packs.declare_requirements(row.domain_id, requires)

    def update_workflow(
        self,
        workflow_id: int,
        *,
        base_version: int,
        name: str | None = None,
        description: str | None = None,
        definition: object = None,
        note: str | None = None,
    ) -> WorkflowRecord:
        """存檔：base_version 不是目前的版本時回 409（別的分頁已經存過）。

        定義和最新版本不同時存成新的版本（version 加一），note 是那個版本的說明（沒給時是
        「存檔」）；名稱與說明寫進 composite.yaml，不分版本。
        """
        workflow = self._definition(definition) if definition is not None else None
        packs = self.services.packs
        with packs.lock, self.sessions() as session:
            row = self._row(session, workflow_id)
            if base_version != row.version:
                raise conflict(
                    "stale_workflow",
                    t("error.stale_workflow", base=base_version, latest=row.version),
                    latest=row.version,
                )
            moment = now()
            if name is not None or description is not None:
                if name is not None:
                    row.name = self._name(name)
                if description is not None:
                    row.description = description.strip() or None
                manifest = packs.composite_manifest(row.code) or CompositeManifest(
                    id=row.code, name=row.name
                )
                packs.write_composite(
                    manifest.model_copy(update={"name": row.name, "description": row.description})
                )
            number: int | None = None
            if workflow is not None and workflow.to_json() != row.definition:
                number = row.version + 1
                try:
                    self._write_revision(
                        session, row, number, workflow, note or t("workflow.note_saved"), moment
                    )
                except FileExistsError:
                    session.rollback()
                    raise conflict(
                        "stale_workflow",
                        t("error.stale_workflow", base=base_version, latest=number),
                        latest=number,
                    ) from None
                row.definition = workflow.to_json()
                row.version = number
            row.updated_at = moment
            try:
                session.commit()
            except BaseException:
                session.rollback()
                if number is not None:
                    packs.discard_composite_revision(row.code, number, new=False)
                raise
            session.refresh(row)
        return self._record(row)

    def manage(
        self,
        workflow_id: int,
        *,
        code: str | None = None,
        domain_id: str | None = None,
        archived: bool | None = None,
        project_id: str | None = None,
    ) -> WorkflowRecord:
        """改代號、搬到其他領域、封存（M11 收尾；第 12 節「之後可以在頁面改代號或搬到其他領域」）。

        代號就是資料夾的名稱：改代號是把 composites/<舊代號> 改名，搬領域是把資料夾搬到另一個
        領域資料夾（推送後在 git 裡是刪除＋新增；版本與驗證紀錄跟著走）。執行中不能改代號或搬。

        project_id 是移到哪個專案（專案空間）：空字串是不屬於任何專案，None 是不變。只改資料庫，
        資料夾不動，所以執行中也可以改。
        """
        packs = self.services.packs
        storage = self.services.storage
        with packs.lock, self.sessions() as session:
            row = self._row(session, workflow_id)
            code = (code or "").strip() or None
            moving = (code is not None and code != row.code) or (
                domain_id is not None and domain_id != row.domain_id
            )
            if moving:
                running = session.scalar(
                    select(func.count())
                    .select_from(WorkflowRunRow)
                    .where(
                        WorkflowRunRow.workflow_id == workflow_id,
                        WorkflowRunRow.status == "running",
                    )
                )
                if running:
                    raise conflict("workflow_running", t("error.workflow_running", id=row.code))
            if code is not None and code != row.code:
                if not _CODE.fullmatch(code):
                    raise invalid(
                        "workflow_code_invalid", t("error.workflow_code_invalid", code=code)
                    )
                if self._code_taken(session, code):
                    raise conflict(
                        "workflow_code_exists", t("error.workflow_code_exists", code=code)
                    )
                source = storage.composite_dir(row.code)
                target = source.with_name(code)
                source.rename(target)
                storage.forget_composite(row.code)
                storage.place_composite(code, row.domain_id or self.services.composites_domain())
                manifest = packs.composite_manifest(code) or CompositeManifest(
                    id=code, name=row.name
                )
                packs.write_composite(manifest.model_copy(update={"id": code}))
                row.code = code
            if domain_id is not None and domain_id != row.domain_id:
                if session.get(Domain, domain_id) is None:
                    raise not_found("domain_not_found", t("error.domain_not_found", id=domain_id))
                source = storage.composite_dir(row.code)
                target = storage.domain_dir(domain_id) / COMPOSITES_DIR / row.code
                if target.exists():
                    raise conflict(
                        "workflow_code_exists", t("error.workflow_code_exists", code=row.code)
                    )
                target.parent.mkdir(parents=True, exist_ok=True)
                source.rename(target)
                storage.forget_composite(row.code)
                storage.place_composite(row.code, domain_id)
                row.domain_id = domain_id
                for number in {
                    row.version,
                    *([row.published_number] if row.published_number else []),
                }:
                    entry, _ = packs.composite_entry(row.code)
                    revision = entry.revisions.get(number) if entry is not None else None
                    if revision is not None and revision.requires:
                        packs.declare_requirements(domain_id, revision.requires)
            if project_id is not None and (project_id or None) != row.project_id:
                if project_id:
                    self.services.projects.check(session, project_id)
                row.project_id = project_id or None
            if archived is not None and archived != row.archived:
                manifest = packs.composite_manifest(row.code) or CompositeManifest(
                    id=row.code, name=row.name
                )
                packs.write_composite(manifest.model_copy(update={"archived": archived}))
                row.archived = archived
            row.updated_at = now()
            session.commit()
            session.refresh(row)
        return self._record(row)

    def dependents(self) -> dict[str, list[WorkflowRecord]]:
        """領域 → 依賴它的組合場景（最新版本或發布的版本釘住了那個領域的場景）。"""
        found: dict[str, list[WorkflowRecord]] = {}
        packs = self.services.packs
        for record in self.list_workflows():
            entry, _ = packs.composite_entry(record.code)
            if entry is None:
                continue
            domains: set[str] = set()
            numbers = {record.version}
            if record.published_number is not None:
                numbers.add(record.published_number)
            for number in numbers:
                revision = entry.revisions.get(number)
                if revision is not None:
                    domains.update(item.domain for item in revision.requires or [])
            for domain_id in sorted(domains - {record.domain_id or ""}):
                found.setdefault(domain_id, []).append(record)
        return found

    def delete_workflow(self, workflow_id: int) -> None:
        """刪除組合場景；執行中不能刪。已經執行過的紀錄保留（有定義的快照）。"""
        with self.sessions() as session:
            row = self._row(session, workflow_id)
            running = session.scalar(
                select(func.count())
                .select_from(WorkflowRunRow)
                .where(
                    WorkflowRunRow.workflow_id == workflow_id,
                    WorkflowRunRow.status == "running",
                )
            )
            if running:
                raise conflict("workflow_running", t("error.workflow_running", id=workflow_id))
            for revision in session.scalars(
                select(WorkflowRevision).where(WorkflowRevision.workflow_id == workflow_id)
            ):
                session.delete(revision)
            session.flush()
            session.delete(row)
            session.commit()
            code = row.code
        # 資料夾一起刪除（推送之後別人拉取也會刪除；歷史在 git 裡）
        self.services.packs.remove_composite(code)

    # ------------------------------------------------------------ 執行

    def start(
        self,
        workflow_id: int,
        *,
        engine: Engine | None = None,
        headless: bool | None = None,
        idempotency_key: str | None = None,
        target: Target | None = None,
        purpose: Purpose = "validation",
        revision: int | None = None,
        worker_id: str | None = None,
        client_id: str | None = None,
    ) -> WorkflowRunRecord:
        """執行組合場景：先檢查，沒有問題才建立組合場景的執行並排入第一個節點。

        purpose 是 validation（驗證某個版本，預設最新；結束時寫驗證紀錄）或 execution
        （執行發布的版本）。target 是執行位置（M9a）：每個節點都一樣，而且第一個節點由哪台
        worker 領取，後面就都給它；worker_id 指定從第一個節點起就給哪台遠端 worker。
        client_id 是觸發的對外 API 用戶端（M14）。
        """
        key = (idempotency_key or "").strip() or None
        existing = self.by_key(key)
        if existing is not None:
            return existing
        with self.sessions() as session:
            row = self._row(session, workflow_id)
            if row.archived:
                raise conflict("workflow_archived", t("error.workflow_archived", id=row.code))
            if purpose == "execution":
                if row.published_number is None:
                    raise conflict(
                        "workflow_unpublished", t("error.workflow_unpublished", id=row.code)
                    )
                number = row.published_number
            else:
                number = revision or row.version
            source_hash = self._usable_revision(session, row, number).content_hash
            code, name = row.code, row.name
        workflow = self.revision_workflow(code, number)
        problems = self.check(workflow) + [
            WorkflowProblem(item.code, item.message)
            for item in self._requirement_items_for(code, number)
            if item.level == "error"
        ]
        self._ensure_runnable(workflow, problems)
        target = self.services.resolve_target(target)
        headless = self.services.resolve_headless(headless, target)
        return self._launch(
            workflow_id=workflow_id,
            name=name,
            version=number,
            workflow=workflow,
            engine=engine,
            headless=headless,
            key=key,
            reused={},
            target=target,
            worker_id=worker_id,
            purpose=purpose,
            code=code,
            source_hash=source_hash,
            client_id=client_id,
        )

    @staticmethod
    def _usable_revision(session: Session, row: WorkflowRow, number: int) -> WorkflowRevision:
        item = session.scalars(
            select(WorkflowRevision).where(
                WorkflowRevision.workflow_id == row.id, WorkflowRevision.number == number
            )
        ).first()
        if item is None or item.missing:
            raise not_found(
                "workflow_revision_not_found",
                t("error.workflow_revision_not_found", id=row.code, number=number),
            )
        if item.problem is not None:
            raise conflict(
                "workflow_revision_unusable",
                t(
                    "error.workflow_revision_unusable",
                    id=row.code,
                    number=number,
                    problem=item.problem,
                ),
            )
        return item

    def revision_workflow(self, code: str, number: int) -> Workflow:
        """某個版本的定義（讀領域資料夾裡的 workflow.json）。"""
        entry, _ = self.services.packs.composite_entry(code)
        revision = entry.revisions.get(number) if entry is not None else None
        if revision is None or revision.workflow is None:
            raise conflict(
                "workflow_revision_unusable",
                t(
                    "error.workflow_revision_unusable",
                    id=code,
                    number=number,
                    problem=revision.problem if revision is not None else "missing",
                ),
            )
        return revision.workflow

    def rerun(
        self,
        run_id: str,
        *,
        resume: bool = False,
        idempotency_key: str | None = None,
        client_id: str | None = None,
    ) -> WorkflowRunRecord:
        """用同一份定義再執行一次：從頭開始，或從停下的節點繼續（沿用前面節點的出參）。

        client_id 是要求重跑的對外 API 用戶端（M14）；Portal 重跑時是 None。
        """
        key = (idempotency_key or "").strip() or None
        existing = self.by_key(key)
        if existing is not None:
            return existing
        with self.sessions() as session:
            row = self._run_row(session, run_id)
            if row.status == "running":
                raise conflict("workflow_run_active", t("error.workflow_run_active", id=run_id))
            workflow = Workflow.model_validate(row.definition)
            snapshot = (row.workflow_id, row.workflow_name, row.workflow_version)
            purpose = cast("Purpose", row.purpose)
            code, source_hash = row.workflow_code, row.workflow_hash
            engine, headless = row.engine, row.headless
            target = cast("Target", row.target)
            reused: dict[str, str] = {}
            pinned: str | None = None
            if resume:
                reused = self._resume_point(session, row, workflow)
                # 沿用的節點在哪台 worker 執行，接下來的節點也給它（M9a）
                pinned = row.worker_id if target != "local" and reused else None
        self._ensure_runnable(workflow, self.check(workflow))
        if target == "remote" and not self.services.workers.has_remote():
            target, pinned = "local", None
        return self._launch(
            workflow_id=snapshot[0],
            name=snapshot[1],
            version=snapshot[2],
            workflow=workflow,
            engine=cast("Engine | None", engine),
            headless=headless if headless or self.services.can_display(target) else True,
            key=key,
            reused=reused,
            resumed_from=run_id if resume else None,
            target=target,
            worker_id=pinned,
            purpose=purpose,
            code=code,
            source_hash=source_hash,
            client_id=client_id,
        )

    def _resume_point(
        self, session: Session, row: WorkflowRunRow, workflow: Workflow
    ) -> dict[str, str]:
        """從停下的節點繼續：沿用的節點 → 那次通過的執行編號（每個全部次數都通過的節點）。

        重複到一半的節點不沿用，新的執行從它沒通過的那一次接著跑（:meth:`_carried`）。
        """
        if row.status == "passed" or row.failed_node is None:
            raise conflict("workflow_not_resumable", t("error.workflow_not_resumable", id=row.id))
        status = self._status(session, row, workflow)
        reused = dict(cast("dict[str, str]", row.reused))
        for node in workflow.nodes:
            latest = status.runs.get(node.id)
            if node.id not in reused and status.states.get(node.id) == "passed" and latest:
                reused[node.id] = latest[-1].id
        return reused

    @staticmethod
    def _ensure_runnable(workflow: Workflow, problems: Sequence[WorkflowProblem]) -> None:
        if problems:
            raise invalid(
                "workflow_invalid",
                t("error.workflow_invalid", count=len(problems)),
                problems=[problem.to_json() for problem in problems],
            )
        if not workflow.nodes:  # check_workflow 會回報；這裡只是保險
            raise invalid("workflow_invalid", t("error.workflow_invalid", count=1))

    def by_key(self, key: str | None) -> WorkflowRunRecord | None:
        """用這個冪等鍵建立的組合場景執行。"""
        if key is None:
            return None
        with self.sessions() as session:
            row = session.scalars(
                select(WorkflowRunRow).where(WorkflowRunRow.idempotency_key == key)
            ).first()
            run_id = row.id if row is not None else None
        return self.get_run(run_id) if run_id is not None else None

    def _launch(
        self,
        *,
        workflow_id: int | None,
        name: str,
        version: int,
        workflow: Workflow,
        engine: Engine | None,
        headless: bool,
        key: str | None,
        reused: Mapping[str, str],
        resumed_from: str | None = None,
        target: Target = "local",
        worker_id: str | None = None,
        purpose: Purpose = "validation",
        code: str | None = None,
        source_hash: str | None = None,
        client_id: str | None = None,
    ) -> WorkflowRunRecord:
        workflow, problems = plan_workflow(
            workflow,
            {node.id: self._scenario(node.scene_id, node.revision) for node in workflow.nodes},
        )
        self._ensure_runnable(workflow, problems)
        with self._lock:
            run_id = new_run_id(code or (f"wf{workflow_id}" if workflow_id is not None else "wf"))
            with self.sessions() as session:
                session.add(
                    WorkflowRunRow(
                        id=run_id,
                        workflow_id=workflow_id,
                        workflow_name=name,
                        workflow_version=version,
                        definition=workflow.to_json(),
                        status="running",
                        engine=engine,
                        headless=headless,
                        reused=dict(reused),
                        resumed_from=resumed_from,
                        idempotency_key=key,
                        cancel_requested=False,
                        created_at=now(),
                        target=target,
                        worker_id=worker_id,
                        purpose=purpose,
                        workflow_code=code,
                        workflow_hash=source_hash,
                        client_id=client_id,
                    )
                )
                try:
                    session.commit()
                except IntegrityError:
                    session.rollback()
                    existing = self.by_key(key)
                    if existing is None:
                        raise
                    return existing
            self._advance(run_id)
        self.services.packs.record_workflow_run(run_id)  # run.json（M11 PR 2）
        return self.get_run(run_id)

    def _node_runs(self, session: Session, run_id: str) -> dict[str, list[Run]]:
        """組合場景執行裡每個節點的每一次執行，依先後。"""
        found: dict[str, list[Run]] = {}
        for run in session.scalars(
            select(Run).where(Run.workflow_run_id == run_id).order_by(Run.created_at, Run.id)
        ):
            if run.node_id is not None:
                found.setdefault(run.node_id, []).append(run)
        return found

    @staticmethod
    def _carried(session: Session, row: WorkflowRunRow, node_id: str) -> int:
        """從失敗的節點繼續時，這個節點在前面幾次組合場景執行已經通過的次數。"""
        count = 0
        previous_id = row.resumed_from
        seen: set[str] = set()
        while previous_id is not None and previous_id not in seen:
            seen.add(previous_id)
            previous = session.get(WorkflowRunRow, previous_id)
            if previous is None or node_id in cast("dict[str, str]", previous.reused):
                break
            count += (
                session.scalar(
                    select(func.count())
                    .select_from(Run)
                    .where(
                        Run.workflow_run_id == previous.id,
                        Run.node_id == node_id,
                        Run.status == "passed",
                    )
                )
                or 0
            )
            previous_id = previous.resumed_from
        return count

    def _status(self, session: Session, row: WorkflowRunRow, workflow: Workflow) -> "_RunStatus":
        """組合場景執行目前的樣子：每個節點的狀態、次數與出參，以及排程的結果。"""
        runs = self._node_runs(session, row.id)
        reused = cast("dict[str, str]", row.reused)
        states: dict[str, NodeState] = {}
        outputs: dict[str, Mapping[str, object] | None] = {}
        iterations: dict[str, int] = {}
        again: list[str] = []
        failed: Run | None = None
        active = 0
        for node in workflow.nodes:
            if node.id in reused:
                previous = session.get(Run, reused[node.id])
                states[node.id] = "passed"
                iterations[node.id] = node.times
                outputs[node.id] = (
                    dict(previous.output or {})
                    if previous is not None and previous.status == "passed"
                    else None
                )
                continue
            items = runs.get(node.id, [])
            done = sum(item.status == "passed" for item in items)
            if node.times > 1:
                done += self._carried(session, row, node.id)
            iterations[node.id] = done
            if not items:
                continue
            latest = items[-1]
            if latest.status in ("queued", "running"):
                states[node.id] = "running"
                active += 1
            elif latest.status == "passed":
                outputs[node.id] = dict(latest.output or {})
                if done >= node.times:
                    states[node.id] = "passed"
                else:
                    states[node.id] = "running"
                    again.append(node.id)
            else:
                states[node.id] = "failed"
                if failed is None or (latest.created_at, latest.id) < (
                    failed.created_at,
                    failed.id,
                ):
                    failed = latest
        return _RunStatus(
            states=states,
            outputs=outputs,
            iterations=iterations,
            runs=runs,
            again=tuple(again),
            failed=failed,
            active=active,
            progress=advance(workflow, states, outputs),
        )

    def _advance(self, run_id: str) -> None:
        """依目前的結果往下走：停下、全部完成，或排入可以開始的節點（不超過同時執行的上限）。

        呼叫端持有鎖。有節點沒有通過時不再排新的節點，已經在跑的跑完才停下。
        """
        with self.sessions() as session:
            row = self._run_row(session, run_id)
            if row.status != "running":
                return
            workflow = Workflow.model_validate(row.definition)
            status = self._status(session, row, workflow)
        if status.failed is not None:
            if status.active == 0:
                failed = status.failed
                message = t(
                    "workflow_run.node_stopped",
                    node=failed.node_id,
                    scene=failed.scene_id,
                    status=t(f"status.{failed.status}"),
                )
                self._finish(
                    run_id, cast("WorkflowRunStatus", failed.status), failed.node_id, message
                )
            return
        if status.progress.finished and status.active == 0 and not status.again:
            self._finish(run_id, "passed", None, None)
            return
        slots = workflow.parallel - status.active
        for node_id in (*status.again, *status.progress.ready)[: max(0, slots)]:
            if not self._start_node(run_id, node_id):
                return

    def _pin(
        self, session: Session, row: WorkflowRunRow, workflow: Workflow, node: WorkflowNode
    ) -> str | None:
        """這個節點只能給哪台 worker（None 是哪台空著都可以）。

        同時執行是 1 時和以前一樣：第一個節點由哪台領取，後面都給它。大於 1 時只有指定了
        worker（或從失敗的節點繼續）才全部給它；否則只有用到上游檔案出參的節點留在跑那個上游的
        worker，因為檔案在那台的共用工作資料夾。
        """
        if workflow.parallel == 1:
            return row.worker_id
        first = session.scalars(
            select(Run)
            .where(Run.workflow_run_id == row.id)
            .order_by(Run.created_at, Run.id)
            .limit(1)
        ).first()
        explicit = row.worker_id if first is None else first.required_worker
        if explicit is not None:
            return explicit
        for binding in node.inputs.values():
            if not isinstance(binding, OutputBinding):
                continue
            upstream = workflow.node(binding.node)
            scenario = (
                self._scenario(upstream.scene_id, upstream.revision)
                if upstream is not None
                else None
            )
            spec = scenario.outputs.get(binding.output) if scenario is not None else None
            if spec is None or spec.type != "file":
                continue
            reused = cast("dict[str, str]", row.reused).get(binding.node)
            source = (
                session.get(Run, reused)
                if reused is not None
                else session.scalars(
                    select(Run)
                    .where(Run.workflow_run_id == row.id, Run.node_id == binding.node)
                    .order_by(Run.created_at.desc(), Run.id.desc())
                    .limit(1)
                ).first()
            )
            if source is not None and source.worker_id is not None:
                return source.worker_id
        return None

    def _start_node(self, run_id: str, node_id: str) -> bool:
        """排入一個節點（重複的節點是下一次）；取值或排入失敗時組合場景停在這個節點，回傳 False。"""
        with self.sessions() as session:
            row = self._run_row(session, run_id)
            workflow = Workflow.model_validate(row.definition)
            outputs = self._outputs(session, row)
            engine, headless = row.engine, row.headless
            target = cast("Target", row.target)
            client_id = row.client_id
            node = workflow.node(node_id)
            pinned = self._pin(session, row, workflow, node) if node is not None else None
        if node is None:
            self._finish(run_id, "failed", node_id, None)
            return False
        values, problems = resolve_inputs(node, outputs)
        if problems:
            self._finish(run_id, "failed", node.id, problems[0].message)
            return False
        try:
            self.services.request_run(
                node.scene_id,
                purpose="workflow",
                number=node.revision,
                inputs=values,
                engine=cast("Engine | None", engine),
                headless=headless,
                workflow_run_id=run_id,
                node_id=node.id,
                target=target,
                required_worker=pinned,
                client_id=client_id,
            )
        except ServiceError as error:
            details = error.details.get("problems")
            items = [
                str(cast("dict[str, object]", item).get("message"))
                for item in (cast("list[object]", details) if isinstance(details, list) else [])
                if isinstance(item, dict)
            ]
            if items:
                problems_text = t("js.list_separator").join(items)
                message = t(
                    "workflow_run.node_inputs_invalid", node=node.id, problems=problems_text
                )
            else:
                message = t("workflow_run.node_not_started", node=node.id, detail=error.message)
            self._finish(run_id, "failed", node.id, message)
            return False
        return True

    def _finish(
        self, run_id: str, status: WorkflowRunStatus, node: str | None, error: str | None
    ) -> None:
        with self.sessions() as session:
            row = self._run_row(session, run_id)
            if row.status != "running":
                return
            row.status = status
            row.failed_node = node
            row.error = error
            row.finished_at = now()
            workers = {row.worker_id} | set(
                session.scalars(
                    select(Run.worker_id).where(Run.workflow_run_id == run_id).distinct()
                )
            )
            session.commit()
        # 共用工作資料夾（ADR 0020）：本機的直接刪；遠端的請跑過節點的每台 worker 下次領取或心跳時刪
        self.services.storage.drop_workspace(run_id)
        for worker in sorted(item for item in workers if item and item != LOCAL_WORKER):
            self.services.workers.queue_cleanup(worker, run_id)
        # run.json；驗證另外寫進領域資料夾的驗證紀錄（M11 PR 2）
        self.services.packs.record_workflow_run(run_id)

    def node_finished(self, run_id: str) -> None:
        """一個節點的執行結束：依目前的結果排接下來的節點、停下或完成。

        結果每次都從資料庫重新算，同一個通知來兩次（例如重啟時的回復）也不會排兩次。
        """
        with self._lock:
            with self.sessions() as session:
                run = session.get(Run, run_id)
                if run is None or run.workflow_run_id is None or run.status not in FINISHED:
                    return
                row = session.get(WorkflowRunRow, run.workflow_run_id)
                if row is None or row.status != "running":
                    return
                workflow_run = row.id
            self._advance(workflow_run)

    def cancel(self, run_id: str) -> WorkflowRunRecord:
        """取消組合場景的執行：停止目前的節點，後面的節點不執行。已經發生的外部動作不會復原。"""
        with self._lock:
            with self.sessions() as session:
                row = self._run_row(session, run_id)
                if row.status != "running":
                    return self.get_run(run_id)
                active = list(
                    session.scalars(
                        select(Run).where(
                            Run.workflow_run_id == run_id,
                            Run.status.in_(["queued", "running"]),
                        )
                    )
                )
                row.cancel_requested = True
                session.commit()
                current = active[0].node_id if active else None
            self._finish(run_id, "cancelled", current, t("workflow_run.cancelled"))
            for run in active:
                self.services.cancel_run(run.id)
        return self.get_run(run_id)

    def recover(self) -> int:
        """伺服器啟動時：還在執行中的組合場景，依各節點的結果接著處理（排接下來的節點或停下）。"""
        with self.sessions() as session:
            rows = list(
                session.scalars(select(WorkflowRunRow).where(WorkflowRunRow.status == "running"))
            )
            pending: list[tuple[str, bool]] = []
            for row in rows:
                started = session.scalars(
                    select(Run.id).where(Run.workflow_run_id == row.id).limit(1)
                ).first()
                pending.append((row.id, started is not None))
        for workflow_run, started in pending:
            if started:
                with self._lock:
                    self._advance(workflow_run)  # 還在排隊的節點不受影響，worker 會照常執行
            else:
                self._finish(workflow_run, "failed", None, t("run.interrupted"))
        return len(pending)

    # ------------------------------------------------------------ 版本、發布、依賴（M11 PR 2）

    def revisions(self, workflow_id: int) -> list[CompositeRevisionRecord]:
        with self.sessions() as session:
            row = self._row(session, workflow_id)
            items = session.scalars(
                select(WorkflowRevision)
                .where(WorkflowRevision.workflow_id == row.id, WorkflowRevision.missing.is_(False))
                .order_by(WorkflowRevision.number.desc())
            )
            return [
                CompositeRevisionRecord(
                    number=item.number,
                    content_hash=item.content_hash,
                    status=cast("RevisionStatus", item.status),
                    verified=item.verified,
                    problem=item.problem,
                    note=item.note,
                    created_at=item.created_at,
                    published_at=item.published_at,
                    published=row.published_number == item.number,
                )
                for item in items
            ]

    def verifications(self, workflow_id: int) -> list[VerificationRecord]:
        """組合場景的驗證紀錄（領域資料夾裡的，不管是哪一台伺服器驗證的），最新的在前。"""
        with self.sessions() as session:
            code = self._row(session, workflow_id).code
        entry, _ = self.services.packs.composite_entry(code)
        if entry is None:
            return []
        server = self.services.packs.server().id
        found: list[VerificationRecord] = []
        with self.sessions() as session:
            for number, revision in entry.revisions.items():
                digest = revision.info.hash if revision.info is not None else None
                for item in revision.verifications:
                    record = item.record
                    here = (
                        record.server.id == server
                        and session.get(WorkflowRunRow, item.id) is not None
                    )
                    # 雜湊相符：定義的雜湊一樣，而且節點跑的場景版本都是釘住的那些
                    matches = record.hash == digest
                    if matches and digest is not None and record.status == "passed":
                        matches = item.proves(digest, revision.requires)
                    found.append(
                        VerificationRecord(
                            id=item.id,
                            revision=number,
                            status=record.status,
                            matches=matches,
                            finished_at=parse_timestamp(record.finished_at),
                            by=record.by,
                            server_id=record.server.id,
                            server_name=record.server.name,
                            worker=record.worker.id,
                            engine=record.engine,
                            headless=record.headless,
                            here=here,
                        )
                    )
        return sorted(found, key=lambda item: (item.finished_at, item.id), reverse=True)

    def publish(self, workflow_id: int, number: int) -> WorkflowRecord:
        """發布組合場景的版本：有雜湊相符的通過驗證紀錄（節點跑的場景版本也相符），
        釘住的場景版本現在都還在、雜湊相同。寫進 composite.yaml 的 published。
        """
        packs = self.services.packs
        with packs.lock, self.sessions() as session:
            row = self._row(session, workflow_id)
            item = self._usable_revision(session, row, number)
            entry, _ = packs.composite_entry(row.code)
            revision = entry.revisions.get(number) if entry is not None else None
            proofs = revision.proofs() if revision is not None else []
            if entry is None or revision is None or not proofs:
                raise conflict(
                    "workflow_not_validated",
                    t("error.workflow_not_validated", id=row.code, number=number),
                )
            errors = [
                problem
                for problem in self._requirement_items(
                    session, number, revision.requires or [], revision.workflow
                )
                if problem.level == "error"
            ]
            if errors:
                raise conflict(
                    "workflow_dependencies",
                    t("error.workflow_dependencies", id=row.code, count=len(errors)),
                    problems=[problem.to_json() for problem in errors],
                )
            moment = now()
            published = PublishedRef(
                revision=number,
                verification=proofs[0].id,
                at=timestamp(moment),
                by=packs.operator(),
                server=packs.server(),
            )
            packs.write_composite(entry.manifest.model_copy(update={"published": published}))
            row.published_number = number
            row.updated_at = moment
            item.published_at = moment
            item.verified = True
            session.commit()
        return self.get_workflow(workflow_id)

    def dependencies(self, workflow_id: int) -> list[DependencyItem]:
        """依賴的問題（最新版本與發布的版本）：任務紀錄第 7 節的清單與補全方式。"""
        with self.sessions() as session:
            row = self._row(session, workflow_id)
        return self._dependencies(row)

    def _dependencies(self, row: WorkflowRow) -> list[DependencyItem]:
        numbers: set[int] = {row.version}
        if row.published_number is not None:
            numbers.add(row.published_number)
        items: list[DependencyItem] = []
        seen: set[tuple[str, str, str | None]] = set()
        for number in sorted(numbers):
            for item in self._requirement_items_for(row.code, number):
                key = (item.code, item.message, item.scene)
                if key not in seen:
                    seen.add(key)
                    items.append(item)
        return items

    def _requirement_items_for(self, code: str, number: int) -> list[DependencyItem]:
        entry, _ = self.services.packs.composite_entry(code)
        revision = entry.revisions.get(number) if entry is not None else None
        if revision is None or revision.workflow is None:
            return []
        with self.sessions() as session:
            return self._requirement_items(
                session, number, revision.requires or [], revision.workflow
            )

    def _requirement_source(self, domain_id: str) -> dict[str, str] | None:
        """依賴的領域從哪裡取得：任一個領域的 pack.yaml requires 裡記的 source。"""
        packs = self.services.packs
        folders = sorted(self.services.storage.domains.glob("*"))
        for folder in folders:
            manifest = packs.manifest(folder.name) if folder.is_dir() else None
            for item in manifest.requires if manifest is not None else []:
                if item.domain == domain_id and item.source is not None:
                    found = {"url": item.source.repo, "directory": item.source.directory or ""}
                    if item.source.branch:
                        found["branch"] = item.source.branch
                    return found
        return None

    def _requirement_items(
        self,
        session: Session,
        number: int,
        requires: Sequence[SceneRequirement],
        workflow: Workflow | None,
    ) -> list[DependencyItem]:
        """一個版本的依賴：釘住的場景版本在不在、雜湊對不對；場景用到的角色與 Secrets。"""
        if workflow is None:
            return []
        pinned = {(item.scene, item.revision): item for item in requires}
        items: list[DependencyItem] = []
        checked: set[tuple[str, int]] = set()

        def add(
            level: Literal["error", "warning"],
            code: str,
            action: str | None,
            params: Mapping[str, object],
            source: dict[str, str] | None = None,
        ) -> None:
            items.append(
                DependencyItem(
                    level=level,
                    code=f"dependency.{code}",
                    message=t(f"dependency.{code}", **params),
                    revision=number,
                    domain=cast("str | None", params.get("domain")),
                    scene=cast("str | None", params.get("scene")),
                    action=action,
                    source=source,
                )
            )

        for node in workflow.nodes:
            key = (node.scene_id, node.revision)
            if key in checked:
                continue
            checked.add(key)
            params: dict[str, object] = {"scene": node.scene_id, "revision": node.revision}
            pin = pinned.get(key)
            if pin is None:
                add("error", "unpinned", "resave", params)
                continue
            params["domain"] = pin.domain
            domain = session.get(Domain, pin.domain)
            if domain is None:
                add(
                    "error",
                    "domain_missing",
                    "add_domain",
                    params,
                    self._requirement_source(pin.domain),
                )
                continue
            # 領域有 git 資料來源：缺的東西多半是還沒拉取（或拉取失敗），補全的方式是拉取
            refresh = "pull" if domain.source else "reload_domain"
            scene = session.get(Scene, pin.scene)
            if scene is None or scene.missing or scene.domain_id != pin.domain:
                add("error", "scene_missing", refresh, params)
                continue
            revision = session.scalars(
                select(Revision).where(
                    Revision.scene_id == pin.scene, Revision.number == pin.revision
                )
            ).first()
            if revision is None or revision.missing:
                add("error", "revision_missing", refresh, params)
                continue
            if revision.problem is not None:
                add("error", "revision_unusable", "reload_domain", params)
                continue
            if revision.content_hash != pin.hash:
                add("error", "hash_mismatch", "resave", params)
                continue
            scenario = self._scenario(pin.scene, pin.revision)
            if scenario is None:
                continue
            if scenario.login is not None:
                role = session.get(Role, scenario.login.role)
                params["role"] = scenario.login.role
                if role is None or role.missing:
                    add("error", "role_missing", "reload_domain", params)
                elif role.status != "logged_in" and not role.auto_login:
                    add("warning", "role_login", "login", params)
            stored = {info.name for info in self.services.roles.list_secrets()}
            missing = [
                name for name in scenario.secrets if name not in stored and name not in os.environ
            ]
            if missing:
                add(
                    "warning", "secrets_missing", "secrets", {**params, "names": ", ".join(missing)}
                )
        return items

    # ------------------------------------------------------------ 查詢

    @staticmethod
    def _run_row(session: Session, run_id: str) -> WorkflowRunRow:
        row = session.get(WorkflowRunRow, run_id)
        if row is None:
            raise not_found("workflow_run_not_found", t("error.workflow_run_not_found", id=run_id))
        return row

    @staticmethod
    def _latest_runs(session: Session, run_id: str) -> dict[str, Run]:
        """組合場景執行裡每個節點最新的一次執行。"""
        found: dict[str, Run] = {}
        for run in session.scalars(
            select(Run).where(Run.workflow_run_id == run_id).order_by(Run.created_at, Run.id)
        ):
            if run.node_id is not None:
                found[run.node_id] = run
        return found

    def _outputs(
        self, session: Session, row: WorkflowRunRow
    ) -> dict[str, Mapping[str, object] | None]:
        """節點代號 → 通過之後發布的出參（沿用的節點取原本那次執行）；沒有通過的是 None。"""
        outputs: dict[str, Mapping[str, object] | None] = {}
        for node, run in self._latest_runs(session, row.id).items():
            outputs[node] = dict(run.output or {}) if run.status == "passed" else None
        for node, previous in cast("dict[str, str]", row.reused).items():
            run = session.get(Run, previous)
            outputs[node] = (
                dict(run.output or {}) if run is not None and run.status == "passed" else None
            )
        return outputs

    def _run_record(self, session: Session, row: WorkflowRunRow) -> WorkflowRunRecord:
        workflow, _ = parse_workflow(row.definition)
        nodes: list[WorkflowNodeState] = []
        links: tuple[tuple[str, str, str], ...] = ()
        concurrency = 1
        if workflow is not None:
            status = self._status(session, row, workflow)
            reused = cast("dict[str, str]", row.reused)
            for index, node in enumerate(workflow.execution_nodes()):
                nodes.append(self._node_state(session, row, index, node, status, reused))
            links = tuple(
                (source, target, state)
                for (source, target), state in sorted(status.progress.links.items())
            )
            concurrency = workflow.parallel
        return WorkflowRunRecord(
            id=row.id,
            workflow_id=row.workflow_id,
            workflow_name=row.workflow_name,
            workflow_version=row.workflow_version,
            status=cast("WorkflowRunStatus", row.status),
            engine=row.engine,
            headless=row.headless,
            error=row.error,
            failed_node=row.failed_node,
            resumed_from=row.resumed_from,
            target=cast("Target", row.target),
            worker_id=row.worker_id,
            cancel_requested=row.cancel_requested,
            created_at=row.created_at,
            finished_at=row.finished_at,
            nodes=tuple(nodes),
            purpose=row.purpose,
            workflow_code=row.workflow_code,
            client_id=row.client_id,
            concurrency=concurrency,
            links=links,
        )

    def _node_state(
        self,
        session: Session,
        row: WorkflowRunRow,
        index: int,
        node: WorkflowNode,
        status: _RunStatus,
        reused: Mapping[str, str],
    ) -> WorkflowNodeState:
        scenario = self._scenario(node.scene_id, node.revision)
        sources = (
            {name: source.to_json() for name, source in input_sources(node, scenario).items()}
            if scenario is not None
            else {}
        )
        runs = status.runs.get(node.id, [])
        run: Run | None = None
        error: str | None = None
        skipped_by: Literal["condition"] | None = None
        state: NodeStatus
        if node.id in reused:
            run = session.get(Run, reused[node.id])
            state = "reused"
        elif runs:
            run = runs[-1]
            state = cast("NodeStatus", run.status)
        elif node.id in status.progress.skipped:
            state, skipped_by = "skipped", "condition"
        elif row.status == "running":
            state = "pending"
        elif row.failed_node == node.id:
            state = "failed"  # 沒有開始執行就停下（例如綁定的值不符合入參規則）
            error = row.error
        else:
            state = "skipped"
        name = run.scene_name if run is not None else (scenario.name if scenario else node.scene_id)
        return WorkflowNodeState(
            index=index,
            id=node.id,
            scene_id=node.scene_id,
            scene_name=name,
            revision=node.revision,
            status=state,
            sources=sources,
            run=_run_record(run) if run is not None else None,
            error=error,
            repeat=node.times,
            iterations=status.iterations.get(node.id, 0),
            runs=tuple(item.id for item in runs),
            skipped_by=skipped_by,
        )

    def get_run(self, run_id: str) -> WorkflowRunRecord:
        with self.sessions() as session:
            return self._run_record(session, self._run_row(session, run_id))

    def get_run_with_definition(self, run_id: str) -> tuple[WorkflowRunRecord, Workflow | None]:
        """組合運行與它開始時的定義快照（匯總報告畫 DAG、找出參的流向用）。"""
        with self.sessions() as session:
            row = self._run_row(session, run_id)
            workflow, _ = parse_workflow(row.definition)
            return self._run_record(session, row), workflow

    def list_runs(
        self,
        *,
        workflow_id: int | None = None,
        project_id: str | None = None,
        limit: int = RUN_LIST_LIMIT,
        projects: Collection[str] | None = None,
        statuses: Collection[str] = (),
        purposes: Collection[str] = (),
        client_id: str | None = None,
        workflow_ids: Collection[int] = (),
        workers: Collection[str] = (),
    ) -> list[WorkflowRunRecord]:
        """組合場景的執行，新的在前；可以只列一個組合場景或一個專案（現在屬於它的組合場景）的。

        對外 API（M14）另外可以限定幾個專案（projects）、狀態、目的與觸發的用戶端；運行報告的
        「組合運行」檢視（2026-10-27）可以限定幾個組合場景與執行位置（本機或 worker 代號）。
        """
        statement = (
            select(WorkflowRunRow)
            .order_by(WorkflowRunRow.created_at.desc(), WorkflowRunRow.id.desc())
            .limit(limit)
        )
        if workflow_id is not None:
            statement = statement.where(WorkflowRunRow.workflow_id == workflow_id)
        if project_id is not None:
            members = select(WorkflowRow.id).where(WorkflowRow.project_id == project_id)
            statement = statement.where(WorkflowRunRow.workflow_id.in_(members))
        if projects is not None:
            members = select(WorkflowRow.id).where(WorkflowRow.project_id.in_(list(projects)))
            statement = statement.where(WorkflowRunRow.workflow_id.in_(members))
        if statuses:
            statement = statement.where(WorkflowRunRow.status.in_(list(statuses)))
        if purposes:
            statement = statement.where(WorkflowRunRow.purpose.in_(list(purposes)))
        if client_id is not None:
            statement = statement.where(WorkflowRunRow.client_id == client_id)
        if workflow_ids:
            statement = statement.where(WorkflowRunRow.workflow_id.in_(list(workflow_ids)))
        if workers:
            # 第一個節點領取後才知道是哪台；還沒領取的本機執行算「本機」
            chosen = list(workers)
            conditions: list[ColumnElement[bool]] = [WorkflowRunRow.worker_id.in_(chosen)]
            if LOCAL_WORKER in chosen:
                conditions.append(
                    and_(WorkflowRunRow.worker_id.is_(None), WorkflowRunRow.target == "local")
                )
            statement = statement.where(or_(*conditions))
        with self.sessions() as session:
            return [self._run_record(session, row) for row in session.scalars(statement)]


def _specs(scenario: Scenario, key: str) -> list[list[object]]:
    """入參或出參：[名稱, DSL 寫法的規格] 的清單，保留場景檔的順序。"""
    specs = scenario.inputs if key == "inputs" else scenario.outputs
    return [
        [name, spec.model_dump(mode="json", by_alias=True, exclude_none=True)]
        for name, spec in specs.items()
    ]


def _dependency_status(items: Sequence[DependencyItem]) -> DependencyStatus:
    if any(item.level == "error" for item in items):
        return "incomplete"
    return "warnings" if items else "complete"
