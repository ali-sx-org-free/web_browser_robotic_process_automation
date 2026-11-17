"""權限的規則與判斷（M8，ADR 0025）：不需要資料庫與 FastAPI。"""

from collections.abc import Iterator

import pytest

from rpa_core.i18n import use_locale
from rpa_server.access import FULL_ACCESS, Access, require, use_access, visible_domains
from rpa_server.errors import ServiceError
from rpa_server.gate import decide, match_rule

DOMAINS = {
    ("scene", "ba-001"): "sales",
    ("scene", "hr-001"): "hr",
    ("scene", "loose"): None,
    ("run", "r-1"): "sales",
    ("batch", "b-1"): "sales",
    ("workflow", "7"): "sales",
    ("workflow_run", "wr-1"): "hr",
    ("domain", "sales"): "sales",
    ("domain", "hr"): "hr",
    ("role", "global"): None,
    ("role", "sales-user"): "sales",
    ("debug", "d-1"): "sales",
}


def resolve(kind: str, key: str) -> tuple[bool, str | None]:
    if (kind, key) not in DOMAINS:
        return False, None
    return True, DOMAINS[kind, key]


def user(**roles: str) -> Access:
    return Access(1, "amy", "Amy", False, roles)


@pytest.fixture(autouse=True)
def _zh_hant() -> Iterator[None]:
    with use_locale("zh-Hant"):
        yield


@pytest.mark.parametrize(
    ("role", "method", "path", "expected"),
    [
        # 檢視者：看得到，不能執行或改
        ("viewer", "GET", "/api/scenes/ba-001", 200),
        ("viewer", "GET", "/scenes/ba-001/edit", 403),
        ("viewer", "POST", "/api/scenes/ba-001/runs", 403),
        ("viewer", "GET", "/runs/r-1/replay", 200),
        ("viewer", "POST", "/api/batches/b-1/start", 403),
        # 執行者：可以執行、批次、取消，不能改場景
        ("runner", "POST", "/api/scenes/ba-001/runs", 200),
        ("runner", "POST", "/api/scenes/ba-001/batches", 200),
        ("runner", "GET", "/scenes/ba-001/run", 200),
        ("runner", "POST", "/api/runs/r-1/cancel", 200),
        ("runner", "POST", "/api/workflows/7/runs", 200),
        ("runner", "PUT", "/api/workflows/7", 403),
        ("runner", "POST", "/api/scenes/ba-001/revisions", 403),
        ("runner", "POST", "/api/scenes/ba-001/debug", 403),
        ("runner", "POST", "/api/files", 200),
        ("runner", "GET", "/recording", 403),
        # 編輯者：可以改場景、逐步調試、錄製；不能管成員
        ("editor", "POST", "/api/scenes/ba-001/revisions", 200),
        ("editor", "POST", "/api/scenes/ba-001/revisions/2/publish", 200),
        ("editor", "POST", "/api/debug/d-1/steps/0", 200),
        ("editor", "GET", "/recording", 200),
        ("editor", "POST", "/api/scenes", 200),
        ("editor", "PUT", "/api/domains/sales/members/bob", 403),
        ("editor", "PATCH", "/api/roles/sales-user", 200),
        # 登入角色（M8.1）：人工登入、檢查、登出要執行者以上（綁定由路由檢查），指定誰能用要管理員
        ("viewer", "POST", "/api/roles/sales-user/login", 403),
        ("runner", "POST", "/api/roles/sales-user/login", 200),
        ("runner", "POST", "/api/roles/sales-user/login/finish", 200),
        ("runner", "POST", "/api/roles/sales-user/check", 200),
        ("runner", "DELETE", "/api/roles/sales-user/state", 200),
        ("runner", "PATCH", "/api/roles/sales-user", 403),
        ("editor", "GET", "/api/roles/sales-user/grants", 403),
        ("editor", "POST", "/api/roles/sales-user/grants", 403),
        ("admin", "GET", "/api/roles/sales-user/grants", 200),
        ("admin", "POST", "/api/roles/sales-user/grants", 200),
        ("admin", "DELETE", "/api/roles/sales-user/grants", 200),
        ("admin", "POST", "/api/secrets/ERP_PASSWORD/grants", 403),
        # 管理員：成員、領域設定、git 同步；刪除領域只有系統管理員
        ("admin", "PUT", "/api/domains/sales/members/bob", 200),
        ("admin", "PATCH", "/api/domains/sales", 200),
        ("admin", "POST", "/api/domains/sales/sync/pull", 200),
        ("admin", "GET", "/domains/sales/sync", 200),
        ("admin", "DELETE", "/api/domains/sales", 403),
    ],
)
def test_roles_in_a_domain(role: str, method: str, path: str, expected: int) -> None:
    assert decide(user(sales=role), method, path, resolve) == expected


def test_other_domains_are_hidden() -> None:
    amy = user(sales="admin")
    assert decide(amy, "GET", "/api/scenes/hr-001", resolve) == 404
    assert decide(amy, "GET", "/playground/runs/wr-1", resolve) == 404
    assert decide(amy, "GET", "/domains/hr", resolve) == 404
    # 沒有領域的場景（未分配）只有系統管理員
    assert decide(amy, "GET", "/scenes/loose", resolve) == 404
    # 不存在的讓路由回 404
    assert decide(amy, "GET", "/api/scenes/nothing", resolve) == 200
    # 全域角色：大家看得到，只有系統管理員能改
    assert decide(amy, "GET", "/api/roles/global", resolve) == 200
    assert decide(amy, "PATCH", "/api/roles/global", resolve) == 403
    # M8.1：全域角色的人工登入交給路由查綁定；指定誰能用只有系統管理員
    assert decide(amy, "POST", "/api/roles/global/login", resolve) == 200
    assert decide(amy, "POST", "/api/roles/global/grants", resolve) == 403


def test_system_pages_and_defaults() -> None:
    amy = user(sales="admin")
    for method, path in [
        ("GET", "/users"),
        ("GET", "/audit"),
        ("GET", "/api/audit/verify"),
        ("POST", "/api/users"),
        ("GET", "/devices"),
        ("PUT", "/api/secrets/ERP_PASSWORD"),
        ("PUT", "/api/settings/video"),
        ("POST", "/api/domains"),
        ("POST", "/api/projects"),
        ("POST", "/api/something-new"),  # 沒有列出的寫入：預設拒絕
    ]:
        assert decide(amy, method, path, resolve) == 403, (method, path)
    for method, path in [
        ("GET", "/api/secrets"),
        ("GET", "/api/settings/batches"),
        ("GET", "/api/me"),
        ("POST", "/api/me/password"),
        ("GET", "/scenes"),
        ("GET", "/api/something-new"),  # 沒有列出的 GET：登入就可以（清單另外篩選）
    ]:
        assert decide(amy, method, path, resolve) == 200, (method, path)
    for method, path in [("POST", "/api/users"), ("DELETE", "/api/domains/hr")]:
        assert decide(FULL_ACCESS, method, path, resolve) == 200


def test_rule_matching() -> None:
    rule, key = match_rule("GET", "/playground/runs/wr-1/replay")
    assert (rule.kind if rule else None, key) == ("workflow_run", "wr-1")
    rule, key = match_rule("GET", "/playground/7/batch")
    assert (rule.need if rule else None, key) == ("run", "7")
    rule, key = match_rule("GET", "/api/domains/sales/members")
    assert (rule.need if rule else None, key) == ("view", "sales")


def test_access_context() -> None:
    assert visible_domains() is None  # 背景工作：不限制
    with use_access(user(sales="runner", hr="viewer")):
        assert visible_domains() == frozenset({"sales", "hr"})
        assert visible_domains("run") == frozenset({"sales"})
        require("run", "sales")
        with pytest.raises(ServiceError) as hidden:
            require("view", "ops")
        assert hidden.value.status == 404
        with pytest.raises(ServiceError) as denied:
            require("edit", "sales")
        assert denied.value.status == 403
    with use_access(FULL_ACCESS):
        assert visible_domains() is None
        require("manage", None)
