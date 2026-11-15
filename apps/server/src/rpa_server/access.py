"""目前請求的使用者與權限（M8，ADR 0025）：不需要資料庫，頁面樣板與服務層都用它。

權限以領域為單位：每個領域的成員是管理員、編輯者、執行者或檢視者（:data:`ROLES`），系統管理員
可以做所有事。rpa_server.gate 在每個請求設好 :func:`use_access`；服務層的清單依
:func:`visible_domains` 只列看得到的領域。背景工作（worker、排程、啟動）沒有設定，不受限制。
帳號與工作階段在 rpa_server.auth。

M8.1（ADR 0026）：登入角色與 Secrets 另外綁定到帳號與 API 用戶端；用它們的是誰由
:func:`current_principal` 決定（Agent API 的請求由 :func:`use_client` 設好用戶端）。
"""

from collections.abc import Generator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from enum import Enum
from typing import Final, Literal

from rpa_server.errors import ServiceError, not_found
from rpa_server.i18n import t

__all__ = [
    "CURRENT",
    "FULL_ACCESS",
    "ROLES",
    "Access",
    "Actor",
    "Capability",
    "Principal",
    "Role",
    "bind_client",
    "current_access",
    "current_principal",
    "require",
    "require_system",
    "resolve_actor",
    "use_access",
    "use_client",
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


@dataclass(frozen=True, slots=True)
class Principal:
    """用登入角色與 Secrets 的是誰（M8.1）：帳號或 API 用戶端。

    ``key`` 是綁定時記的 ``user:帳號 id`` 或 ``client:用戶端代號``；``label`` 用在錯誤訊息。
    系統管理員不受綁定限制（``unrestricted``）；停用的帳號什麼都不能用（``blocked``）。
    """

    key: str
    label: str
    unrestricted: bool = False
    blocked: bool = False

    @property
    def user_id(self) -> int | None:
        """帳號的 id；API 用戶端與內部呼叫是 None。"""
        kind, _, value = self.key.partition(":")
        return int(value) if kind == "user" and value.isdigit() else None

    @staticmethod
    def user(user_id: int, username: str, *, system_admin: bool = False) -> "Principal":
        return Principal(f"user:{user_id}", username, unrestricted=system_admin)

    @staticmethod
    def client(client_id: str) -> "Principal":
        return Principal(f"client:{client_id}", client_id)


class _Context(Enum):
    CURRENT = "current"


CURRENT: Final = _Context.CURRENT
"""「用目前請求的人」：服務的 ``actor`` 參數預設值（背景工作改傳記下的人，或 None 不檢查）。"""
Actor = Principal | None | Literal[_Context.CURRENT]

_client: ContextVar[str | None] = ContextVar("rpa_client", default=None)


@contextmanager
def use_client(client_id: str | None) -> Generator[None]:
    """Agent API 的請求：之後的服務呼叫以這個 API 用戶端的綁定檢查。"""
    token = _client.set(client_id)
    try:
        yield
    finally:
        _client.reset(token)


def bind_client(client_id: str) -> None:
    """Agent API：在這個請求的 task 裡記下用戶端（不必還原：ContextVar 隨 task 結束）。"""
    _client.set(client_id)


def current_principal() -> Principal | None:
    """目前請求用登入角色與 Secrets 的是誰；背景工作是 None（由呼叫的人另外指定）。"""
    client = _client.get()
    if client is not None:
        return Principal.client(client)
    access = current_access()
    if access is None:
        return None
    if access.user_id is None:  # 內部呼叫與測試的 FULL_ACCESS
        return Principal("internal", access.username, unrestricted=True)
    return Principal.user(access.user_id, access.username, system_admin=access.system_admin)


def resolve_actor(actor: Actor, client_id: str | None = None) -> Principal | None:
    """服務的 ``actor`` 參數：CURRENT 時是觸發的 API 用戶端或目前請求的人。"""
    if actor is not CURRENT:
        return actor
    if client_id is not None:
        return Principal.client(client_id)
    return current_principal()


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
