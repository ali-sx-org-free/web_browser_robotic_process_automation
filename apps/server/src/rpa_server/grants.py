"""登入角色與 Secrets 的使用權限（M8.1，ADR 0026）。

登入角色是目標系統裡的一個身分加上伺服器保存的登入狀態；Secret 是密碼這類的值。誰能用它們，
另外綁定到帳號或 API 用戶端（``credential_grants``）：

- 看得到、用得到的只有綁定的；系統管理員不受限制。
- 指定誰能用：登入角色由所在領域的管理員與系統管理員，全域的登入角色與 Secrets 由系統管理員
  （規則在 rpa_server.gate 與路由）。
- 用到的地方（存檔、發布、驗證、執行、批次、組合運行、逐步調試、錄製、人工登入）呼叫
  :meth:`Grants.check`；背景工作傳記下的人，沒有人時不檢查。

升級時（第一次啟動）把既有的 API 用戶端綁到它可用領域裡的登入角色與所有 Secrets
（:meth:`Grants.seed_clients`），只做一次。
"""

from collections.abc import Collection, Iterable
from dataclasses import dataclass
from typing import Final, Literal

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, sessionmaker

from rpa_server.access import Principal
from rpa_server.domain import now
from rpa_server.errors import ServiceError, invalid, not_found
from rpa_server.i18n import t
from rpa_server.models import ApiClient, CredentialGrant, Setting, User

__all__ = ["SEEDED", "GrantHolders", "GrantKind", "Grants"]

GrantKind = Literal["role", "secret"]
SEEDED: Final = "credential_grants_seeded"
"""設定的鍵：升級時的自動綁定做過了（值是時間與綁了幾筆）。"""


@dataclass(frozen=True, slots=True)
class GrantHolders:
    """綁定了某個登入角色或 Secret 的帳號與 API 用戶端。"""

    users: tuple[tuple[int, str, str], ...]
    """(id, 帳號, 顯示名稱)，依帳號排序。"""
    clients: tuple[tuple[str, str], ...]
    """(代號, 名稱)，依代號排序。"""

    def to_json(self) -> dict[str, object]:
        return {
            "users": [
                {"id": user_id, "username": username, "displayName": name}
                for user_id, username, name in self.users
            ],
            "clients": [{"id": client_id, "name": name} for client_id, name in self.clients],
        }


class Grants:
    """綁定的資料與檢查。"""

    def __init__(self, sessions: sessionmaker[Session]) -> None:
        self.sessions = sessions

    # ------------------------------------------------------------ 誰

    def principal_for(
        self, *, user_id: int | None = None, client_id: str | None = None
    ) -> Principal | None:
        """背景工作記下的人（批次、組合運行）：API 用戶端、帳號，都沒有時是 None（不檢查）。

        帳號依目前的資料：已經是系統管理員就不受限制，停用或不在了就什麼都不能用。
        """
        if client_id is not None:
            return Principal.client(client_id)
        if user_id is None:
            return None
        with self.sessions() as session:
            user = session.get(User, user_id)
            if user is None or user.disabled:
                label = user.username if user is not None else str(user_id)
                return Principal(f"user:{user_id}", label, blocked=True)
            return Principal.user(user.id, user.username, system_admin=user.system_admin)

    # ------------------------------------------------------------ 查詢與檢查

    def allowed(self, principal: Principal, kind: GrantKind) -> frozenset[str] | None:
        """這個人綁定的登入角色或 Secrets；不受限制時是 None。"""
        if principal.unrestricted:
            return None
        if principal.blocked:
            return frozenset()
        with self.sessions() as session:
            return frozenset(
                session.scalars(
                    select(CredentialGrant.target).where(
                        CredentialGrant.kind == kind, CredentialGrant.principal == principal.key
                    )
                )
            )

    def can_use(self, principal: Principal | None, kind: GrantKind, target: str) -> bool:
        if principal is None:
            return True
        allowed = self.allowed(principal, kind)
        return allowed is None or target in allowed

    def check(
        self,
        principal: Principal | None,
        *,
        role: str | None = None,
        secrets: Iterable[str] = (),
    ) -> None:
        """要能用這個登入角色與這些 Secrets；不能時 403。None（背景工作）不檢查。"""
        if principal is None or principal.unrestricted:
            return
        if role is not None and not self.can_use(principal, "role", role):
            raise ServiceError(
                403,
                "login_role_forbidden",
                t("error.login_role_forbidden", who=principal.label, id=role),
            )
        names = sorted(set(secrets))
        if names:
            allowed = self.allowed(principal, "secret") or frozenset()
            missing = [name for name in names if name not in allowed]
            if missing:
                raise ServiceError(
                    403,
                    "secret_forbidden",
                    t("error.secret_forbidden", who=principal.label, names=", ".join(missing)),
                )

    def holders(self, kind: GrantKind, target: str) -> GrantHolders:
        with self.sessions() as session:
            keys = list(
                session.scalars(
                    select(CredentialGrant.principal).where(
                        CredentialGrant.kind == kind, CredentialGrant.target == target
                    )
                )
            )
            user_ids = [
                int(key[5:]) for key in keys if key.startswith("user:") and key[5:].isdigit()
            ]
            client_ids = [key[7:] for key in keys if key.startswith("client:")]
            users = (
                session.scalars(select(User).where(User.id.in_(user_ids))).all() if user_ids else []
            )
            clients = (
                session.scalars(select(ApiClient).where(ApiClient.id.in_(client_ids))).all()
                if client_ids
                else []
            )
            return GrantHolders(
                users=tuple(
                    sorted(
                        ((user.id, user.username, user.display_name) for user in users),
                        key=lambda item: item[1],
                    )
                ),
                clients=tuple(sorted((client.id, client.name) for client in clients)),
            )

    def counts(self, kind: GrantKind) -> dict[str, int]:
        """登入角色或 Secret → 綁了幾個（帳號與 API 用戶端）。"""
        found: dict[str, int] = {}
        with self.sessions() as session:
            for target in session.scalars(
                select(CredentialGrant.target).where(CredentialGrant.kind == kind)
            ):
                found[target] = found.get(target, 0) + 1
        return found

    # ------------------------------------------------------------ 指定與移除

    def principal_key(self, *, username: str | None = None, client_id: str | None = None) -> str:
        """指定誰：帳號（依帳號名稱）或 API 用戶端（依代號）；找不到時 404。"""
        with self.sessions() as session:
            if username:
                name = username.strip().lower()
                user = session.scalars(select(User).where(User.username == name)).first()
                if user is None:
                    raise not_found("user_not_found", t("error.user_not_found", id=name))
                return Principal.user(user.id, user.username).key
            if client_id:
                client = session.get(ApiClient, client_id.strip())
                if client is None:
                    raise not_found("agent_not_found", t("error.agent_not_found", id=client_id))
                return Principal.client(client.id).key
        raise invalid("grant_who_missing", t("error.grant_who_missing"))

    def grant(self, kind: GrantKind, target: str, principal: str, *, by: str | None) -> bool:
        """綁定（已經綁了就不動）；新綁定時回傳 True。"""
        with self.sessions() as session:
            if self._find(session, kind, target, principal) is not None:
                return False
            session.add(
                CredentialGrant(
                    kind=kind, target=target, principal=principal, granted_at=now(), granted_by=by
                )
            )
            session.commit()
            return True

    def revoke(self, kind: GrantKind, target: str, principal: str) -> bool:
        with self.sessions() as session:
            found = self._find(session, kind, target, principal)
            if found is None:
                return False
            session.delete(found)
            session.commit()
            return True

    def forget(self, kind: GrantKind, target: str) -> None:
        """登入角色或 Secret 刪除了：綁定一起刪。"""
        with self.sessions() as session:
            session.execute(
                delete(CredentialGrant).where(
                    CredentialGrant.kind == kind, CredentialGrant.target == target
                )
            )
            session.commit()

    def forget_principal(self, principal: str) -> None:
        """API 用戶端刪除了：它的綁定一起刪。"""
        with self.sessions() as session:
            session.execute(delete(CredentialGrant).where(CredentialGrant.principal == principal))
            session.commit()

    @staticmethod
    def _find(
        session: Session, kind: GrantKind, target: str, principal: str
    ) -> CredentialGrant | None:
        return session.scalars(
            select(CredentialGrant).where(
                CredentialGrant.kind == kind,
                CredentialGrant.target == target,
                CredentialGrant.principal == principal,
            )
        ).first()

    # ------------------------------------------------------------ 升級

    def seed_clients(
        self, roles: Iterable[tuple[str, str | None]], secrets: Collection[str]
    ) -> int | None:
        """升級後第一次啟動：既有的 API 用戶端綁到它可用領域裡的登入角色（全域的也算）與
        所有 Secrets，讓升級前能跑的照樣能跑。做過了回傳 None，否則回傳綁了幾筆。"""
        roles = list(roles)
        with self.sessions() as session:
            if session.get(Setting, SEEDED) is not None:
                return None
            moment = now()
            count = 0
            for client in session.scalars(select(ApiClient)):
                key = Principal.client(client.id).key
                allowed = client.domains
                targets: list[tuple[GrantKind, str]] = []
                for role_id, domain_id in roles:
                    if allowed is None or domain_id is None or domain_id in allowed:
                        targets.append(("role", role_id))
                for name in sorted(secrets):
                    targets.append(("secret", name))
                for kind, target in targets:
                    if self._find(session, kind, target, key) is None:
                        session.add(
                            CredentialGrant(
                                kind=kind,
                                target=target,
                                principal=key,
                                granted_at=moment,
                                granted_by=None,
                            )
                        )
                        count += 1
            session.add(Setting(key=SEEDED, value={"at": moment.isoformat(), "count": count}))
            session.commit()
            return count
