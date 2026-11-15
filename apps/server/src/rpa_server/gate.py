"""登入與權限的關卡（M8，ADR 0025）：管理 Portal 的頁面與 ``/api`` 一律要登入。

- 還沒有任何帳號：頁面轉到 ``/setup``（只有伺服器那台電腦 127.0.0.1 能建立第一個系統管理員），
  ``/api`` 回 401 ``setup_required``。
- 沒登入：頁面轉到 ``/login?next=…``，``/api`` 回 401 ``login_required``。
- 登入後依 :data:`RULES`（第一個符合的規則）檢查權限：要看的東西所在的領域看不到時 404（不透露
  存在），看得到但不能做時 403。東西的領域由 :class:`Resolve` 查（場景、執行、批次、組合場景、
  組合運行、領域、登入角色、逐步調試）；建立時才指定領域的（新場景、新組合場景、新角色、錄製）
  在路由裡另外檢查（rpa_server.auth.require）。沒有列出的 GET 只要登入；沒有列出的寫入只有系統
  管理員（預設拒絕）。
- 改變東西的 ``/api`` 請求（POST、PUT、PATCH、DELETE）結束後寫一筆稽核紀錄（rpa_server.audit）。
- 不經過這裡的：靜態檔、登入／登出／建立第一個管理員、語言切換、API 的說明（openapi.json）、
  Worker API、Client API、Agent API（它們各有權杖或 API 金鑰）。

用純 ASGI 寫（同 rpa_server.middleware）：目前的使用者放在 ContextVar，路由與服務層讀得到。
"""

import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from http.cookies import CookieError, SimpleCookie
from typing import TYPE_CHECKING, Final, Literal, cast
from urllib.parse import quote

import anyio
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from rpa_server.access import FULL_ACCESS, Access, Capability, use_access
from rpa_server.context import via_recorder
from rpa_server.i18n import t
from rpa_server.middleware import EXTERNAL_PATHS

if TYPE_CHECKING:  # 規則與判斷不需要資料庫（可以單獨測試）
    from rpa_server.audit import AuditLog
    from rpa_server.auth import AccountService

__all__ = [
    "LOGIN_HEADER",
    "OPEN_PATHS",
    "RULES",
    "SESSION_COOKIE",
    "AuthGateMiddleware",
    "Need",
    "Resolve",
    "Rule",
    "decide",
    "is_loopback",
    "match_rule",
]

LOGIN_HEADER: Final = "X-RPA-Login"
"""沒登入的 401 帶著這個標頭：錄製端的閘道據此分辨「要登入」與「裝置權杖失效」。"""
SESSION_COOKIE: Final = "rpa_session"
"""登入的 Cookie 名稱前綴；實際名稱加上伺服器代號（同一台電腦開了兩個伺服器時不互相蓋掉）。"""
OPEN_PATHS: Final = (
    "/static/",
    "/login",
    "/logout",
    "/setup",
    "/lang/",
    "/favicon.ico",
    # API 的說明（不含資料）：`rpa serve` 用 openapi.json 的標題認出這個埠上已經有管理 Portal
    "/api/openapi.json",
    "/api/docs",
)
_SAFE: Final = frozenset({"GET", "HEAD", "OPTIONS"})

Need = Literal["login", "system", "view", "run", "edit", "manage", "run-any", "edit-any"]
Kind = Literal["scene", "run", "batch", "workflow", "workflow_run", "domain", "role", "debug"]
Resolve = Callable[[Kind, str], tuple[bool, str | None]]
"""(種類, 代號) → (存在嗎, 所在的領域)；組合場景的 workflow 代號是數字編號。"""


@dataclass(frozen=True, slots=True)
class Rule:
    methods: frozenset[str] | None
    """None 是所有方法；``"write"`` 展開成 POST、PUT、PATCH、DELETE。"""
    pattern: re.Pattern[str]
    need: Need
    kind: Kind | None = None


_WRITE: Final = frozenset({"POST", "PUT", "PATCH", "DELETE"})
_READ: Final = frozenset({"GET", "HEAD"})


def _rule(methods: str, path: str, need: Need, kind: Kind | None = None) -> Rule:
    """``path`` 的 ``{id}`` 是東西的代號，``{_}`` 是其他一段，結尾的 ``…`` 代表後面還可以有路徑。"""
    tail = path.endswith("…")
    body = re.escape(path.removesuffix("…"))
    body = body.replace(r"\{id\}", "(?P<id>[^/]+)").replace(r"\{_\}", "[^/]+")
    pattern = re.compile(body + ("(/.*)?" if tail else "") + "$")
    if methods == "*":
        chosen: frozenset[str] | None = None
    elif methods == "write":
        chosen = _WRITE
    elif methods == "read":
        chosen = _READ
    else:
        chosen = frozenset(methods.split(","))
    return Rule(chosen, pattern, need, kind)


RULES: Final[tuple[Rule, ...]] = (
    # ---- 只有系統管理員：帳號、稽核、裝置、對外 API 用戶端、伺服器設定、Secrets 的值、領域的建立
    _rule("*", "/api/users…", "system"),
    _rule("*", "/api/audit…", "system"),
    _rule("*", "/api/workers…", "system"),
    _rule("*", "/api/recorders…", "system"),
    _rule("*", "/api/agents…", "system"),
    _rule("*", "/api/agent-audit…", "system"),
    _rule("read", "/api/settings/batches", "login"),
    _rule("*", "/api/settings…", "system"),
    _rule("read", "/api/secrets", "login"),
    _rule("*", "/api/secrets…", "system"),
    _rule("write", "/api/domains", "system"),
    _rule("*", "/api/domains/order", "system"),
    _rule("*", "/api/domains/from-git", "system"),
    _rule("*", "/api/git/probe", "system"),
    _rule("read", "/api/projects…", "login"),
    _rule("*", "/api/projects…", "system"),
    # ---- 領域
    _rule("read", "/api/domains/{id}/members", "view", "domain"),
    _rule("*", "/api/domains/{id}/members…", "manage", "domain"),
    _rule("*", "/api/domains/{id}/sync…", "manage", "domain"),
    _rule("*", "/api/domains/{id}/source…", "manage", "domain"),
    _rule("POST", "/api/domains/{id}/reload", "edit", "domain"),
    _rule("DELETE", "/api/domains/{id}", "system"),
    _rule("PATCH", "/api/domains/{id}", "manage", "domain"),
    _rule("read", "/api/domains/{id}", "view", "domain"),
    # ---- 場景
    _rule("POST", "/api/scenes", "edit-any"),
    _rule("POST", "/api/scenes/import", "edit-any"),
    _rule("POST", "/api/scenes/{id}/runs", "run", "scene"),
    _rule("POST", "/api/scenes/{id}/batches", "run", "scene"),
    _rule("read", "/api/scenes/{id}…", "view", "scene"),
    _rule("write", "/api/scenes/{id}…", "edit", "scene"),
    # ---- 執行、批次
    _rule("read", "/api/runs/{id}…", "view", "run"),
    _rule("write", "/api/runs/{id}…", "run", "run"),
    _rule("read", "/api/batches/{id}…", "view", "batch"),
    _rule("write", "/api/batches/{id}…", "run", "batch"),
    _rule("POST", "/api/batch-sheets", "run-any"),
    _rule("*", "/api/files…", "run-any"),
    # ---- 組合場景
    _rule("read", "/api/workflows/library", "login"),
    _rule("POST", "/api/workflows/check", "login"),
    _rule("POST", "/api/workflows", "edit-any"),
    _rule("POST", "/api/workflows/{id}/runs", "run", "workflow"),
    _rule("POST", "/api/workflows/{id}/batches", "run", "workflow"),
    _rule("read", "/api/workflows/{id}…", "view", "workflow"),
    _rule("write", "/api/workflows/{id}…", "edit", "workflow"),
    _rule("read", "/api/workflow-runs/{id}…", "view", "workflow_run"),
    _rule("write", "/api/workflow-runs/{id}…", "run", "workflow_run"),
    # ---- 登入角色（沒有領域的是全域角色：大家看得到，只有系統管理員能改）
    _rule("POST", "/api/roles", "edit-any"),
    _rule("read", "/api/roles/{id}…", "view", "role"),
    _rule("write", "/api/roles/{id}…", "edit", "role"),
    # ---- 錄製、逐步調試、選取元素
    _rule("*", "/api/debug/{id}…", "edit", "debug"),
    _rule("*", "/api/recordings…", "edit-any"),
    _rule("*", "/api/locator-picks…", "edit-any"),
    # ---- 其他登入後都能用的
    _rule("*", "/api/me…", "login"),
    _rule("POST", "/api/contract/render", "login"),
    # ---- 頁面
    _rule("read", "/users…", "system"),
    _rule("read", "/audit…", "system"),
    _rule("read", "/workers…", "system"),
    _rule("read", "/devices…", "system"),
    _rule("read", "/agents…", "system"),
    _rule("read", "/domains/{id}/sync", "manage", "domain"),
    _rule("read", "/domains/{id}…", "view", "domain"),
    _rule("read", "/scenes/{id}/edit", "edit", "scene"),
    _rule("read", "/scenes/{id}/debug", "edit", "scene"),
    _rule("read", "/scenes/{id}/run", "run", "scene"),
    _rule("read", "/scenes/{id}/batch", "run", "scene"),
    _rule("read", "/scenes/{id}…", "view", "scene"),
    _rule("read", "/runs/{id}…", "view", "run"),
    _rule("read", "/batches/{id}…", "view", "batch"),
    _rule("read", "/playground/runs/{id}…", "view", "workflow_run"),
    _rule("read", "/playground/{id}/batch", "run", "workflow"),
    _rule("read", "/playground/{id}…", "view", "workflow"),
    _rule("read", "/debug/{id}…", "edit", "debug"),
    _rule("read", "/recording…", "edit-any"),
    _rule("read", "/recordings/{id}…", "edit-any"),
)


def match_rule(method: str, path: str) -> tuple[Rule | None, str | None]:
    """第一個符合的規則與路徑裡的代號。"""
    for rule in RULES:
        if rule.methods is not None and method not in rule.methods:
            continue
        found = rule.pattern.match(path)
        if found is not None:
            return rule, found.groupdict().get("id")
    return None, None


def decide(access: Access, method: str, path: str, resolve: Resolve) -> Literal[200, 403, 404]:
    """權限檢查的結果：200 可以、403 不能做、404 看不到。"""
    rule, key = match_rule(method, path)
    if rule is None:
        return 200 if method in _SAFE or access.system_admin else 403
    need = rule.need
    if need == "login" or access.system_admin:
        return 200
    if need == "system":
        return 403
    if need in ("run-any", "edit-any"):
        return 200 if access.can_any(cast("Capability", need.removesuffix("-any"))) else 403
    if rule.kind is None or key is None:
        return 403
    exists, domain = resolve(rule.kind, key)
    if not exists:
        return 200  # 讓路由回 404
    capability = need
    if rule.kind == "role" and domain is None:
        return 200 if capability == "view" else 403  # 全域角色
    if not access.can("view", domain):
        return 404
    return 200 if access.can(capability, domain) else 403


def is_loopback(scope: Scope) -> bool:
    """請求是不是從伺服器這台電腦直接來的（不是透過錄製端的閘道）。"""
    client = cast("tuple[str, int] | None", scope.get("client"))
    host = client[0] if client is not None else ""
    return host in ("127.0.0.1", "::1", "localhost") and via_recorder() is None


def _header(scope: Scope, name: bytes) -> str | None:
    for key, value in cast("list[tuple[bytes, bytes]]", scope.get("headers", [])):
        if key.lower() == name:
            return value.decode("latin-1")
    return None


def session_token(scope: Scope, cookie_name: str) -> str | None:
    raw = _header(scope, b"cookie")
    if not raw:
        return None
    jar = SimpleCookie()
    try:
        jar.load(raw)
    except CookieError:
        return None
    morsel = jar.get(cookie_name)
    return morsel.value if morsel is not None else None


def client_ip(scope: Scope) -> str | None:
    client = cast("tuple[str, int] | None", scope.get("client"))
    return client[0] if client is not None else None


class AuthGateMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        *,
        accounts: "AccountService",
        audit: "AuditLog",
        resolve: Resolve,
        cookie_name: Callable[[], str],
        skip_login: bool = False,
        render_denied: Callable[[int, str], bytes] | None = None,
    ) -> None:
        self.app = app
        self.accounts = accounts
        self.audit = audit
        self.resolve = resolve
        self.cookie_name = cookie_name
        self.skip_login = skip_login
        self.render_denied = render_denied

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        path = str(scope.get("path", ""))
        method = str(scope.get("method", "GET")).upper()
        if path.startswith(OPEN_PATHS + EXTERNAL_PATHS):
            await self.app(scope, receive, send)
            return
        if self.skip_login:
            with use_access(FULL_ACCESS):
                await self.app(scope, receive, send)
            return
        api = path.startswith("/api/") or path == "/api"
        token = session_token(scope, self.cookie_name())
        access = await anyio.to_thread.run_sync(self.accounts.access_for, token)
        if access is None:
            has_users = await anyio.to_thread.run_sync(self.accounts.has_users)
            if api:
                code = "login_required" if has_users else "setup_required"
                message = t("error.login_required") if has_users else t("error.setup_required")
                await _json(send, 401, code, message, login=True)
                return
            target = "/login" if has_users else "/setup"
            query = cast("bytes", scope.get("query_string") or b"").decode("latin-1")
            here = path + (f"?{query}" if query else "")
            await _redirect(send, f"{target}?next={quote(here, safe='')}" if has_users else target)
            return
        verdict = await anyio.to_thread.run_sync(decide, access, method, path, self.resolve)
        if verdict != 200:
            if api:
                code = "forbidden" if verdict == 403 else "not_found"
                message = t("error.forbidden") if verdict == 403 else t("error.not_found_or_hidden")
                await _json(send, verdict, code, message)
                if method not in _SAFE:  # 被擋下的寫入也記下（誰試著做了沒有權限的事）
                    await self._record_request(scope, access, method, path, verdict)
            else:
                await self._denied_page(send, verdict, access)
            return
        status: list[int] = []

        async def capture(message: Message) -> None:
            if message["type"] == "http.response.start":
                status.append(int(message["status"]))
            await send(message)

        with use_access(access):
            await self.app(scope, receive, capture if api and method not in _SAFE else send)
        if api and method not in _SAFE:
            await self._record_request(scope, access, method, path, status[0] if status else None)

    async def _record_request(
        self, scope: Scope, access: Access, method: str, path: str, status: int | None
    ) -> None:
        via = via_recorder()
        await anyio.to_thread.run_sync(
            lambda: self.audit.record(
                "request",
                user_id=access.user_id,
                username=access.username,
                target=f"{method} {path}",
                status=status,
                ip=client_ip(scope),
                via=via.id if via is not None else None,
            )
        )

    async def _denied_page(self, send: Send, status: int, access: Access) -> None:
        message = t("error.forbidden") if status == 403 else t("error.not_found_or_hidden")
        render = self.render_denied

        def page() -> bytes:
            if render is None:
                return message.encode("utf-8")
            with use_access(access):  # 選單只列這個使用者看得到的領域
                return render(status, message)

        body = await anyio.to_thread.run_sync(page)
        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": [(b"content-type", b"text/html; charset=utf-8")],
            }
        )
        await send({"type": "http.response.body", "body": body})


async def _json(send: Send, status: int, code: str, message: str, *, login: bool = False) -> None:
    body = json.dumps({"error": {"code": code, "message": message}}, ensure_ascii=False).encode()
    headers = [(b"content-type", b"application/json")]
    if login:
        headers.append((LOGIN_HEADER.lower().encode(), b"required"))
    await send({"type": "http.response.start", "status": status, "headers": headers})
    await send({"type": "http.response.body", "body": body})


async def _redirect(send: Send, location: str) -> None:
    await send(
        {
            "type": "http.response.start",
            "status": 303,
            "headers": [(b"location", location.encode("latin-1")), (b"content-length", b"0")],
        }
    )
    await send({"type": "http.response.body", "body": b""})
