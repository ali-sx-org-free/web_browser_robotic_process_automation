"""接著錄製（rpa_runner.record）的錄製器：在已經開好的瀏覽器上開始錄製，之後的操作寫進錄製稿。

``enable_recorder`` 用 Playwright 的內部 API（1.65 起是 ``BrowserContext._show_recorder``），
Playwright 改版時由這個測試發現（2026-11-26：升到 1.65 時 ``Channel.send`` 被拿掉，接著錄製壞掉）。
錄製器的 Inspector 平常開在有頭的視窗；這裡用 Playwright 自己測試用的環境變數
``PWTEST_CLI_HEADLESS`` 讓 Inspector 也用無頭模式，CI 的 Linux 沒有螢幕也能跑。
"""

import json
from collections.abc import Iterator
from pathlib import Path

import pytest
from playwright.sync_api import BrowserContext, sync_playwright

from rpa_runner import record
from rpa_runner.contexts import open_context
from rpa_runner.record import enable_recorder
from testsite.browsers import ENGINES, require_engine
from testsite.server import running

pytestmark = pytest.mark.browser

ROOT = Path(__file__).resolve().parents[3]
BA_001 = ROOT / "scenarios" / "demo" / "ba-001.yaml"

PAGE = """<!doctype html>
<html lang="zh-Hant"><body>
<label>帳號 <input id="account"></label>
<label>標題 <input id="title"></label>
<button onclick="document.querySelector('#saved').textContent = '已儲存'">儲存</button>
<p id="saved"></p>
</body></html>
"""


@pytest.fixture(params=ENGINES)
def engine(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> str:
    engine = require_engine(str(request.param))
    # Playwright 的 driver 在 sync_playwright() 時啟動、繼承環境變數
    monkeypatch.setenv("PWTEST_CLI_HEADLESS", "1")
    return engine


@pytest.fixture(scope="module")
def site() -> Iterator[str]:
    with running() as url:
        yield url


def test_recorder_writes_only_the_actions_after_it_starts(engine: str, tmp_path: Path) -> None:
    output = tmp_path / "recording.py"
    with sync_playwright() as playwright:
        browser = getattr(playwright, engine).launch()
        context = browser.new_context()
        page = context.new_page()
        page.set_content(PAGE)
        page.get_by_label("帳號").fill("replayed")  # 開始錄製前的操作（既有的步驟）

        enable_recorder(context, output)
        page.get_by_label("標題").fill("錄製測試")
        page.get_by_role("button", name="儲存").click()
        assert page.locator("#saved").inner_text() == "已儲存"
        context.close()  # 關掉時錄製器把錄製稿寫完
        browser.close()

    text = output.read_text(encoding="utf-8")
    assert '.fill("錄製測試")' in text, text
    assert 'get_by_role("button", name="儲存").click()' in text, text
    assert "replayed" not in text, text


def test_continue_recording_after_the_existing_steps(
    engine: str,
    site: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """整個子程序的流程：執行 BA-001 既有的步驟，再開始錄製；使用者操作完關掉視窗就結束。

    瀏覽器平常是有頭的，這裡換成無頭；使用者的操作與關掉視窗由測試代替。
    """

    def headless(*args: object, **kwargs: object) -> BrowserContext:
        return open_context(*args, **{**kwargs, "headed": False})  # pyright: ignore[reportArgumentType]

    def user(context: BrowserContext) -> None:
        page = context.pages[0]
        assert page.locator("#receipt").is_visible()  # 既有的步驟已經建立了紀錄
        page.get_by_label("標題", exact=True).fill("接著錄製")
        page.get_by_role("link", name="查詢紀錄").click()
        page.close()

    monkeypatch.setattr(record, "open_context", headless)
    monkeypatch.setattr(record, "_wait_closed", user)
    (tmp_path / "input.json").write_text("{}", encoding="utf-8")
    output = tmp_path / "recording.py"

    code = record.main(
        [
            "--scenario",
            str(BA_001),
            "--input",
            str(tmp_path / "input.json"),
            "--output",
            str(output),
            "--out",
            str(tmp_path / "out"),
            "--engine",
            engine,
            "--base-url",
            site,
        ]
    )

    events = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert code == 0, events
    assert [event["event"] for event in events] == ["replaying", "recording"], events
    text = output.read_text(encoding="utf-8")
    assert '.fill("接著錄製")' in text, text
    assert 'get_by_role("link", name="查詢紀錄").click()' in text, text
    assert "介面驗證範例" not in text, text  # 既有步驟填的標題不在錄製稿裡
