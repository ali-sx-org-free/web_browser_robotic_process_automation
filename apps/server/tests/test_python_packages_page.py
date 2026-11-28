"""套件管理頁（ADR 0027）：``/python-packages`` 頁面與 ``/api/python-packages…`` 的 API。

用伺服器內附的預設套件（#1），不連網、不解析：檢查的結果直接寫進草稿（解析、下載在
test_python_packages.py）。要登入的權限規則在 test_gate.py。
"""

from typing import cast

from fastapi import FastAPI
from httpx2 import Client, Response

from rpa_core.i18n import use_locale
from rpa_server.models import PythonPackageSet
from rpa_server.pypackages.routes import describe
from rpa_server.services import Services

JsonObject = dict[str, object]
API = "/api/python-packages"

NODE = """\
schemaVersion: 1
id: py-report
name: 月報
script:
  runtime: '1'
  automation: automation.py
verify:
  - { value: '{{ facts.done }}', matches: '^yes$' }
"""
AUTOMATION = """\
import requests
from pptx import Presentation

from rpa_script import automation


@automation
def main(run):
    run.facts["done"] = "yes"
"""


def services(app: FastAPI) -> Services:
    return cast("Services", app.state.services)


def body(response: Response, status: int = 200) -> JsonObject:
    assert response.status_code == status, response.text
    data: object = response.json()
    assert isinstance(data, dict)
    return cast("JsonObject", data)


def error_code(response: Response, status: int) -> str:
    error = cast("JsonObject", body(response, status)["error"])
    return str(error["code"])


def names(revision: JsonObject) -> list[str]:
    return [
        str(cast("JsonObject", item)["name"])
        for item in cast("list[object]", revision["requirements"])
    ]


def set_check(app: FastAPI, status: str, check: JsonObject) -> None:
    """把檢查的結果直接寫進草稿（不跑 uv）。"""
    with services(app).sessions() as session:
        row = session.query(PythonPackageSet).filter_by(number=None).one()
        row.status = status
        row.check = check
        session.commit()


def test_page_shows_the_current_set(client: Client) -> None:
    page = client.get("/python-packages")
    assert page.status_code == 200
    html = page.text
    assert 'href="/python-packages" title="Python 套件" class="active"' in html
    assert 'data-current="1"' in html
    assert "目前的版本：套件 #1" in html
    assert 'id="pkg-draft"' not in html  # 還沒有草稿
    # 預設套件每一列都能修改、移除；被需要而安裝的另外列
    row = html.split('data-package="')[1].split("</tr>")[0]
    assert "預設" in row
    assert 'data-action="pkg-edit"' in row
    assert 'data-action="pkg-remove"' in row
    assert "被需要而安裝的其他套件" in html
    # 找套件：常用套件的用途在 title、套件來源的選項
    assert 'data-lookup="python-pptx" title="讀寫 PowerPoint（.pptx）"' in html
    assert '<option value="auto" selected>自動（測速後用最快的）</option>' in html
    assert '<option value="tuna">清華大學 TUNA</option>' in html
    assert "還沒有登記遠端 Worker" in html

    overview = body(client.get(API))
    assert overview["current"] == 1
    assert overview["draft"] is None
    assert cast("JsonObject", overview["revision"])["number"] == 1
    assert "requests" in names(cast("JsonObject", overview["revision"]))
    assert overview["devices"] == []


def test_draft_add_remove_and_discard(app: FastAPI, client: Client) -> None:
    added = body(
        client.post(
            f"{API}/draft/packages",
            json={
                "name": "python-pptx",
                "spec": ">=1.0",
                "platforms": ["windows", "x"],
                "note": "月報",
            },
        )
    )
    assert added["status"] == "draft"
    assert "python-pptx" in names(added)
    pptx = next(
        cast("JsonObject", item)
        for item in cast("list[object]", added["requirements"])
        if cast("JsonObject", item)["name"] == "python-pptx"
    )
    assert pptx["platforms"] == ["windows"]  # 不認得的系統不收
    assert pptx["addedBy"] is None or isinstance(pptx["addedBy"], str)

    removed = body(client.post(f"{API}/draft/remove", json={"name": "requests"}))
    assert "requests" not in names(removed)

    html = client.get("/python-packages").text
    assert 'id="pkg-draft"' in html
    assert "套件清單（草稿）" in html
    assert 'data-action="pkg-check"' in html
    assert 'data-action="pkg-upgrade" disabled' in html  # 有草稿時不能檢查更新
    assert 'data-action="pkg-restore"' not in html  # 只有一版
    new_row = html.split("<strong>python-pptx</strong>")[1].split("</tr>")[0]
    assert "新加" in new_row
    assert "檢查後決定" in new_row  # 版本要檢查後才知道
    assert "Windows" in new_row
    assert "<s>requests</s>" in html
    assert "將移除" in html.split("<s>requests</s>")[1].split("</tr>")[0]

    # 不能加的名稱
    assert error_code(client.post(f"{API}/draft/packages", json={"name": "pip"}), 422) == (
        "package_blocked_tool"
    )
    assert error_code(client.post(f"{API}/draft/packages", json={"name": "bad name!"}), 422) == (
        "package_invalid_name"
    )
    # 沒檢查不能發布
    assert error_code(client.post(f"{API}/draft/publish", json={}), 409) == "package_not_checked"

    assert client.delete(f"{API}/draft").status_code == 204
    assert body(client.get(API))["draft"] is None
    assert 'id="pkg-draft"' not in client.get("/python-packages").text


def test_page_shows_check_results(app: FastAPI, client: Client) -> None:
    body(client.post(f"{API}/draft/packages", json={"name": "python-pptx"}))
    set_check(
        app,
        "failed",
        {
            "steps": [
                {"id": "resolve", "status": "passed"},
                {"id": "platforms", "status": "failed"},
            ],
            "errors": [
                {"code": "platform_failed", "platform": "macos-arm64", "detail": "no wheels"},
                {"code": "something_new"},
            ],
            "warnings": [{"code": "cooldown", "packages": ["a", "b"], "days": 7}],
        },
    )
    html = client.get("/python-packages").text
    assert "檢查沒有通過" in html
    assert "確認每個平台都有 wheel" in html
    assert "macos-arm64 沒辦法安裝" in html
    assert '<pre class="source">no wheels</pre>' in html
    assert "<li>something_new</li>" in html  # 不認得的代碼原樣顯示
    assert "a、b 是 7 天內上架的" in html
    assert 'data-action="pkg-check"' in html  # 可以再檢查

    set_check(
        app,
        "checked",
        {
            "steps": [{"id": "resolve", "status": "passed"}],
            "diff": {
                "added": [["python-pptx", "1.0.2"]],
                "changed": [["lxml", "5.3.0", "5.3.1"]],
                "removed": [],
            },
            "sizes": {"linux-x86_64": {"total": 2048, "new": 1024, "newFiles": 2}},
        },
    )
    html = client.get("/python-packages").text
    assert "檢查通過" in html
    assert "和套件 #1 比" in html
    assert "python-pptx 1.0.2" in html
    assert "lxml 5.3.0 → 5.3.1" in html
    assert "（2 個檔案）" in html
    assert 'data-action="pkg-publish" data-number="2"' in html
    assert "發布成套件 #2" in html


def test_scenes_that_need_packages(app: FastAPI, client: Client) -> None:
    assert client.post("/api/scenes", json={"id": "py-report", "name": "暫名"}).status_code == 201
    files = {"scenario.yaml": NODE, "automation.py": AUTOMATION}
    created = client.post(
        "/api/scenes/py-report/revisions", json={"baseRevision": 1, "files": files}
    )
    assert created.status_code == 201, created.text

    # 清單裡沒有 pptx：建議 python-pptx
    html = client.get("/python-packages").text
    missing = html.split("場景用到、清單裡沒有的模組")[1].split("</table>")[0]
    assert '<td class="mono">pptx</td><td>python-pptx</td>' in missing
    assert '<a href="/scenes/py-report">月報</a> v2' in missing
    assert "未發布" in missing
    assert "requests" not in missing

    scenes = cast("list[JsonObject]", body(client.get(f"{API}/impact?name=requests"))["scenes"])
    assert [(item["sceneId"], item["published"], item["modules"]) for item in scenes] == [
        ("py-report", False, ["requests"])
    ]
    # 草稿用到不必寫原因（已發布的才要）
    assert "requests" not in names(
        body(client.post(f"{API}/draft/remove", json={"name": "requests"}))
    )


def test_settings_and_devices(app: FastAPI, client: Client) -> None:
    settings: JsonObject = {
        "source": "tuna",
        "customUrl": "",
        "proxy": "",
        "caFile": "",
        "cooldownDays": 3,
        "parallel": 2,
        "workerDownloads": 4,
        "keepVersions": 5,
    }
    saved = body(client.put(f"{API}/settings", json=settings))
    assert (saved["source"], saved["cooldownDays"], saved["workerDownloads"]) == ("tuna", 3, 4)
    bad = client.put(
        f"{API}/settings", json={**settings, "source": "custom", "customUrl": "ftp://x"}
    )
    assert error_code(bad, 422) == "package_custom_url"
    assert client.put(f"{API}/settings", json={**settings, "parallel": 0}).status_code == 422

    created = client.post("/api/workers", json={"id": "py-box", "name": "機房 Linux"})
    assert created.status_code == 201, created.text
    services(app).packages.report("py-box", {"revision": 1, "state": "failed", "error": "磁碟滿了"})
    html = client.get("/python-packages").text
    assert '<option value="tuna" selected>' in html
    assert 'name="cooldownDays" min="0" max="365" value="3"' in html
    devices = html.split('id="pkg-devices"')[1].split("</section>")[0]
    assert "機房 Linux" in devices
    assert "準備失敗" in devices
    assert "磁碟滿了" in devices
    device = cast("list[JsonObject]", body(client.get(API))["devices"])[0]
    assert (device["id"], device["state"], device["revision"]) == ("py-box", "failed", 1)


def test_describe_issues() -> None:
    with use_locale("zh-Hant"):
        assert describe({"code": "still_needed", "packages": ["idna"]}).startswith("idna 從清單")
        assert describe({"code": "no_wheel", "detail": "demo 1.0"}).startswith("demo 1.0 沒有")
        assert describe({"code": "unknown_thing"}) == "unknown_thing"
    with use_locale("en"):
        assert describe({"code": "cooldown", "packages": ["a", "b"], "days": 7}).startswith(
            "a, b were released within 7 days"
        )
