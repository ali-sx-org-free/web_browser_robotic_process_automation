"""目前請求的使用者與權限（M8，ADR 0025）：不需要資料庫，頁面樣板與服務層都用它。

權限以領域為單位：每個領域的成員是管理員、編輯者、執行者或檢視者（:data:`ROLES`），系統管理員
可以做所有事。rpa_server.gate 在每個請求設好 :func:`use_access`；服務層的清單依
:func:`visible_domains` 只列看得到的領域。背景工作（worker、排程、啟動）沒有設定，不受限制。
帳號與工作階段在 rpa_server.auth。
"""

from collections.abc import Generator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Final, Literal

from rpa_server.errors import ServiceError, not_found
from rpa_server.i18n import t

__all__ = [
    "FULL_ACCESS",
    "ROLES",
    "Access",
    "Capability",
    "Role",
    "current_access",
    "require",
    "require_system",
    "use_access",
    "visible_domains",
]

Role = Literal["admin", "editor", "runner", "viewer"]
ROLES: Final[tuple[Role, ...]] = ("admin", "editor", "runner", "viewer")
Capability = Literal["view", "run", "edit", "manage"]
"""看（檢視者以上）、執行（執行者以上）、編輯（編輯者以上）、管理成員與領域設定（管理員）。"""
_RANK: Final[dict[str, int]] = {"viewer": 0, "runner": 1, "editor": 2, "admin": 3}
_NEED: Final[dict[str, int]] = {"view": 0, "run": 1, "edit": 2, "manage": 3}


@dataclass(frozen=True, slots=True)
class Access:
    """目前請求的使用者與權限。"""

    user_id: int | None
    username: str
    display_name: str
    system_admin: bool
    roles: Mapping[str, str] = field(default_factory=dict[str, str])
    """領域代號 → 角色（admin、editor、runner、viewer）。"""

    def role(self, domain_id: str | None) -> str | None:
        return self.roles.get(domain_id) if domain_id is not None else None

    def can(self, capability: Capability, domain_id: str | None) -> bool:
        """能不能在這個領域做這件事；沒有領域的東西（未分配）只有系統管理員。"""
        if self.system_admin:
            return True
        role = self.role(domain_id)
        return role is not None and _RANK[role] >= _NEED[capability]

    def can_any(self, capability: Capability) -> bool:
        """至少在一個領域能做這件事。"""
        return self.system_admin or any(
            _RANK[role] >= _NEED[capability] for role in self.roles.values()
        )

    def domains(self, capability: Capability = "view") -> frozenset[str] | None:
        """能做這件事的領域；系統管理員是 None（全部）。"""
        if self.system_admin:
            return None
        return frozenset(
            domain for domain, role in self.roles.items() if _RANK[role] >= _NEED[capability]
        )

    def to_json(self) -> dict[str, object]:
        return {
            "id": self.user_id,
            "username": self.username,
            "displayName": self.display_name,
            "systemAdmin": self.system_admin,
            "roles": dict(self.roles),
        }


FULL_ACCESS: Final = Access(None, "", "", True)
"""不限制（測試的 ``skip_login``、內部呼叫）。"""

_current: ContextVar[Access | None] = ContextVar("rpa_access", default=None)


def current_access() -> Access | None:
    """目前請求的使用者；背景工作與沒有登入的請求是 None。"""
    return _current.get()


@contextmanager
def use_access(access: Access | None) -> Generator[None]:
    token = _current.set(access)
    try:
        yield
    finally:
        _current.reset(token)


def visible_domains(capability: Capability = "view") -> frozenset[str] | None:
    """目前請求看得到（或能做這件事）的領域；不限制時是 None。"""
    access = current_access()
    return None if access is None else access.domains(capability)


def require(capability: Capability, domain_id: str | None) -> None:
    """目前請求要能在這個領域做這件事：看不到時 404（不透露存在），看得到但不能做時 403。"""
    access = current_access()
    if access is None or access.can(capability, domain_id):
        return
    if not access.can("view", domain_id):
        raise not_found("domain_not_found", t("error.domain_not_found", id=domain_id or ""))
    raise ServiceError(403, "forbidden", t("error.forbidden"))


def require_system() -> None:
    access = current_access()
    if access is not None and not access.system_admin:
        raise ServiceError(403, "forbidden", t("error.forbidden_system"))
