"""登入、登出、建立第一個系統管理員，與帳號、領域成員、稽核的 API（M8，ADR 0025）。

``/login``、``/logout``、``/setup`` 不經過登入關卡（rpa_server.gate 的 OPEN_PATHS）；登入與建立
用 JSON（伺服器沒有表單解析的依賴），頁面上的腳本（static/login.js）送出。其他 ``/api`` 路由的
權限由關卡依規則檢查（帳號與稽核只有系統管理員；成員管理是領域管理員）。
"""

from typing import Annotated

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from rpa_server.auth import ROLES, current_access
from rpa_server.errors import ServiceError
from rpa_server.gate import client_ip, is_loopback, session_token
from rpa_server.i18n import t
from rpa_server.render import render
from rpa_server.services import Services

__all__ = ["account_router", "safe_next"]


class _Body(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="forbid")


class LoginBody(_Body):
    username: str = Field(max_length=64)
    password: str = Field(max_length=1024)
    next: str | None = Field(default=None, max_length=2000)


class SetupBody(_Body):
    username: str = Field(max_length=64)
    display_name: str = Field(default="", max_length=100)
    password: str = Field(max_length=1024)


class PasswordChange(_Body):
    current: str = Field(max_length=1024)
    password: str = Field(max_length=1024)


class UserCreate(_Body):
    username: str = Field(max_length=64)
    display_name: str = Field(default="", max_length=100)
    password: str = Field(max_length=1024)
    system_admin: bool = False


class UserUpdate(_Body):
    display_name: str | None = Field(default=None, max_length=100)
    system_admin: bool | None = None
    disabled: bool | None = None


class PasswordReset(_Body):
    password: str = Field(max_length=1024)


class MemberSet(_Body):
    role: str = Field(max_length=10)


def safe_next(value: str | None) -> str:
    """登入後回到哪裡：只接受這個網站裡的路徑（避免被拿去轉到別的網站）。"""
    if not value or not value.startswith("/") or value.startswith(("//", "/\\")):
        return "/scenes"
    if value.startswith(("/login", "/logout", "/setup")):
        return "/scenes"
    return value


def account_router(services: Services) -> APIRouter:
    router = APIRouter()
    accounts = services.accounts
    audit = services.audit

    def set_cookie(response: Response, request: Request, token: str) -> None:
        response.set_cookie(
            services.session_cookie(),
            token,
            httponly=True,
            samesite="lax",
            secure=request.url.scheme == "https",
            path="/",
        )

    def auth_page(mode: str, *, next_path: str = "/scenes", status: int = 200) -> HTMLResponse:
        html = render(
            "auth.html",
            page="login",
            title=t(f"auth.{mode}_title"),
            mode=mode,
            next_path=next_path,
            min_password=8,
            server=services.server_info(),
        )
        return HTMLResponse(html, status_code=status)

    def signed_in(request: Request) -> bool:
        token = session_token(request.scope, services.session_cookie())
        return accounts.access_for(token) is not None

    # ------------------------------------------------------------ 頁面

    @router.get("/login", include_in_schema=False)
    def login_page(request: Request, next: str | None = None) -> Response:
        if not accounts.has_users():
            return RedirectResponse("/setup", 303)
        if signed_in(request):
            return RedirectResponse(safe_next(next), 303)
        return auth_page("login", next_path=safe_next(next))

    @router.post("/login", include_in_schema=False)
    def login(request: Request, body: LoginBody) -> Response:
        ip = client_ip(request.scope)
        try:
            token, user = accounts.login(
                body.username, body.password, ip=ip, user_agent=request.headers.get("user-agent")
            )
        except ServiceError as error:
            audit.record(
                "login_failed",
                username=body.username.strip().lower()[:64],
                target="POST /login",
                status=error.status,
                ip=ip,
            )
            raise
        audit.record(
            "login",
            user_id=user.id,
            username=user.username,
            target="POST /login",
            status=200,
            ip=ip,
        )
        response = JSONResponse({"next": safe_next(body.next), "user": user.to_json()})
        set_cookie(response, request, token)
        return response

    @router.post("/logout", include_in_schema=False)
    def logout(request: Request) -> Response:
        cookie = services.session_cookie()
        token = session_token(request.scope, cookie)
        access = accounts.access_for(token)
        accounts.logout(token)
        if access is not None:
            audit.record(
                "logout",
                user_id=access.user_id,
                username=access.username,
                target="POST /logout",
                status=303,
                ip=client_ip(request.scope),
            )
        response = RedirectResponse("/login", 303)
        response.delete_cookie(cookie, path="/")
        return response

    @router.get("/setup", include_in_schema=False)
    def setup_page(request: Request) -> Response:
        if accounts.has_users():
            return RedirectResponse("/login", 303)
        if not is_loopback(request.scope):
            return auth_page("setup_remote", status=403)
        return auth_page("setup")

    @router.post("/setup", include_in_schema=False)
    def setup(request: Request, body: SetupBody) -> Response:
        """建立第一個系統管理員：只有還沒有任何帳號、而且從伺服器那台電腦打開時。"""
        if not is_loopback(request.scope):
            raise ServiceError(403, "setup_local_only", t("error.setup_local_only"))
        user = accounts.create_user(body.username, body.display_name, body.password, first=True)
        ip = client_ip(request.scope)
        audit.record(
            "setup",
            user_id=user.id,
            username=user.username,
            target="POST /setup",
            status=200,
            ip=ip,
        )
        token, _ = accounts.login(
            body.username, body.password, ip=ip, user_agent=request.headers.get("user-agent")
        )
        response = JSONResponse({"next": "/scenes", "user": user.to_json()})
        set_cookie(response, request, token)
        return response

    # ------------------------------------------------------------ 自己

    @router.get("/api/me")
    def me() -> dict[str, object]:
        access = current_access()
        if access is None:
            raise ServiceError(401, "login_required", t("error.login_required"))
        return access.to_json()

    @router.post("/api/me/password", status_code=204)
    def change_password(request: Request, body: PasswordChange) -> Response:
        access = current_access()
        if access is None or access.user_id is None:
            raise ServiceError(401, "login_required", t("error.login_required"))
        token = session_token(request.scope, services.session_cookie()) or ""
        accounts.change_password(access.user_id, body.current, body.password, keep=token)
        return Response(status_code=204)

    # ------------------------------------------------------------ 帳號（系統管理員）

    @router.get("/api/users")
    def list_users() -> dict[str, object]:
        return {"users": [user.to_json() for user in accounts.list_users()]}

    @router.post("/api/users", status_code=201)
    def create_user(body: UserCreate) -> dict[str, object]:
        user = accounts.create_user(
            body.username, body.display_name, body.password, system_admin=body.system_admin
        )
        return user.to_json()

    @router.patch("/api/users/{user_id}")
    def update_user(user_id: int, body: UserUpdate) -> dict[str, object]:
        access = current_access()
        if access is not None and access.user_id == user_id and body.disabled:
            raise ServiceError(409, "disable_self", t("error.disable_self"))
        user = accounts.update_user(
            user_id,
            display_name=body.display_name,
            system_admin=body.system_admin,
            disabled=body.disabled,
        )
        return user.to_json()

    @router.post("/api/users/{user_id}/password", status_code=204)
    def reset_password(user_id: int, body: PasswordReset) -> Response:
        accounts.set_password(user_id, body.password)
        return Response(status_code=204)

    # ------------------------------------------------------------ 領域成員（領域管理員）

    @router.get("/api/domains/{domain_id}/members")
    def members(domain_id: str) -> dict[str, object]:
        services.get_domain(domain_id)
        return {
            "members": [member.to_json() for member in accounts.members(domain_id)],
            "roles": list(ROLES),
        }

    @router.put("/api/domains/{domain_id}/members/{username}")
    def set_member(domain_id: str, username: str, body: MemberSet) -> dict[str, object]:
        services.get_domain(domain_id)
        return accounts.set_member(domain_id, username, body.role).to_json()

    @router.delete("/api/domains/{domain_id}/members/{user_id}", status_code=204)
    def remove_member(domain_id: str, user_id: int) -> Response:
        accounts.remove_member(domain_id, user_id)
        return Response(status_code=204)

    # ------------------------------------------------------------ 稽核（系統管理員）

    @router.get("/api/audit")
    def audit_events(
        user: str | None = None,
        before: int | None = None,
        limit: Annotated[int, Query(ge=1, le=1000)] = 200,
    ) -> dict[str, object]:
        events = audit.recent(username=user, before=before, limit=limit)
        return {"events": [event.to_json() for event in events]}

    @router.get("/api/audit/verify")
    def audit_verify() -> dict[str, object]:
        return audit.verify().to_json()

    return router
