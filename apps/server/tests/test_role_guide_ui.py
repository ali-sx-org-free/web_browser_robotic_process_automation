"""登入角色表單的引導（2026-11-10）：在真的瀏覽器裡操作表單。

點選與自己填都填進「已登入時看得到的元素」。頁面由 :func:`rpa_server.render.render` 產生，
靜態檔案與 ``/api/locator-picks`` 由 Playwright 攔截回應（點選子程序與伺服器的部分在
test_production_api.py 測）。
"""

import json
from collections.abc import Iterator
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import Page, Route, sync_playwright

from rpa_core.i18n import use_locale
from rpa_server.domain import RoleRecord
from rpa_server.render import render
from testsite.browsers import require_engine

pytestmark = pytest.mark.browser

STATIC = Path(__file__).resolve().parents[1] / "src" / "rpa_server" / "static"
ORIGIN = "http://portal.test"
CANDIDATES = [
    {
        "locator": {"testId": "current-user"},
        "text": "{ testId: current-user }",
        "count": 1,
        "visible": True,
    },
    {"locator": {"text": "王小明"}, "text": "{ text: 王小明 }", "count": 2, "visible": False},
]


def _no_text(role: RoleRecord) -> str:
    return ""


def _no_values(role: RoleRecord) -> dict[str, object]:
    return {}


def _page_html(*, display: bool) -> str:
    with use_locale("zh-Hant"):
        return render(
            "roles.html",
            page="roles",
            title="登入與憑證",
            roles=list[RoleRecord](),
            secrets=[],
            usage={},
            missing=[],
            environ=set[str](),
            display=display,
            check_unavailable={},
            busy=False,
            engines=("chromium", "firefox"),
            check_text=_no_text,
            role_values=_no_values,
            auto_example="",
            domain_names={},
        )


class _Picks:
    """假的 /api/locator-picks：開視窗 → ready；pick → picked；記下收到的請求。"""

    def __init__(self) -> None:
        self.status = "starting"
        self.calls: list[tuple[str, str, object]] = []

    def data(self) -> dict[str, object]:
        picked = self.status == "picked"
        return {
            "id": "p1",
            "status": self.status,
            "message": None,
            "url": "http://127.0.0.1:9/home#top" if picked else None,
            "candidates": CANDIDATES if picked else [],
            "deviceId": None,
        }

    def handle(self, route: Route) -> None:
        request = route.request
        path = urlsplit(request.url).path
        body = json.loads(request.post_data) if request.post_data else None
        self.calls.append((request.method, path, body))
        if request.method == "POST" and path == "/api/locator-picks":
            self.status = "starting"
            reply = self.data()
            self.status = "ready"  # 下一次查詢時視窗已經開好
        elif path.endswith("/pick"):
            self.status = "picked"
            reply = self.data()
        elif request.method == "DELETE":
            self.status = "closed"
            reply = self.data()
        else:
            reply = self.data()
        route.fulfill(status=200, content_type="application/json", body=json.dumps(reply))


@pytest.fixture
def page() -> Iterator[Page]:
    require_engine("chromium")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            yield browser.new_page()
        finally:
            browser.close()


def _open_form(page: Page, *, display: bool = True) -> _Picks:
    picks = _Picks()
    html = _page_html(display=display)

    def static(route: Route) -> None:
        name = urlsplit(route.request.url).path.rsplit("/", 1)[-1]
        route.fulfill(path=STATIC / name)

    page.route(f"{ORIGIN}/static/**", static)
    page.route(f"{ORIGIN}/api/locator-picks**", picks.handle)
    page.route(f"{ORIGIN}/roles", lambda route: route.fulfill(body=html, content_type="text/html"))
    page.goto(f"{ORIGIN}/roles")
    page.click('[data-action="new-role"]')
    page.click("[data-locator-guide] summary")
    return picks


def test_picking_fills_the_check_and_the_check_url(page: Page) -> None:
    picks = _open_form(page)
    dialog = page.locator("#dialog-content")
    status = dialog.locator("[data-guide-status]")
    dialog.locator('[data-guide="open"]').click()
    assert status.text_content() == "先填登入網址"
    assert picks.calls == []

    dialog.locator('[name="loginUrl"]').fill("http://127.0.0.1:9/login")
    dialog.locator('[name="engine"]').select_option("firefox")
    dialog.locator('[data-guide="open"]').click()
    pick = dialog.locator('[data-guide="pick"]')
    pick.wait_for()
    assert picks.calls[0] == (
        "POST",
        "/api/locator-picks",
        {"loginUrl": "http://127.0.0.1:9/login", "engine": "firefox"},
    )
    assert "瀏覽器已打開" in (status.text_content() or "")
    assert dialog.locator('[data-guide="open"]').is_hidden()

    pick.click()
    items = dialog.locator("[data-guide-candidates] li")
    items.first.wait_for()
    assert items.count() == 2
    assert items.nth(0).locator("code").text_content() == "{ testId: current-user }"
    assert "頁面上只有這 1 個" in (items.nth(0).text_content() or "")
    assert "頁面上有 2 個，會用第一個" in (items.nth(1).text_content() or "")
    assert "現在看不到" in (items.nth(1).text_content() or "")

    items.nth(0).locator("[data-guide-use]").click()
    assert dialog.locator('[name="check"]').input_value() == "{ testId: current-user }"
    assert dialog.locator('[name="checkUrl"]').input_value() == "http://127.0.0.1:9/home"
    assert "確認網址也換成點選時的網址" in (status.text_content() or "")
    assert ("DELETE", "/api/locator-picks/p1", None) in picks.calls
    assert dialog.locator("[data-guide-candidates]").is_hidden()
    assert dialog.locator('[data-guide="open"]').is_visible()


def test_closing_the_dialog_closes_the_browser(page: Page) -> None:
    picks = _open_form(page)
    dialog = page.locator("#dialog-content")
    dialog.locator('[name="loginUrl"]').fill("http://127.0.0.1:9/login")
    dialog.locator('[data-guide="open"]').click()
    dialog.locator('[data-guide="pick"]').wait_for()
    page.click("#dialog-close")
    page.wait_for_function("() => !document.querySelector('#dialog').open")
    page.wait_for_timeout(200)
    assert ("DELETE", "/api/locator-picks/p1", None) in picks.calls


def test_building_a_locator_without_a_browser(page: Page) -> None:
    _open_form(page, display=False)
    dialog = page.locator("#dialog-content")
    assert dialog.locator('[data-guide="open"]').is_disabled()
    assert "這台電腦沒有圖形介面" in (dialog.locator("[data-locator-guide]").text_content() or "")
    dialog.locator("[data-guide-kind]").select_option("button")
    assert dialog.locator("[data-guide-value]").get_attribute("placeholder") == "登出"
    assert "按鈕上的字" in (dialog.locator("[data-guide-kind-hint]").text_content() or "")
    dialog.locator('[data-guide="build"]').click()
    assert dialog.locator("[data-guide-status]").text_content() == "先填看到的內容"
    for kind, value, expected in (
        ("button", "登出", "{ role: button, name: 登出 }"),
        ("text", "My account", "{ text: My account }"),
        ("css", "#user-menu", '{ css: "#user-menu" }'),
        ("testId", "true", '{ testId: "true" }'),
    ):
        dialog.locator("[data-guide-kind]").select_option(kind)
        dialog.locator("[data-guide-value]").fill(value)
        dialog.locator('[data-guide="build"]').click()
        assert dialog.locator('[name="check"]').input_value() == expected
