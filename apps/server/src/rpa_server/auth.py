"""多用戶（M8，ADR 0025）：本地帳號、登入工作階段、領域成員與權限。

- **帳號**：第一版只有本地帳號（密碼用標準庫的 scrypt 雜湊）；``users.provider``、``subject``
  預留給之後的 OIDC、LDAP。帳號不刪除，只停用。
- **第一個系統管理員**：還沒有任何帳號時，只能在伺服器那台電腦上（127.0.0.1）打開 ``/setup``
  建立（rpa_server.gate）；之後由系統管理員在「帳號」頁新增帳號。
- **工作階段**：登入後 Cookie 帶隨機權杖（HttpOnly、SameSite=Lax），資料庫只存它的 SHA-256；
  最後一次使用後 :data:`SESSION_IDLE` 沒用就失效，最長 :data:`SESSION_MAX`。改密碼或停用時
  那個帳號的工作階段全部失效。同一個帳號 15 分鐘內連續輸錯 :data:`MAX_FAILURES` 次就先暫停登入。
- **權限以領域為單位**：每個領域的成員是管理員、編輯者、執行者或檢視者；系統管理員可以做所有事。
  目前請求的使用者與權限檢查在 rpa_server.access（不需要資料庫；這裡一起匯出）。
"""

import hashlib
import hmac
import re
import secrets
import threading
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Final, cast

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, sessionmaker

from rpa_server.access import (
    FULL_ACCESS,
    ROLES,
    Access,
    Capability,
    Role,
    current_access,
    require,
    require_system,
    use_access,
    visible_domains,
)
from rpa_server.domain import now
from rpa_server.errors import ServiceError, conflict, invalid, not_found
from rpa_server.i18n import t
from rpa_server.models import Domain, DomainMember, LoginSession, User

__all__ = [
    "FULL_ACCESS",
    "MAX_FAILURES",
    "PASSWORD_MIN",
    "ROLES",
    "SESSION_IDLE",
    "SESSION_MAX",
    "USERNAME",
    "Access",
    "AccountService",
    "Capability",
    "MemberRecord",
    "Role",
    "UserRecord",
    "current_access",
    "hash_password",
    "require",
    "require_system",
    "use_access",
    "verify_password",
    "visible_domains",
]


USERNAME: Final = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}")
PASSWORD_MIN: Final = 8
SESSION_IDLE: Final = timedelta(days=7)
SESSION_MAX: Final = timedelta(days=30)
_TOUCH: Final = timedelta(minutes=5)
"""最後使用時間最多每 5 分鐘寫一次。"""
MAX_FAILURES: Final = 5
_FAILURE_WINDOW: Final = 15 * 60.0

# scrypt：N=2^15、r=8、p=1（約 32 MiB 記憶體），OWASP 建議的範圍
_SCRYPT_N: Final = 2**15
_SCRYPT_R: Final = 8
_SCRYPT_P: Final = 1


def hash_password(password: str) -> str:
    """``scrypt$N$r$p$<鹽 hex>$<雜湊 hex>``。"""
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
        maxmem=64 * 1024 * 1024,
        dklen=32,
    )
    return f"scrypt${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str | None) -> bool:
    if not encoded:
        return False
    try:
        kind, n, r, p, salt, expected = encoded.split("$")
        if kind != "scrypt":
            return False
        digest = hashlib.scrypt(
            password.encode("utf-8"),
            salt=bytes.fromhex(salt),
            n=int(n),
            r=int(r),
            p=int(p),
            maxmem=64 * 1024 * 1024,
            dklen=len(expected) // 2,
        )
    except ValueError:
        return False
    return hmac.compare_digest(digest.hex(), expected)


_DUMMY_HASH: Final = hash_password(secrets.token_hex(8))
"""帳號不存在時也算一次雜湊，回應時間不洩漏帳號是否存在。"""


def _token_id(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- 帳號


@dataclass(frozen=True, slots=True)
class UserRecord:
    id: int
    username: str
    display_name: str
    system_admin: bool
    disabled: bool
    provider: str
    created_at: datetime
    last_login_at: datetime | None
    roles: Mapping[str, str] = field(default_factory=dict[str, str])

    def to_json(self) -> dict[str, object]:
        return {
            "id": self.id,
            "username": self.username,
            "displayName": self.display_name,
            "systemAdmin": self.system_admin,
            "disabled": self.disabled,
            "provider": self.provider,
            "createdAt": self.created_at.isoformat(timespec="seconds"),
            "lastLoginAt": self.last_login_at.isoformat(timespec="seconds")
            if self.last_login_at
            else None,
            "roles": dict(self.roles),
        }


@dataclass(frozen=True, slots=True)
class MemberRecord:
    user_id: int
    username: str
    display_name: str
    role: str
    disabled: bool

    def to_json(self) -> dict[str, object]:
        return {
            "userId": self.user_id,
            "username": self.username,
            "displayName": self.display_name,
            "role": self.role,
            "disabled": self.disabled,
        }


def _user_record(user: User, roles: Mapping[str, str] | None = None) -> UserRecord:
    return UserRecord(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        system_admin=user.system_admin,
        disabled=user.disabled,
        provider=user.provider,
        created_at=user.created_at,
        last_login_at=user.last_login_at,
        roles=dict(roles or {}),
    )


class AccountService:
    """帳號、工作階段與領域成員。"""

    def __init__(
        self, sessions: sessionmaker[Session], clock: Callable[[], float] = time.monotonic
    ) -> None:
        self.sessions = sessions
        self._lock = threading.Lock()
        self._failures: dict[str, list[float]] = {}
        self._clock = clock

    # ------------------------------------------------------------ 帳號

    def has_users(self) -> bool:
        with self.sessions() as session:
            return session.scalar(select(func.count()).select_from(User)) != 0

    @staticmethod
    def _check_username(username: str) -> str:
        name = username.strip().lower()
        if not USERNAME.fullmatch(name):
            raise invalid("username_invalid", t("error.username_invalid"))
        return name

    @staticmethod
    def _check_password(password: str) -> None:
        if len(password) < PASSWORD_MIN:
            raise invalid("password_too_short", t("error.password_too_short", min=PASSWORD_MIN))

    def create_user(
        self,
        username: str,
        display_name: str,
        password: str,
        *,
        system_admin: bool = False,
        first: bool = False,
    ) -> UserRecord:
        """新增本地帳號；``first`` 時只有還沒有任何帳號才建立（第一個系統管理員）。"""
        name = self._check_username(username)
        self._check_password(password)
        shown = display_name.strip()[:100] or name
        hashed = hash_password(password)
        moment = now()
        with self._lock, self.sessions() as session:
            if first and session.scalar(select(func.count()).select_from(User)):
                raise conflict("setup_done", t("error.setup_done"))
            if session.scalars(select(User).where(User.username == name)).first() is not None:
                raise conflict("username_taken", t("error.username_taken", username=name))
            user = User(
                username=name,
                display_name=shown,
                password_hash=hashed,
                provider="local",
                system_admin=system_admin or first,
                disabled=False,
                created_at=moment,
                password_changed_at=moment,
            )
            session.add(user)
            session.commit()
            return _user_record(user)

    def list_users(self) -> list[UserRecord]:
        with self.sessions() as session:
            roles: dict[int, dict[str, str]] = {}
            for member in session.scalars(select(DomainMember)):
                roles.setdefault(member.user_id, {})[member.domain_id] = member.role
            return [
                _user_record(user, roles.get(user.id))
                for user in session.scalars(select(User).order_by(User.username))
            ]

    def get_user(self, user_id: int) -> UserRecord:
        with self.sessions() as session:
            user = self._user(session, user_id)
            return _user_record(user, self._roles(session, user_id))

    @staticmethod
    def _user(session: Session, user_id: int) -> User:
        user = session.get(User, user_id)
        if user is None:
            raise not_found("user_not_found", t("error.user_not_found", id=user_id))
        return user

    @staticmethod
    def _roles(session: Session, user_id: int) -> dict[str, str]:
        return {
            member.domain_id: member.role
            for member in session.scalars(
                select(DomainMember).where(DomainMember.user_id == user_id)
            )
        }

    @staticmethod
    def _other_admins(session: Session, user_id: int) -> int:
        return int(
            session.scalar(
                select(func.count())
                .select_from(User)
                .where(User.system_admin.is_(True), User.disabled.is_(False), User.id != user_id)
            )
            or 0
        )

    def update_user(
        self,
        user_id: int,
        *,
        display_name: str | None = None,
        system_admin: bool | None = None,
        disabled: bool | None = None,
    ) -> UserRecord:
        """改顯示名稱、系統管理員、停用；最後一個能用的系統管理員不能拿掉或停用。"""
        with self._lock, self.sessions() as session:
            user = self._user(session, user_id)
            losing = (system_admin is False and user.system_admin) or (
                disabled is True and user.system_admin and not user.disabled
            )
            if losing and self._other_admins(session, user_id) == 0:
                raise conflict("last_admin", t("error.last_admin"))
            if display_name is not None:
                user.display_name = display_name.strip()[:100] or user.username
            if system_admin is not None:
                user.system_admin = system_admin
            if disabled is not None:
                user.disabled = disabled
                if disabled:
                    session.execute(delete(LoginSession).where(LoginSession.user_id == user_id))
            session.commit()
            return _user_record(user, self._roles(session, user_id))

    def set_password(self, user_id: int, password: str) -> None:
        """系統管理員重設密碼；那個帳號已經登入的工作階段全部失效。"""
        self._check_password(password)
        hashed = hash_password(password)
        with self.sessions() as session:
            user = self._user(session, user_id)
            user.password_hash = hashed
            user.password_changed_at = now()
            session.execute(delete(LoginSession).where(LoginSession.user_id == user_id))
            session.commit()

    def change_password(self, user_id: int, current: str, password: str, *, keep: str) -> None:
        """自己改密碼：要先輸入目前的密碼；其他地方的登入失效，這次的（``keep``）留著。"""
        self._check_password(password)
        with self.sessions() as session:
            user = self._user(session, user_id)
            if not verify_password(current, user.password_hash):
                raise invalid("password_wrong", t("error.password_wrong"))
            user.password_hash = hash_password(password)
            user.password_changed_at = now()
            session.execute(
                delete(LoginSession).where(
                    LoginSession.user_id == user_id, LoginSession.id != _token_id(keep)
                )
            )
            session.commit()

    # ------------------------------------------------------------ 登入

    def _throttled(self, name: str) -> bool:
        moment = self._clock()
        with self._lock:
            recent = [at for at in self._failures.get(name, []) if moment - at < _FAILURE_WINDOW]
            self._failures[name] = recent
            return len(recent) >= MAX_FAILURES

    def _failed(self, name: str) -> None:
        with self._lock:
            self._failures.setdefault(name, []).append(self._clock())

    def login(
        self, username: str, password: str, *, ip: str | None = None, user_agent: str | None = None
    ) -> tuple[str, UserRecord]:
        """帳號密碼對、帳號沒停用時建立工作階段，回傳 (權杖, 帳號)。"""
        name = username.strip().lower()
        if self._throttled(name):
            raise ServiceError(
                429,
                "too_many_attempts",
                t("error.too_many_attempts", minutes=int(_FAILURE_WINDOW // 60)),
            )
        with self.sessions() as session:
            user = session.scalars(select(User).where(User.username == name)).first()
            if user is None:
                verify_password(password, _DUMMY_HASH)
                ok = False
            else:
                ok = verify_password(password, user.password_hash) and not user.disabled
            if not ok or user is None:
                self._failed(name)
                raise ServiceError(401, "login_failed", t("error.login_failed"))
            with self._lock:
                self._failures.pop(name, None)
            token = secrets.token_urlsafe(32)
            moment = now()
            session.add(
                LoginSession(
                    id=_token_id(token),
                    user_id=user.id,
                    created_at=moment,
                    last_seen_at=moment,
                    expires_at=moment + SESSION_MAX,
                    ip=(ip or "")[:64] or None,
                    user_agent=(user_agent or "")[:255] or None,
                )
            )
            user.last_login_at = moment
            # 順便清掉過期的工作階段
            session.execute(delete(LoginSession).where(LoginSession.expires_at < moment))
            session.commit()
            return token, _user_record(user, self._roles(session, user.id))

    def logout(self, token: str | None) -> None:
        if not token:
            return
        with self.sessions() as session:
            session.execute(delete(LoginSession).where(LoginSession.id == _token_id(token)))
            session.commit()

    def access_for(self, token: str | None) -> Access | None:
        """Cookie 的權杖 → 目前的使用者；沒有、過期、帳號停用時是 None。"""
        if not token:
            return None
        moment = now()
        with self.sessions() as session:
            row = session.get(LoginSession, _token_id(token))
            if row is None:
                return None
            seen = row.last_seen_at
            if row.expires_at <= moment or moment - seen > SESSION_IDLE:
                session.delete(row)
                session.commit()
                return None
            user = session.get(User, row.user_id)
            if user is None or user.disabled:
                return None
            if moment - seen > _TOUCH:
                row.last_seen_at = moment
                session.commit()
            return Access(
                user.id,
                user.username,
                user.display_name,
                user.system_admin,
                self._roles(session, user.id),
            )

    # ------------------------------------------------------------ 領域成員

    def members(self, domain_id: str) -> list[MemberRecord]:
        with self.sessions() as session:
            rows = session.execute(
                select(DomainMember, User)
                .join(User, User.id == DomainMember.user_id)
                .where(DomainMember.domain_id == domain_id)
                .order_by(User.username)
            )
            return [
                MemberRecord(user.id, user.username, user.display_name, member.role, user.disabled)
                for member, user in rows
            ]

    def set_member(self, domain_id: str, username: str, role: str) -> MemberRecord:
        """加入或改角色。"""
        if role not in ROLES:
            raise invalid("member_role_invalid", t("error.member_role_invalid", role=role))
        name = username.strip().lower()
        with self._lock, self.sessions() as session:
            if session.get(Domain, domain_id) is None:
                raise not_found("domain_not_found", t("error.domain_not_found", id=domain_id))
            user = session.scalars(select(User).where(User.username == name)).first()
            if user is None:
                raise not_found("user_not_found", t("error.user_not_found", id=name))
            member = session.scalars(
                select(DomainMember).where(
                    DomainMember.domain_id == domain_id, DomainMember.user_id == user.id
                )
            ).first()
            if member is None:
                member = DomainMember(
                    domain_id=domain_id, user_id=user.id, role=role, created_at=now()
                )
                session.add(member)
            else:
                member.role = role
            session.commit()
            return MemberRecord(user.id, user.username, user.display_name, role, user.disabled)

    def remove_member(self, domain_id: str, user_id: int) -> None:
        with self.sessions() as session:
            found = session.execute(
                delete(DomainMember).where(
                    DomainMember.domain_id == domain_id, DomainMember.user_id == user_id
                )
            )
            session.commit()
        if not cast("int", getattr(found, "rowcount", 0)):
            raise not_found("member_not_found", t("error.member_not_found"))

    def drop_domain(self, session: Session, domain_id: str) -> None:
        """刪除領域時一起刪掉成員（在刪除領域的同一個交易裡呼叫）。"""
        session.execute(delete(DomainMember).where(DomainMember.domain_id == domain_id))
