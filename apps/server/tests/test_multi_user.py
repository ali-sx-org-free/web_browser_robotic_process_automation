"""多用戶與治理（M8，ADR 0025）：第一個系統管理員、登入、領域的角色、帳號、稽核。

其他測試用 ``skip_login``（conftest）；這裡的伺服器一律要登入。規則本身在 test_gate.py。
"""

from collections.abc import Iterator
from dataclasses import replace
from typing import cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx2 import Response
from sqlalchemy import update

from rpa_core.i18n import use_locale
from rpa_server.app import create_app
from rpa_server.auth import MAX_FAILURES
from rpa_server.config import Settings
from rpa_server.models import AuditEvent
from rpa_server.services import Services

JsonObject = dict[str, object]
ADMIN_PASSWORD = "admin-password"


@pytest.fixture
def app(settings: Settings) -> FastAPI:
    return create_app(replace(settings, skip_login=False))


def services(app: FastAPI) -> Services:
    return cast("Services", app.state.services)


def body(response: Response, status: int = 200) -> JsonObject:
    assert response.status_code == status, response.text
    data: object = response.json()
    assert isinstance(data, dict)
    return cast("JsonObject", data)


def code(response: Response, status: int) -> str:
    error = body(response, status)["error"]
    assert isinstance(error, dict)
    return str(cast("JsonObject", error)["code"])


@pytest.fixture
def local(app: FastAPI) -> Iterator[TestClient]:
    """從伺服器這台電腦（127.0.0.1）打開的瀏覽器。"""
    with TestClient(app, client=("127.0.0.1", 50000), follow_redirects=False) as client:
        yield client


@pytest.fixture
def remote(app: FastAPI, local: TestClient) -> TestClient:
    """從別台電腦打開的瀏覽器（伺服器由 ``local`` 啟動；同一個應用只啟動一次）。"""
    return browser(app, ("10.0.0.8", 50000))


def browser(app: FastAPI, address: tuple[str, int] = ("10.0.0.9", 50001)) -> TestClient:
    """另一個瀏覽器（自己的 Cookie）；不進入 with，伺服器的啟動與關閉由 ``local`` 負責。"""
    return TestClient(app, client=address, follow_redirects=False)


@pytest.fixture
def admin(local: TestClient, app: FastAPI) -> TestClient:
    """建立第一個系統管理員並登入；也建立「測試網站自動化」與另一個領域 hr。"""
    created = local.post(
        "/setup", json={"username": "Root", "displayName": "管理員", "password": ADMIN_PASSWORD}
    )
    assert body(created)["next"] == "/scenes"
    with use_locale("zh-Hant"):
        services(app).seed_examples_domain()
    body(local.post("/api/domains", json={"id": "hr", "name": "人資"}), 201)
    return local


def sign_in(app: FastAPI, username: str, password: str) -> TestClient:
    client = browser(app)
    body(client.post("/login", json={"username": username, "password": password}))
    return client


def add_user(
    admin: TestClient, username: str, *, domain: str | None = None, role: str = ""
) -> None:
    body(
        admin.post(
            "/api/users",
            json={"username": username, "displayName": username.title(), "password": "secret-123"},
        ),
        201,
    )
    if domain:
        body(admin.put(f"/api/domains/{domain}/members/{username}", json={"role": role}))


def test_first_admin_only_from_the_server_machine(local: TestClient, remote: TestClient) -> None:
    # 還沒有帳號：頁面轉到 /setup，API 回 401
    assert local.get("/scenes").headers["location"] == "/setup"
    assert code(local.get("/api/scenes"), 401) == "setup_required"
    assert local.get("/api/scenes").headers["x-rpa-login"] == "required"  # 閘道據此分辨
    assert local.get("/login").headers["location"] == "/setup"
    # 別台電腦：說明要到伺服器那台建立
    page = remote.get("/setup")
    assert page.status_code == 403
    assert "127.0.0.1" in page.text
    refused = remote.post("/setup", json={"username": "evil", "password": "12345678"})
    assert code(refused, 403) == "setup_local_only"
    # API 的說明不必登入（rpa serve 用它認出管理 Portal）
    assert local.get("/api/openapi.json").status_code == 200
    # 伺服器這台：建立並登入
    assert 'id="auth-form"' in local.get("/setup").text
    short = local.post("/setup", json={"username": "root", "password": "short"})
    assert code(short, 422) == "password_too_short"
    created = body(local.post("/setup", json={"username": "Root", "password": ADMIN_PASSWORD}))
    user = cast("JsonObject", created["user"])
    assert (user["username"], user["systemAdmin"]) == ("root", True)
    me = body(local.get("/api/me"))
    assert (me["username"], me["systemAdmin"]) == ("root", True)
    # 只能建立一次
    again = local.post("/setup", json={"username": "other", "password": ADMIN_PASSWORD})
    assert code(again, 409) == "setup_done"
    assert local.get("/setup").headers["location"] == "/login"
    assert "root" in local.get("/scenes", follow_redirects=True).text


def test_login_logout_and_throttling(admin: TestClient, app: FastAPI) -> None:
    client = browser(app)
    target = client.get("/runs?status=failed")
    assert target.status_code == 303
    assert target.headers["location"] == "/login?next=%2Fruns%3Fstatus%3Dfailed"
    assert 'id="auth-form"' in client.get("/login").text
    wrong = client.post("/login", json={"username": "root", "password": "nope-nope"})
    assert code(wrong, 401) == "login_failed"
    unknown = client.post("/login", json={"username": "nobody", "password": "nope-nope"})
    assert code(unknown, 401) == "login_failed"
    # 登入後回到原本要去的地方；外站的網址不接受
    done = body(
        client.post(
            "/login",
            json={"username": "ROOT", "password": ADMIN_PASSWORD, "next": "/runs?x=1"},
        )
    )
    assert done["next"] == "/runs?x=1"
    evil = {"username": "root", "password": ADMIN_PASSWORD, "next": "//evil.example"}
    assert body(client.post("/login", json=evil))["next"] == "/scenes"
    assert client.get("/api/me").status_code == 200
    out = client.post("/logout")
    assert (out.status_code, out.headers["location"]) == (303, "/login")
    assert code(client.get("/api/me"), 401) == "login_required"
    # 連續輸錯：先暫停這個帳號的登入
    for _ in range(MAX_FAILURES):
        client.post("/login", json={"username": "root", "password": "wrong-wrong"})
    paused = client.post("/login", json={"username": "root", "password": ADMIN_PASSWORD})
    assert code(paused, 429) == "too_many_attempts"


def test_domain_roles(admin: TestClient, app: FastAPI) -> None:
    add_user(admin, "amy", domain="testsite", role="runner")
    add_user(admin, "bob", domain="testsite", role="viewer")
    add_user(admin, "eve", domain="hr", role="admin")
    members = body(admin.get("/api/domains/testsite/members"))
    assert [(m["username"], m["role"]) for m in cast("list[JsonObject]", members["members"])] == [
        ("amy", "runner"),
        ("bob", "viewer"),
    ]
    amy = sign_in(app, "amy", "secret-123")
    bob = sign_in(app, "bob", "secret-123")
    eve = sign_in(app, "eve", "secret-123")
    # 清單只列看得到的領域
    domains = cast("list[JsonObject]", body(amy.get("/api/domains"))["domains"])
    assert [domain["id"] for domain in domains] == ["testsite"]
    scenes = cast("list[JsonObject]", body(eve.get("/api/scenes"))["scenes"])
    assert scenes == []
    assert "ba-001" not in eve.get("/scenes", follow_redirects=True).text
    # 執行者可以執行，檢視者不行；其他領域的看不到
    queued = amy.post("/api/scenes/ba-001/runs", json={"purpose": "validation"})
    assert queued.status_code in (201, 202, 409, 422), queued.text
    assert code(bob.post("/api/scenes/ba-001/runs", json={}), 403) == "forbidden"
    assert bob.get("/api/scenes/ba-001").status_code == 200
    assert code(eve.get("/api/scenes/ba-001"), 404) == "not_found"
    assert eve.get("/scenes/ba-001").status_code == 404
    # 編輯要編輯者以上
    assert amy.get("/scenes/ba-001/edit").status_code == 403
    assert amy.get("/scenes/ba-001/run").status_code in (200, 409)  # 409：還沒發布
    created = amy.post("/api/scenes", json={"id": "amy-001", "name": "A", "domainId": "testsite"})
    assert code(created, 403) == "forbidden"
    # 領域管理員管自己領域的成員；別的領域不行
    body(eve.put("/api/domains/hr/members/bob", json={"role": "editor"}))
    assert eve.put("/api/domains/testsite/members/bob", json={"role": "editor"}).status_code == 404
    assert code(amy.put("/api/domains/testsite/members/bob", json={"role": "admin"}), 403) == (
        "forbidden"
    )
    # 系統管理員才有的頁面與設定
    assert amy.get("/users").status_code == 403
    assert code(amy.get("/api/users"), 403) == "forbidden"
    assert code(amy.put("/api/secrets/ERP_PASSWORD", json={"value": "x"}), 403) == "forbidden"
    assert amy.get("/api/secrets").status_code == 200
    page = amy.get("/runs").text
    assert 'href="/users"' not in page
    assert "Amy" in page  # 右上角的使用者
    mine = body(amy.get("/api/me"))
    assert mine["roles"] == {"testsite": "runner"}
    # 角色換了，下一個請求就生效
    body(admin.put("/api/domains/testsite/members/amy", json={"role": "editor"}))
    assert amy.get("/scenes/ba-001/edit").status_code == 200
    assert admin.delete(f"/api/domains/testsite/members/{bob_id(admin)}").status_code == 204
    assert code(bob.get("/api/scenes/ba-001"), 404) == "not_found"


def bob_id(admin: TestClient) -> int:
    users = cast("list[JsonObject]", body(admin.get("/api/users"))["users"])
    return next(int(cast("int", user["id"])) for user in users if user["username"] == "bob")


def test_accounts(admin: TestClient, app: FastAPI) -> None:
    add_user(admin, "amy")
    taken = admin.post("/api/users", json={"username": "amy", "password": "secret-123"})
    assert code(taken, 409) == "username_taken"
    bad = admin.post("/api/users", json={"username": "Amy Lee", "password": "secret-123"})
    assert code(bad, 422) == "username_invalid"
    users = cast("list[JsonObject]", body(admin.get("/api/users"))["users"])
    root = next(user for user in users if user["username"] == "root")
    amy_id = next(user["id"] for user in users if user["username"] == "amy")
    # 最後一個系統管理員：不能取消、不能停用自己
    refused = admin.patch(f"/api/users/{root['id']}", json={"systemAdmin": False})
    assert code(refused, 409) == "last_admin"
    assert code(admin.patch(f"/api/users/{root['id']}", json={"disabled": True}), 409) == (
        "disable_self"
    )
    amy = sign_in(app, "amy", "secret-123")
    # 自己改密碼：目前的密碼要對；其他地方的登入失效，這次的留著
    other = sign_in(app, "amy", "secret-123")
    wrong = amy.post("/api/me/password", json={"current": "x", "password": "new-secret"})
    assert code(wrong, 422) == "password_wrong"
    changed = amy.post("/api/me/password", json={"current": "secret-123", "password": "new-secret"})
    assert changed.status_code == 204
    assert amy.get("/api/me").status_code == 200
    assert code(other.get("/api/me"), 401) == "login_required"
    # 系統管理員重設密碼、停用：登入全部失效
    assert (
        admin.post(f"/api/users/{amy_id}/password", json={"password": "reset-123"}).status_code
        == 204
    )
    assert code(amy.get("/api/me"), 401) == "login_required"
    again = sign_in(app, "amy", "reset-123")
    body(admin.patch(f"/api/users/{amy_id}", json={"disabled": True}))
    assert code(again.get("/api/me"), 401) == "login_required"
    refused_login = again.post("/login", json={"username": "amy", "password": "reset-123"})
    assert code(refused_login, 401) == "login_failed"
    assert "amy" in admin.get("/users").text


def test_audit_log(admin: TestClient, app: FastAPI) -> None:
    add_user(admin, "amy", domain="testsite", role="viewer")
    browser(app).post("/login", json={"username": "amy", "password": "wrong-wrong"})
    events = cast("list[JsonObject]", body(admin.get("/api/audit"))["events"])
    actions = [(event["action"], event["username"], event["target"]) for event in events]
    assert ("login_failed", "amy", "POST /login") in actions
    assert ("request", "root", "POST /api/users") in actions
    assert ("request", "root", "PUT /api/domains/testsite/members/amy") in actions
    assert actions[-1] == ("setup", "root", "POST /setup")
    assert all(event["action"] != "request" or event["status"] for event in events)
    # GET 不記
    assert not any(str(event["target"]).startswith("GET ") for event in events)
    assert body(admin.get("/api/audit/verify"))["ok"] is True
    page = admin.get("/audit")
    assert 'data-ok="true"' in page.text
    # 直接改資料庫：驗證從那一筆起對不上
    with services(app).sessions() as session:
        first = events[-1]["id"]
        session.execute(update(AuditEvent).where(AuditEvent.id == first).values(username="eve"))
        session.commit()
    broken = body(admin.get("/api/audit/verify"))
    assert (broken["ok"], broken["brokenAt"]) == (False, first)
    assert 'data-ok="false"' in admin.get("/audit").text
