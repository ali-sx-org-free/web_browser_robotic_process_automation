"""登入角色與 Secrets 的使用權限（M8.1，ADR 0026）：綁定的帳號才看得到、用得到。

伺服器一律要登入（同 test_multi_user.py）；API 用戶端的部分在 test_agent_api.py。
"""

from collections.abc import Iterator
from dataclasses import replace
from typing import cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx2 import Response

from rpa_core.i18n import use_locale
from rpa_server.access import Principal
from rpa_server.app import create_app
from rpa_server.config import Settings
from rpa_server.grants import SEEDED
from rpa_server.models import Setting
from rpa_server.services import Services

JsonObject = dict[str, object]
PASSWORD = "secret-123"


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
def admin(app: FastAPI) -> Iterator[TestClient]:
    """伺服器這台的系統管理員；「測試網站自動化」有 BA 範例（BA-004 用登入角色 testsite-user）。"""
    with TestClient(app, client=("127.0.0.1", 50000), follow_redirects=False) as client:
        body(client.post("/setup", json={"username": "root", "password": "admin-password"}))
        with use_locale("zh-Hant"):
            services(app).seed_examples_domain()
        yield client


def member(admin: TestClient, app: FastAPI, username: str, role: str) -> TestClient:
    """新增帳號、加進「測試網站自動化」，回傳登入好的瀏覽器。"""
    body(admin.post("/api/users", json={"username": username, "password": PASSWORD}), 201)
    body(admin.put(f"/api/domains/testsite/members/{username}", json={"role": role}))
    browser = TestClient(app, client=("10.0.0.9", 50001), follow_redirects=False)
    body(browser.post("/login", json={"username": username, "password": PASSWORD}))
    return browser


def role_ids(client: TestClient) -> list[str]:
    roles = cast("list[JsonObject]", body(client.get("/api/roles"))["roles"])
    return [str(role["id"]) for role in roles]


def test_login_roles_follow_grants(admin: TestClient, app: FastAPI) -> None:
    dana = member(admin, app, "dana", "admin")
    eddie = member(admin, app, "eddie", "editor")
    amy = member(admin, app, "amy", "runner")

    # 還沒綁定：看不到、用不到；領域的管理員看得到（要能指定誰能用）
    assert role_ids(eddie) == []
    assert role_ids(amy) == []
    assert "testsite-user" in role_ids(dana)
    assert code(eddie.get("/api/roles/testsite-user"), 404) == "role_not_found"
    refused = eddie.post("/api/scenes/ba-004/revisions/1/validate", json={"inputs": {}})
    assert code(refused, 403) == "login_role_forbidden"
    assert code(eddie.post("/api/roles/testsite-user/check"), 403) == "login_role_forbidden"

    # 指定誰能用：領域的管理員可以，編輯者不行
    grant = {"user": "eddie"}
    assert code(eddie.post("/api/roles/testsite-user/grants", json=grant), 403) == "forbidden"
    holders = body(dana.post("/api/roles/testsite-user/grants", json=grant), 201)
    assert [user["username"] for user in cast("list[JsonObject]", holders["users"])] == ["eddie"]
    assert role_ids(eddie) == ["testsite-user"]
    body(eddie.post("/api/scenes/ba-004/revisions/1/validate", json={"inputs": {}}), 202)
    unknown = dana.post("/api/roles/testsite-user/grants", json={"user": "nobody"})
    assert code(unknown, 404) == "user_not_found"

    # 移除後又不能用
    body(dana.request("DELETE", "/api/roles/testsite-user/grants", json=grant))
    refused = eddie.post("/api/scenes/ba-004/revisions/1/validate", json={"inputs": {}})
    assert code(refused, 403) == "login_role_forbidden"

    # 系統管理員不必綁定
    body(admin.post("/api/scenes/ba-004/revisions/1/validate", json={"inputs": {}}), 202)


def test_new_role_is_granted_to_its_creator(admin: TestClient, app: FastAPI) -> None:
    eddie = member(admin, app, "eddie", "editor")
    role = {
        "id": "erp-clerk",
        "name": "ERP 職員",
        "loginUrl": "https://erp.example.test/login",
        "check": "{ testId: current-user }",
        "domainId": "testsite",
    }
    body(admin.put("/api/secrets/ERP_PASSWORD", json={"value": "s3cret"}))
    auto = {
        **role,
        "autoLogin": (
            "- action: fill\n  target: {label: 密碼}\n  value: '{{ secrets.ERP_PASSWORD }}'\n"
        ),
    }
    assert code(eddie.post("/api/roles", json=auto), 403) == "secret_forbidden"
    body(eddie.post("/api/roles", json=role), 201)
    assert role_ids(eddie) == ["erp-clerk"]
    holders = body(admin.get("/api/roles/erp-clerk/grants"))
    assert [user["username"] for user in cast("list[JsonObject]", holders["users"])] == ["eddie"]


def test_secrets_follow_grants(admin: TestClient, app: FastAPI) -> None:
    dana = member(admin, app, "dana", "admin")
    eddie = member(admin, app, "eddie", "editor")
    body(admin.put("/api/secrets/ERP_PASSWORD", json={"value": "s3cret"}))
    assert body(eddie.get("/api/secrets")) == {"secrets": []}

    files = cast("JsonObject", body(admin.get("/api/scenes/ba-001/revisions/1"))["files"])
    text = str(files["scenario.yaml"]).replace("\nsteps:", "\nsecrets: [ERP_PASSWORD]\nsteps:", 1)
    save = {"baseRevision": 1, "files": {"scenario.yaml": text}}
    assert code(eddie.post("/api/scenes/ba-001/revisions", json=save), 403) == "secret_forbidden"

    # Secrets 的綁定只有系統管理員能指定
    grant = {"user": "eddie"}
    assert code(dana.post("/api/secrets/ERP_PASSWORD/grants", json=grant), 403) == "forbidden"
    body(admin.post("/api/secrets/ERP_PASSWORD/grants", json=grant), 201)
    listed = cast("list[JsonObject]", body(eddie.get("/api/secrets"))["secrets"])
    assert [item["name"] for item in listed] == ["ERP_PASSWORD"]
    body(eddie.post("/api/scenes/ba-001/revisions", json=save), 201)

    # 刪除 Secret 時綁定一起刪
    body(admin.delete("/api/secrets/ERP_PASSWORD"))
    body(admin.put("/api/secrets/ERP_PASSWORD", json={"value": "again"}))
    assert body(eddie.get("/api/secrets")) == {"secrets": []}


def test_background_work_uses_who_started_it(admin: TestClient, app: FastAPI) -> None:
    """批次與組合運行記下開始的人：之後排的列與節點用他檢查；停用的帳號什麼都不能用。"""
    member(admin, app, "amy", "runner")
    grants = services(app).grants
    users = services(app).accounts.list_users()
    amy_id = next(user.id for user in users if user.username == "amy")
    amy = grants.principal_for(user_id=amy_id)
    assert amy is not None
    assert not amy.unrestricted
    assert not grants.can_use(amy, "role", "testsite-user")
    grants.grant("role", "testsite-user", amy.key, by="root")
    assert grants.can_use(amy, "role", "testsite-user")
    body(admin.patch(f"/api/users/{amy_id}", json={"disabled": True}))
    blocked = grants.principal_for(user_id=amy_id)
    assert blocked is not None
    assert blocked.blocked
    assert not grants.can_use(blocked, "role", "testsite-user")
    assert grants.principal_for() is None  # 沒有人：不檢查
    assert grants.can_use(None, "role", "testsite-user")
    client = grants.principal_for(client_id="agent-x")
    assert client == Principal.client("agent-x")


def test_upgrade_grants_existing_api_clients_once(admin: TestClient, app: FastAPI) -> None:
    body(admin.post("/api/domains", json={"id": "hr", "name": "人資"}), 201)
    body(
        admin.post(
            "/api/agents",
            json={"id": "agent-a", "policy": {"scopes": ["runs:read"], "domains": ["testsite"]}},
        ),
        201,
    )
    body(admin.post("/api/agents", json={"id": "agent-b", "policy": {"domains": ["hr"]}}), 201)
    body(admin.put("/api/secrets/ERP_PASSWORD", json={"value": "s3cret"}))
    store = services(app)
    with store.sessions() as session:  # 當作還沒做過（升級前的資料）
        found = session.get(Setting, SEEDED)
        if found is not None:
            session.delete(found)
            session.commit()
    store._seed_grants()  # pyright: ignore[reportPrivateUsage]
    agent_a = Principal.client("agent-a")
    agent_b = Principal.client("agent-b")
    assert store.grants.can_use(agent_a, "role", "testsite-user")  # 可用領域裡的登入角色
    assert not store.grants.can_use(agent_b, "role", "testsite-user")
    assert store.grants.can_use(agent_b, "secret", "ERP_PASSWORD")  # Secrets 全部
    # 只做一次：之後新增的用戶端不會自動綁定
    body(admin.post("/api/agents", json={"id": "agent-c"}), 201)
    store._seed_grants()  # pyright: ignore[reportPrivateUsage]
    assert not store.grants.can_use(Principal.client("agent-c"), "secret", "ERP_PASSWORD")
    events = cast("list[JsonObject]", body(admin.get("/api/audit"))["events"])
    assert any(event["action"] == "grants_seeded" for event in events)
