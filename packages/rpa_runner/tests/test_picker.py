"""點選元素產生 DSL 定位器（登入角色的引導，2026-11-10）：點選層、寫法的順序、在頁面上驗證。

寫法的規則不需要瀏覽器；點選層與驗證在 Chromium 與 Firefox 各跑一次（本機沒有時略過，
CI 設定 RPA_REQUIRE_BROWSER=1 時缺瀏覽器直接失敗）。``pick`` 子程序的命令流程另外測一次。
"""

import json
import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import cast

import pytest
from playwright.sync_api import Page, sync_playwright

from rpa_core.i18n import ENV_VAR
from rpa_runner.login import ENV_LOGIN, EXIT_CANCELLED, LoginSettings
from rpa_runner.picker import candidates, install, picked, remove, verify
from testsite.browsers import ENGINES, require_engine

PAGE = """<!doctype html>
<html lang="zh-Hant"><body>
<header>
  <span id="user-name">王小明</span>
  <button data-testid="logout" onclick="window.clicked = 'logout'">
    <i class="icon" style="display:inline-block;width:12px;height:12px"></i>登出
  </button>
  <a href="#me" title="我的帳號" onclick="window.clicked = 'me'">
    <img alt="頭像" width="20" height="20" src="data:image/gif;base64,R0lGODlhAQABAAAAACw=">
  </a>
  <button id="menu-18273645">選單</button>
</header>
<p>王小明 的待辦</p>
</body></html>
"""


def test_candidates_follow_the_recommended_order() -> None:
    """測試代號、角色與名稱、文字、title、alt、#id；點到按鈕裡的圖示時用按鈕的。"""
    chain: list[dict[str, object]] = [
        {"tag": "i", "text": ""},
        {"tag": "button", "testId": "logout", "text": "登出", "id": "logout-button"},
        {"tag": "header", "testId": "page-header", "text": "王小明 登出"},
    ]
    assert candidates(chain) == [
        {"testId": "logout"},
        {"role": "button", "name": "登出"},
        {"text": "登出"},
        {"css": "#logout-button"},
    ]
    link = [{"tag": "img", "alt": "頭像"}, {"tag": "a", "href": True, "title": "我的帳號"}]
    assert candidates(link) == [
        {"role": "img", "name": "頭像"},
        {"title": "我的帳號"},
        {"altText": "頭像"},
    ]
    # 寫明的 role 優先；DSL 不認得的 role、太長的文字、程式產生的 id 都不用
    assert candidates([{"tag": "div", "role": "menuitem", "ariaLabel": "設定"}]) == [
        {"role": "menuitem", "name": "設定"}
    ]
    assert candidates([{"tag": "div", "role": "nope", "text": "x" * 41, "id": "ember1234"}]) == []
    # 再往上的容器（第四層）不拿來當寫法：登入前多半也看得到
    deep = [{"tag": "span"}, {"tag": "span"}, {"tag": "span"}, {"tag": "nav", "testId": "nav"}]
    assert candidates(deep) == []


@pytest.fixture(params=ENGINES)
def engine(request: pytest.FixtureRequest) -> str:
    return require_engine(str(request.param))


@pytest.fixture
def page(engine: str) -> Iterator[Page]:
    with sync_playwright() as playwright:
        browser = getattr(playwright, engine).launch()
        try:
            page = cast("Page", browser.new_page())
            page.set_content(PAGE)
            yield page
        finally:
            browser.close()


@pytest.mark.browser
def test_clicking_an_element_lists_locators_that_find_it(page: Page) -> None:
    install(page)
    assert picked(page) is None
    page.hover("#user-name")
    assert page.locator("[data-rpa-pick]").count() == 2  # 框與標籤
    page.click("[data-testid=logout] .icon")
    chain = picked(page)
    assert chain is not None
    assert [item["tag"] for item in chain[:2]] == ["i", "button"]
    # 這次點擊沒有傳給網頁，點選層也拿掉了
    assert page.evaluate("window.clicked || null") is None
    assert page.locator("[data-rpa-pick]").count() == 0

    found = verify(page, candidates(chain))
    assert [item.text for item in found] == [
        "{ testId: logout }",
        "{ role: button, name: 登出 }",
        "{ text: 登出 }",
    ]
    assert all(item.count == 1 and item.visible for item in found)
    assert found[0].to_json() == {
        "locator": {"testId": "logout"},
        "text": "{ testId: logout }",
        "count": 1,
        "visible": True,
    }

    # 文字在頁面上出現兩次：只有一個的寫法排前面；程式產生的 id 不列
    install(page)
    page.click("#user-name")
    chain = picked(page)
    assert chain is not None
    found = verify(page, candidates(chain))
    assert [(item.text, item.count) for item in found] == [
        ('{ css: "#user-name" }', 1),
        ("{ text: 王小明 }", 2),
    ]
    install(page)
    page.click("#menu-18273645")
    chain = picked(page)
    assert chain is not None
    assert [item.text for item in verify(page, candidates(chain))] == [
        "{ role: button, name: 選單 }",
        "{ text: 選單 }",
    ]


@pytest.mark.browser
def test_removing_the_layer_lets_clicks_through(page: Page) -> None:
    install(page)
    remove(page)
    page.click("a[title]")
    assert page.evaluate("window.clicked") == "me"
    assert picked(page) is None


def _events(process: subprocess.Popen[str]) -> Iterator[dict[str, object]]:
    assert process.stdout is not None
    for line in process.stdout:
        yield cast("dict[str, object]", json.loads(line))


@pytest.mark.browser
def test_pick_command_flow(engine: str, tmp_path: Path) -> None:
    """子程序：ready → pick → picking → stop → stopped → cancel → cancelled（退出碼 2）。

    不存登入狀態。
    """
    settings = LoginSettings(role="pick", state=tmp_path / "unused.json", login_url="about:blank")
    process = subprocess.Popen(
        [sys.executable, "-m", "rpa_runner.login", "pick", "--headless", "--engine", engine],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        env={**os.environ, ENV_LOGIN: json.dumps(settings.to_json()), ENV_VAR: "zh-Hant"},
    )
    try:
        assert process.stdin is not None
        events = _events(process)
        assert next(events)["event"] == "ready"
        for command, expected in (
            ("pick", "picking"),
            ("stop", "stopped"),
            ("cancel", "cancelled"),
        ):
            process.stdin.write(command + "\n")
            process.stdin.flush()
            assert next(events)["event"] == expected
        assert process.wait(timeout=30) == EXIT_CANCELLED
    finally:
        if process.poll() is None:
            process.kill()
    assert not (tmp_path / "unused.json").exists()
