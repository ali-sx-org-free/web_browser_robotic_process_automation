"""稽核紀錄（M8，ADR 0025）：誰在什麼時候登入、登出、改了或執行了什麼。

- 記的是事件（登入、登入失敗、登出、建立第一個系統管理員）與每一個改變東西的請求（Portal 的
  ``/api`` 寫入請求，含沒有權限被擋下的：方法、路徑、結果的狀態碼）；**不記請求內容**
  （可能有密碼、Secrets 的值）。
  Agent API 另有自己的稽核（api_audit）。
- 只增不改：沒有修改或刪除的介面。每一筆的雜湊是「前一筆的雜湊＋這一筆的內容」的 SHA-256，
  改了或刪了中間任何一筆，:meth:`AuditLog.verify` 就從那一筆起對不上（直接改資料庫也看得出來；
  連最後幾筆一起刪掉看不出來，要防這個得把雜湊另外存到別處，ADR 0025 記為之後再看）。
"""

import hashlib
import json
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Final

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from rpa_server.domain import now
from rpa_server.models import AuditEvent

__all__ = ["GENESIS", "AuditLog", "AuditRecord", "Verification"]

GENESIS: Final = "0" * 64
"""第一筆的「前一筆雜湊」。"""


@dataclass(frozen=True, slots=True)
class AuditRecord:
    id: int
    at: datetime
    user_id: int | None
    username: str | None
    action: str
    target: str | None
    status: int | None
    ip: str | None
    via: str | None
    detail: str | None

    def to_json(self) -> dict[str, object]:
        return {
            "id": self.id,
            "at": self.at.isoformat(timespec="seconds"),
            "userId": self.user_id,
            "username": self.username,
            "action": self.action,
            "target": self.target,
            "status": self.status,
            "ip": self.ip,
            "via": self.via,
            "detail": self.detail,
        }


@dataclass(frozen=True, slots=True)
class Verification:
    ok: bool
    checked: int
    broken_at: int | None
    """第一筆對不上的編號。"""

    def to_json(self) -> dict[str, object]:
        return {"ok": self.ok, "checked": self.checked, "brokenAt": self.broken_at}


def _digest(previous: str, event: AuditEvent) -> str:
    content = json.dumps(
        [
            previous,
            event.at.isoformat(timespec="microseconds"),
            event.user_id,
            event.username,
            event.action,
            event.target,
            event.status,
            event.ip,
            event.via,
            event.detail,
        ],
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _record(event: AuditEvent) -> AuditRecord:
    return AuditRecord(
        id=event.id,
        at=event.at,
        user_id=event.user_id,
        username=event.username,
        action=event.action,
        target=event.target,
        status=event.status,
        ip=event.ip,
        via=event.via,
        detail=event.detail,
    )


class AuditLog:
    def __init__(self, sessions: sessionmaker[Session]) -> None:
        self.sessions = sessions
        self._lock = threading.Lock()

    def record(
        self,
        action: str,
        *,
        user_id: int | None = None,
        username: str | None = None,
        target: str | None = None,
        status: int | None = None,
        ip: str | None = None,
        via: str | None = None,
        detail: str | None = None,
    ) -> None:
        # 同一把鎖裡讀最後一筆、算雜湊、寫入：鏈不會分岔
        with self._lock, self.sessions() as session:
            last = session.scalars(
                select(AuditEvent).order_by(AuditEvent.id.desc()).limit(1)
            ).first()
            event = AuditEvent(
                at=now(),
                user_id=user_id,
                username=(username or "")[:64] or None,
                action=action[:40],
                target=(target or "")[:500] or None,
                status=status,
                ip=(ip or "")[:64] or None,
                via=(via or "")[:64] or None,
                detail=detail,
                prev_hash=last.hash if last is not None else GENESIS,
                hash="",
            )
            event.hash = _digest(event.prev_hash, event)
            session.add(event)
            session.commit()

    def recent(
        self, *, username: str | None = None, before: int | None = None, limit: int = 200
    ) -> list[AuditRecord]:
        """最新的在前；``before`` 是上一頁最後一筆的編號。"""
        with self.sessions() as session:
            statement = select(AuditEvent).order_by(AuditEvent.id.desc()).limit(limit)
            if username:
                statement = statement.where(AuditEvent.username == username.strip().lower())
            if before is not None:
                statement = statement.where(AuditEvent.id < before)
            return [_record(event) for event in session.scalars(statement)]

    def verify(self) -> Verification:
        """從第一筆依序重算雜湊。"""
        previous = GENESIS
        checked = 0
        with self.sessions() as session:
            for event in session.scalars(
                select(AuditEvent).order_by(AuditEvent.id).execution_options(yield_per=500)
            ):
                if event.prev_hash != previous or _digest(previous, event) != event.hash:
                    return Verification(False, checked, event.id)
                previous = event.hash
                checked += 1
        return Verification(True, checked, None)
