"""批次執行（M7.3）的表格：讀入 CSV／TSV／xlsx、欄位對應、逐列換成入參、匯出。不需要資料庫。"""

import csv
import io
import zipfile
from collections.abc import Iterator
from datetime import date, datetime, time
from xml.etree import ElementTree
from xml.sax.saxutils import escape

import pytest

from rpa_core.dsl import Scenario, validate_text
from rpa_core.i18n import use_locale
from rpa_server.batch_table import (
    MAX_ROWS,
    ExportRow,
    TableError,
    default_mapping,
    export_csv,
    export_xlsx,
    parse_text,
    read_table,
    row_values,
)

SCENARIO = """\
schemaVersion: 1
id: batch-demo
name: 批次範例
inputs:
  title: { type: string, minLength: 1, maxLength: 20 }
  quantity: { type: integer, minimum: 1, maximum: 30, default: 1 }
  price: { type: number, default: 0 }
  urgent: { type: boolean, default: false }
  tags: { type: array, default: [] }
  sheet: { type: file, default: files/a.csv }
steps:
  - { id: open, action: goto, url: 'https://example.test/' }
"""


@pytest.fixture(autouse=True)
def _zh_hant() -> Iterator[None]:
    with use_locale("zh-Hant"):
        yield


@pytest.fixture
def scenario() -> Scenario:
    result = validate_text(SCENARIO)
    assert result.scenario is not None, result.issues
    return result.scenario


MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
RELATIONSHIPS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
EPOCH = datetime(1899, 12, 30)
"""Excel 的日期是從這一天起算的天數（1900 制，1900-03-01 以後）。"""


def serial(value: date | datetime | time) -> float:
    if isinstance(value, datetime):
        delta = value - EPOCH
        return delta.days + delta.seconds / 86400
    if isinstance(value, date):
        return float((value - EPOCH.date()).days)
    return (value.hour * 3600 + value.minute * 60 + value.second) / 86400


def zipped(files: dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as book:
        for name, content in files.items():
            book.writestr(name, content)
    return buffer.getvalue()


def xlsx(rows: list[list[object]], number_formats: dict[str, str] | None = None) -> bytes:
    """照 Excel 存檔的樣子寫一個工作表：文字是共用字串，數字、是非照原樣，日期與時間是序號，
    ``number_formats``（儲存格 → 數字格式）寫成自訂格式。

    不用 openpyxl：伺服器的依賴沒有它，測試環境也不一定有。
    """
    formats = number_formats or {}
    codes = sorted(set(formats.values()))
    style_of = {code: index + 1 for index, code in enumerate(codes)}
    strings: list[str] = []
    lines: list[str] = []
    for number, row in enumerate(rows, start=1):
        cells: list[str] = []
        for index, value in enumerate(row):
            reference = f"{chr(ord('A') + index)}{number}"
            code = formats.get(reference)
            style = f' s="{style_of[code]}"' if code is not None else ""
            if value is None:
                continue
            if isinstance(value, bool):
                cells.append(f'<c r="{reference}" t="b"{style}><v>{int(value)}</v></c>')
            elif isinstance(value, int | float):
                cells.append(f'<c r="{reference}"{style}><v>{value}</v></c>')
            elif isinstance(value, date | datetime | time):
                cells.append(f'<c r="{reference}"{style}><v>{serial(value)}</v></c>')
            else:
                strings.append(str(value))
                cells.append(f'<c r="{reference}" t="s"{style}><v>{len(strings) - 1}</v></c>')
        lines.append(f'<row r="{number}">{"".join(cells)}</row>')
    custom = "".join(
        f'<numFmt numFmtId="{163 + index}" formatCode="{escape(code, {chr(34): "&quot;"})}"/>'
        for code, index in style_of.items()
    )
    styles = "".join(
        f'<xf numFmtId="{163 + index}" applyNumberFormat="1"/>' for index in style_of.values()
    )
    shared = "".join(f"<si><t>{escape(text)}</t></si>" for text in strings)
    return zipped(
        {
            "xl/workbook.xml": (
                f'<workbook xmlns="{MAIN}" xmlns:r="{RELATIONSHIPS}">'
                '<sheets><sheet name="工作表1" sheetId="1" r:id="rId1"/></sheets></workbook>'
            ),
            "xl/_rels/workbook.xml.rels": (
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/'
                'relationships"><Relationship Id="rId1" Type="worksheet" '
                'Target="worksheets/sheet1.xml"/></Relationships>'
            ),
            "xl/sharedStrings.xml": f'<sst xmlns="{MAIN}">{shared}</sst>',
            "xl/styles.xml": (
                f'<styleSheet xmlns="{MAIN}"><numFmts>{custom}</numFmts>'
                f'<cellXfs><xf numFmtId="0"/>{styles}</cellXfs></styleSheet>'
            ),
            "xl/worksheets/sheet1.xml": (
                f'<worksheet xmlns="{MAIN}"><sheetData>{"".join(lines)}</sheetData></worksheet>'
            ),
        }
    )


# ---------------------------------------------------------------- 讀入


def test_csv_with_bom_and_blank_rows() -> None:
    data = "﻿title,quantity\n文具,3\n\n,\n紙張,5\n".encode()

    table = read_table("orders.csv", data)

    assert table.columns == ("title", "quantity")
    assert table.rows == (("文具", "3"), ("紙張", "5"))
    assert table.records()[1] == {"title": "紙張", "quantity": "5"}


def test_pasted_from_excel_is_tab_separated() -> None:
    table = parse_text("title\tquantity\r\n文具, 紅色\t3\r\n紙張\t\r\n")

    assert table.columns == ("title", "quantity")
    assert table.rows == (("文具, 紅色", "3"), ("紙張", ""))


def test_big5_csv_from_traditional_chinese_excel() -> None:
    data = "title,quantity\n文具,3\n".encode("cp950")

    assert read_table("x.csv", data).rows == (("文具", "3"),)


def test_short_rows_are_padded_and_untitled_empty_columns_dropped() -> None:
    table = parse_text("title,quantity,\n文具\n紙張,5,\n")

    assert table.columns == ("title", "quantity")
    assert table.rows == (("文具", ""), ("紙張", "5"))


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("", "表格是空的"),
        ("title,quantity\n", "沒有資料列"),
        ("title,title\na,b\n", "標題重複：title"),
        ("title,\na,b\n", "第 2 欄有資料但沒有標題"),
    ],
)
def test_table_problems(text: str, message: str) -> None:
    with pytest.raises(TableError, match=message):
        parse_text(text)


def test_row_limit() -> None:
    lines = ["title"] + [f"r{number}" for number in range(MAX_ROWS + 1)]

    with pytest.raises(TableError, match="最多 1000 列"):
        parse_text("\n".join(lines))
    assert len(parse_text("\n".join(lines[:-1])).rows) == MAX_ROWS


def test_old_xls_is_refused() -> None:
    with pytest.raises(TableError, match=r"\.xls"):
        read_table("orders.xls", b"\xd0\xcf\x11\xe0")


def test_xlsx_values_dates_and_numbers() -> None:
    data = xlsx(
        [
            ["title", "quantity", "price", "urgent", "day", "moment", "clock", "code"],
            [
                "文具",
                3,
                12.5,
                True,
                date(2026, 11, 13),
                datetime(2026, 11, 13, 9, 30),
                time(8, 5),
                "007",
            ],
            ["紙張", 5.0, 1200, False, None, None, None, "=1+1"],
        ],
        {"E2": "yyyy/mm/dd", "F2": "yyyy-mm-dd hh:mm", "G2": "h:mm:ss", "C3": "#,##0"},
    )

    table = read_table("orders.xlsx", data)

    assert table.columns == (
        "title",
        "quantity",
        "price",
        "urgent",
        "day",
        "moment",
        "clock",
        "code",
    )
    assert table.rows[0] == (
        "文具",
        "3",
        "12.5",
        "true",
        "2026-11-13",
        "2026-11-13 09:30:00",
        "08:05:00",
        "007",
    )
    assert table.rows[1][:4] == ("紙張", "5", "1200", "false")


def test_xlsx_shared_strings_rich_text_formulas_and_1904_dates() -> None:
    """Excel 存的檔多半用共用字串（sharedStrings），有的是多段格式的文字（<r>）、注音（<rPh>）；
    公式取 Excel 存下的計算結果；Mac 的舊檔用 1904 制的日期。工作表的位置照 workbook 的關聯找，
    不一定是 sheet1。"""
    files = {
        "xl/workbook.xml": (
            f'<workbook xmlns="{MAIN}" xmlns:r="http://schemas.openxmlformats.org/'
            'officeDocument/2006/relationships"><workbookPr date1904="1"/>'
            '<sheets><sheet name="資料" sheetId="1" r:id="rId7"/></sheets></workbook>'
        ),
        "xl/_rels/workbook.xml.rels": (
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId7" Type="worksheet" Target="worksheets/data.xml"/>'
            "</Relationships>"
        ),
        "xl/sharedStrings.xml": (
            f'<sst xmlns="{MAIN}"><si><t>title</t></si><si><t>day</t></si>'
            "<si><r><t>第</t></r><r><t>一</t></r><rPh><t>ㄉㄧˋ</t></rPh></si>"
            "<si><t>sum</t></si><si><t>label</t></si><si><t>later</t></si></sst>"
        ),
        "xl/styles.xml": (
            f'<styleSheet xmlns="{MAIN}"><cellXfs><xf numFmtId="0"/><xf numFmtId="14"/>'
            "</cellXfs></styleSheet>"
        ),
        "xl/worksheets/data.xml": (
            f'<worksheet xmlns="{MAIN}"><sheetData>'
            '<row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c>'
            '<c r="C1" t="s"><v>3</v></c><c r="D1" t="s"><v>4</v></c>'
            '<c r="E1" t="s"><v>5</v></c></row>'
            '<row r="3"><c r="A3" t="s"><v>2</v></c><c r="B3" s="1"><v>0</v></c>'
            '<c r="C3"><f>1+1</f><v>2</v></c><c r="D3" t="str"><f>A1&amp;"!"</f><v>title!</v></c>'
            '<c r="E3"><f>NOW()</f></c></row>'
            "</sheetData></worksheet>"
        ),
    }

    table = read_table("a.xlsx", zipped(files))

    assert table.columns == ("title", "day", "sum", "label", "later")
    # 沒有存下計算結果的公式讀成空白
    assert table.rows == (("第一", "1904-01-01", "2", "title!", ""),)


def test_broken_xlsx() -> None:
    with pytest.raises(TableError, match="Excel 檔讀不出來"):
        read_table("a.xlsx", b"PK\x03\x04 not really a zip")


# ---------------------------------------------------------------- 欄位對應與入參


def test_default_mapping(scenario: Scenario) -> None:
    mapping = default_mapping(scenario, ["Title", "quantity", "價格", "URGENT"])

    assert mapping == {
        "title": "Title",
        "quantity": "quantity",
        "price": None,
        "urgent": "URGENT",
        "tags": None,
        "sheet": None,
    }


def test_row_values_convert_by_type(scenario: Scenario) -> None:
    mapping = {
        "title": "標題",
        "quantity": "數量",
        "price": "價格",
        "urgent": "急件",
        "tags": "標籤",
    }
    cells = {"標題": " 文具 ", "數量": "1,2", "價格": "1,200.5", "急件": "是", "標籤": '["a", "b"]'}

    values, problems = row_values(scenario, mapping, {**cells, "數量": "12"})

    assert problems == []
    assert values == {
        "title": " 文具 ",
        "quantity": 12,
        "price": 1200.5,
        "urgent": True,
        "tags": ["a", "b"],
    }
    _, wrong = row_values(scenario, mapping, cells)
    assert [(item.input, item.column) for item in wrong] == [("quantity", "數量")]
    assert "不是整數" in wrong[0].message


def test_empty_cells_use_defaults_and_missing_required_is_reported(scenario: Scenario) -> None:
    values, problems = row_values(scenario, {"title": "標題"}, {"標題": "  "})

    assert values == {}
    assert [(item.input, item.column) for item in problems] == [("title", "標題")]
    assert "title" in problems[0].message


def test_contract_violations_and_dynamic_values(scenario: Scenario) -> None:
    mapping = {"title": "t", "quantity": "q", "sheet": "s"}

    _, problems = row_values(scenario, mapping, {"t": "x" * 21, "q": "31", "s": "a.csv"})

    assert sorted(item.input or "" for item in problems) == ["quantity", "sheet", "title"]
    assert any("檔案入參" in item.message for item in problems)
    values, ok = row_values(scenario, mapping, {"t": "{{today}}", "q": "{{random:10:20}}"})
    assert ok == []
    assert values == {"title": "{{today}}", "quantity": "{{random:10:20}}"}


@pytest.mark.parametrize(
    ("cell", "expected"),
    [("true", True), ("FALSE", False), ("1", True), ("0", False), ("否", False), ("yes", True)],
)
def test_booleans(scenario: Scenario, cell: str, expected: bool) -> None:
    values, problems = row_values(scenario, {"title": "t", "urgent": "u"}, {"t": "a", "u": cell})

    assert problems == []
    assert values["urgent"] is expected


# ---------------------------------------------------------------- 匯出


def rows() -> list[ExportRow]:
    return [
        ExportRow(
            1,
            {"title": "文具", "quantity": "3"},
            "passed",
            "run-1",
            {"recordId": "DEMO-1", "tags": ["a"]},
            None,
            1,
        ),
        ExportRow(
            2, {"title": '=HYPERLINK("x")', "quantity": "-5"}, "failed", "run-2", None, "逾時", 2
        ),
        ExportRow(3, {"title": "", "quantity": ""}, "invalid", None, None, "缺少 title", 0),
    ]


def test_export_csv_opens_in_excel_and_is_safe() -> None:
    data = export_csv(["title", "quantity"], ["recordId", "tags"], rows())

    assert data.startswith(b"\xef\xbb\xbf")
    lines = list(csv.reader(io.StringIO(data.decode("utf-8-sig"))))
    assert lines[0] == [
        "列",
        "title",
        "quantity",
        "狀態",
        "執行次數",
        "運行",
        "出參：recordId",
        "出參：tags",
        "錯誤",
    ]
    assert lines[1] == ["1", "文具", "3", "通過", "1", "run-1", "DEMO-1", '["a"]', ""]
    assert lines[2][1:3] == ['\'=HYPERLINK("x")', "-5"]
    assert lines[3][3] == "資料有問題"


def test_export_xlsx_round_trip() -> None:
    data = export_xlsx(["title", "quantity"], ["recordId", "tags"], rows())

    with zipfile.ZipFile(io.BytesIO(data)) as book:
        assert "[Content_Types].xml" in book.namelist()
        sheet = ElementTree.fromstring(book.read("xl/worksheets/sheet1.xml"))
    cells = {cell.get("r"): cell for cell in sheet.iter(f"{{{MAIN}}}c")}
    assert cells["A2"].get("t") is None  # 列號與執行次數是數字
    assert cells["E2"].get("t") is None
    assert cells["B3"].get("t") == "inlineStr"  # 文字儲存格，不是公式
    assert cells["B3"].find(f"{{{MAIN}}}f") is None
    # 自己讀得回來（匯出的結果可以改過再上傳成新的批次）
    again = read_table("results.xlsx", data)
    assert again.columns[:3] == ("列", "title", "quantity")
    assert again.rows[0] == ("1", "文具", "3", "通過", "1", "run-1", "DEMO-1", '["a"]', "")
    assert again.rows[1][1] == '=HYPERLINK("x")'
