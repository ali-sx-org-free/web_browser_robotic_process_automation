"""子場景的檔案入參與出參（M7.2 收尾）：不用瀏覽器的部分。"""

from collections.abc import Iterator
from pathlib import Path

import pytest

from rpa_core.dsl import validate_text
from rpa_core.dsl.files import file_meta
from rpa_core.dsl.scenario import Scenario
from rpa_core.i18n import use_locale
from rpa_runner.callfiles import callee_file_outputs, callee_files, caller_index
from rpa_runner.contract import check_inputs

CALLEE = """\
schemaVersion: 1
id: upload-one
name: 上傳
inputs:
  title: { type: string }
  sheet: { type: file, accept: [.csv] }
  photos: { type: file, multiple: true, maxSize: 10B }
steps:
  - { id: open, action: goto, url: 'https://example.test/' }
  - { id: export, action: download, target: { text: 匯出 }, as: exported }
verify:
  - { name: 有下載, value: '{{ facts.exported.name }}', notEmpty: true }
outputs:
  report: { type: file, from: '{{ facts.exported }}' }
"""


@pytest.fixture(autouse=True)
def _zh_hant() -> Iterator[None]:
    with use_locale("zh-Hant"):
        yield


def scenario(text: str = CALLEE) -> Scenario:
    result = validate_text(text)
    assert result.scenario is not None, result.issues
    return result.scenario


def staged(folder: Path, name: str, data: bytes) -> tuple[Path, dict[str, object]]:
    """呼叫場景準備好的檔案（暫存資料夾裡以網頁看到的檔名存放）與表達式看到的說明。"""
    path = folder / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path, file_meta(path, path.name).to_json()


def test_caller_files_and_workspace_files_become_callee_inputs(tmp_path: Path) -> None:
    orders, orders_meta = staged(tmp_path / "staging" / "orders" / "0", "訂單.csv", b"a,b\n")
    one, one_meta = staged(tmp_path / "staging" / "pics" / "0", "1.png", b"png1")
    two, two_meta = staged(tmp_path / "staging" / "pics" / "1", "2.png", b"png2")
    workspace = tmp_path / "workspace"
    got, got_meta = staged(workspace / "downloads", "下載.png", b"png3")
    index = caller_index(
        {"orders": orders_meta, "pics": [one_meta, two_meta], "note": "x"},
        {"orders": [orders], "pics": [one, two]},
    )
    callee = scenario()
    given: dict[str, object] = {
        "title": "t",
        "sheet": orders_meta,
        # 多檔：整個多檔入參加上一個下載的檔案（download 步驟的事實）
        "photos": [[one_meta, two_meta], {"workspace": "downloads/下載.png", **got_meta}],
    }
    prepared = callee_files(callee, given, index, workspace)
    assert prepared.problems == []
    assert prepared.paths == {
        "sheet": [orders],
        "photos": [one, two, workspace / "downloads/下載.png"],
    }
    assert prepared.meta["sheet"] == orders_meta
    assert prepared.meta["photos"] == [one_meta, two_meta, got_meta]
    assert got.is_file()
    # 其他入參照常檢查；檔案入參略過（另外準備）
    inputs, problems = check_inputs(callee, {"title": "t"}, skip={"sheet", "photos"})
    assert (inputs, problems) == ({"title": "t"}, [])


def test_unknown_or_unsuitable_files_are_problems(tmp_path: Path) -> None:
    orders, orders_meta = staged(tmp_path / "s" / "a", "訂單.csv", b"a,b\n")
    big, big_meta = staged(tmp_path / "s" / "b", "大.png", b"x" * 11)
    text, text_meta = staged(tmp_path / "s" / "c", "說明.txt", b"hi")
    index = caller_index(
        {"orders": orders_meta, "big": big_meta, "text": text_meta},
        {"orders": [orders], "big": [big], "text": [text]},
    )
    callee = scenario()

    def problems(given: dict[str, object]) -> list[str]:
        found = callee_files(callee, given, index, tmp_path / "workspace").problems
        return [problem.message for problem in found]

    # 單檔入參給了兩個；不是呼叫場景的檔案（其他事實、工作資料夾外面、不存在）
    assert problems({"sheet": [orders_meta, orders_meta], "photos": []}) == [
        "子場景的檔案入參 sheet 只收一個檔案，給了 2 個"
    ]
    for value in ({"recordId": "R-1"}, {"workspace": "../etc/passwd"}, {"workspace": "no.csv"}):
        found = problems({"sheet": value, "photos": []})
        assert len(found) == 1
        assert "不是呼叫場景的檔案入參" in found[0]
    # 類型與大小照子場景的契約
    found = problems({"sheet": text_meta, "photos": [big_meta]})
    assert "accept: .csv" in found[0]
    assert "太大" in found[1]
    # 沒給檔案入參（校驗會先擋下，這裡是保險）
    assert problems({"photos": []}) == ["缺少入參 sheet"]


def test_file_outputs_stay_in_the_workspace(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    _, meta = staged(workspace / "downloads", "報表.csv", b"1,2\n")
    callee = scenario()
    outputs: dict[str, object] = {"report": {"workspace": "downloads/報表.csv", **meta}}
    assert callee_file_outputs(callee, outputs, workspace) == []
    assert outputs == {"report": {"workspace": "downloads/報表.csv", **meta}}
    # 路徑寫法（相對於共用工作資料夾）也換成檔案說明
    outputs = {"report": "downloads/報表.csv"}
    assert callee_file_outputs(callee, outputs, workspace) == []
    assert outputs["report"] == {"workspace": "downloads/報表.csv", **meta}
    # 工作資料夾外面的檔案不行；有問題時不改出參
    outside, _ = staged(tmp_path / "elsewhere", "x.csv", b"x")
    outputs = {"report": str(outside)}
    found = callee_file_outputs(callee, outputs, workspace)
    assert [problem.name for problem in found] == ["report"]
    assert outputs == {"report": str(outside)}
