"""批次執行（M7.3，ADR 0024）的表格：讀入、逐列換成入參、匯出結果。不碰資料庫。

一張表的第一列是標題，之後每一列是一組入參。讀得懂的格式：

- CSV（逗號分隔）與 TSV（定位字元分隔，從 Excel 複製貼上就是這種）。編碼依序試 UTF-8
  （可以有 BOM）、Big5（cp950，繁中 Windows 的 Excel 另存 CSV 的預設）、GB18030。
- Excel 的 .xlsx：只讀第一個工作表，日期與時間依儲存格格式轉成文字。不用 openpyxl
  （伺服器沒有這個依賴；加了會改變分發包的運行環境），用標準庫讀 zip 裡的 XML。舊的 .xls 不支援。

儲存格一律存成文字；排入執行前才依入參的型別轉換（:func:`row_values`），所以改了欄位對應
之後重新檢查不用重新上傳。匯出（:func:`export_csv`、:func:`export_xlsx`）是同一張表加上
每一列的狀態、運行與出參。
"""

import contextlib
import csv
import io
import json
import re
import zipfile
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Final, cast
from xml.etree import ElementTree
from xml.sax.saxutils import escape

from rpa_core.dsl import Scenario
from rpa_core.dsl.dynamic import has_dynamic
from rpa_runner.contract import prepare_inputs
from rpa_server.i18n import t

__all__ = [
    "MAX_BYTES",
    "MAX_CELL",
    "MAX_COLUMNS",
    "MAX_ROWS",
    "ExportRow",
    "RowProblem",
    "Table",
    "TableError",
    "cells_json",
    "default_mapping",
    "export_csv",
    "export_xlsx",
    "parse_text",
    "read_table",
    "row_values",
]

MAX_BYTES: Final = 5 * 1024 * 1024
"""上傳或貼上的表格最大 5 MB。"""
MAX_ROWS: Final = 1000
"""一個批次最多 1,000 列（不含標題；整列空白的不算）。"""
MAX_COLUMNS: Final = 50
MAX_CELL: Final = 10_000
"""一個儲存格最多 10,000 個字元。"""
_MAX_XML: Final = 50 * 1024 * 1024
"""xlsx 裡單一個 XML 檔解壓後的上限（防壓縮炸彈）。"""

_MAIN: Final = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_REL: Final = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
_PKG_REL: Final = "{http://schemas.openxmlformats.org/package/2006/relationships}"
_DATE_FORMATS: Final = frozenset({*range(14, 23), *range(27, 37), *range(45, 48), *range(50, 59)})
"""Excel 內建的日期與時間格式代號（含中日韓的日期格式）。"""
_TIME_FORMATS: Final = frozenset({18, 19, 20, 21, 32, 33, 34, 35, 45, 46, 47, 55, 56})
"""其中只有時間的。"""
_TRUE: Final = frozenset({"true", "1", "yes", "y", "是", "對"})
_FALSE: Final = frozenset({"false", "0", "no", "n", "否", "錯"})
_THOUSANDS: Final = re.compile(r"^[+-]?\d{1,3}(,\d{3})+(\.\d+)?$")


class TableError(ValueError):
    """表格讀不進來；訊息已是目前語言的文字。"""


@dataclass(frozen=True, slots=True)
class Table:
    """讀進來的表格：標題與每一列（長度和標題相同的文字）。"""

    columns: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]

    def records(self) -> list[dict[str, str]]:
        """每一列：標題 → 儲存格。"""
        return [dict(zip(self.columns, row, strict=True)) for row in self.rows]


@dataclass(frozen=True, slots=True)
class RowProblem:
    """一列的一個問題。``column`` 是表格的欄位（沒有對應到欄位的入參是 None）。"""

    input: str | None
    column: str | None
    message: str

    def to_json(self) -> dict[str, object]:
        return {"input": self.input, "column": self.column, "message": self.message}


@dataclass(frozen=True, slots=True)
class ExportRow:
    """匯出的一列：原本的儲存格加上結果。"""

    number: int
    cells: Mapping[str, str]
    status: str
    run_id: str | None
    output: Mapping[str, object] | None
    error: str | None
    attempts: int = 0


# ---------------------------------------------------------------- 讀入


def read_table(name: str, data: bytes) -> Table:
    """依副檔名讀入表格：.xlsx 讀第一個工作表，其他當成 CSV／TSV 文字。"""
    if len(data) > MAX_BYTES:
        raise TableError(t("batch.table_too_large", max=MAX_BYTES // (1024 * 1024)))
    lower = name.lower()
    if lower.endswith(".xls"):
        raise TableError(t("batch.table_xls"))
    if lower.endswith((".xlsx", ".xlsm")) or data[:4] == b"PK\x03\x04":
        return _shape(_xlsx_rows(data))
    return parse_text(_decode(data))


def parse_text(text: str) -> Table:
    """CSV 或 TSV 文字（例如從 Excel 複製貼上）：第一列有定位字元就是 TSV，否則是 CSV。"""
    if len(text.encode("utf-8")) > MAX_BYTES:
        raise TableError(t("batch.table_too_large", max=MAX_BYTES // (1024 * 1024)))
    text = text.lstrip("﻿")
    first = next((line for line in text.splitlines() if line.strip()), "")
    delimiter = "\t" if "\t" in first else ","
    try:
        rows = list(csv.reader(io.StringIO(text, newline=""), delimiter=delimiter, strict=False))
    except csv.Error as error:
        raise TableError(t("batch.table_unreadable", detail=str(error))) from error
    return _shape(rows)


def _decode(data: bytes) -> str:
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16")
    for encoding in ("utf-8-sig", "cp950", "gb18030"):
        with contextlib.suppress(UnicodeDecodeError):
            return data.decode(encoding)
    raise TableError(t("batch.table_encoding"))  # pragma: no cover - gb18030 幾乎都解得開


def _shape(raw: Sequence[Sequence[str]]) -> Table:
    """去掉整列空白的列與整欄空白、沒有標題的欄，檢查標題與上限。"""
    rows = [list(row) for row in raw if any(cell.strip() for cell in row)]
    if not rows:
        raise TableError(t("batch.table_empty"))
    header = [cell.strip() for cell in rows[0]]
    body = rows[1:]
    width = max(len(header), *(len(row) for row in body)) if body else len(header)
    header += [""] * (width - len(header))
    padded = [row + [""] * (width - len(row)) for row in body]
    keep: list[int] = []
    for index, title in enumerate(header):
        used = any(row[index].strip() for row in padded)
        if title:
            keep.append(index)
        elif used:
            raise TableError(t("batch.table_untitled", column=index + 1))
    columns = tuple(header[index] for index in keep)
    duplicates = sorted({name for name in columns if columns.count(name) > 1})
    if duplicates:
        raise TableError(t("batch.table_duplicate", names="、".join(duplicates)))
    if len(columns) > MAX_COLUMNS:
        raise TableError(t("batch.table_columns", count=len(columns), max=MAX_COLUMNS))
    if not padded:
        raise TableError(t("batch.table_no_rows"))
    if len(padded) > MAX_ROWS:
        raise TableError(t("batch.table_rows", count=len(padded), max=MAX_ROWS))
    shaped: list[tuple[str, ...]] = []
    for number, row in enumerate(padded, start=1):
        cells = tuple(row[index] for index in keep)
        for column, cell in zip(columns, cells, strict=True):
            if len(cell) > MAX_CELL:
                raise TableError(t("batch.table_cell", row=number, column=column, max=MAX_CELL))
        shaped.append(cells)
    return Table(columns, tuple(shaped))


# ---------------------------------------------------------------- xlsx


def _xlsx_rows(data: bytes) -> list[list[str]]:
    try:
        book = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile as error:
        raise TableError(t("batch.table_xlsx", detail=str(error))) from error
    with book:
        try:
            workbook = _xml(book, "xl/workbook.xml")
            if workbook is None:
                raise TableError(t("batch.table_xlsx", detail="xl/workbook.xml"))
            sheet = _first_sheet(book, workbook)
            root = _xml(book, sheet)
            if root is None:
                raise TableError(t("batch.table_xlsx", detail=sheet))
            strings = _shared_strings(book)
            dates = _date_styles(book)
        except (ElementTree.ParseError, KeyError, ValueError) as error:
            if isinstance(error, TableError):
                raise
            raise TableError(t("batch.table_xlsx", detail=str(error))) from error
        pr = workbook.find(f"{_MAIN}workbookPr")
        epoch_1904 = pr is not None and pr.get("date1904") in ("1", "true")
        grid: dict[int, dict[int, str]] = {}
        next_row = 0
        for row in root.iter(f"{_MAIN}row"):
            number = int(row.get("r") or next_row + 1)
            next_row = number
            if number > MAX_ROWS + 1 + 1000:  # 遠超過上限就不用再讀
                break
            next_column = 0
            for cell in row.iter(f"{_MAIN}c"):
                reference = cell.get("r")
                column = _column_index(reference) if reference else next_column + 1
                next_column = column
                value = _cell_text(cell, strings, dates, epoch_1904)
                if value != "":
                    grid.setdefault(number, {})[column] = value
    if not grid:
        return []
    last_row = max(grid)
    last_column = max(max(cells) for cells in grid.values())
    if last_column > MAX_COLUMNS * 4:
        last_column = MAX_COLUMNS * 4  # 標題以外很遠的欄位不讀
    return [
        [grid.get(row, {}).get(column, "") for column in range(1, last_column + 1)]
        for row in range(1, last_row + 1)
    ]


def _xml(book: zipfile.ZipFile, name: str) -> ElementTree.Element | None:
    try:
        info = book.getinfo(name)
    except KeyError:
        return None
    if info.file_size > _MAX_XML:
        raise TableError(t("batch.table_too_large", max=MAX_BYTES // (1024 * 1024)))
    return ElementTree.fromstring(book.read(info))


def _first_sheet(book: zipfile.ZipFile, workbook: ElementTree.Element) -> str:
    sheet = workbook.find(f"{_MAIN}sheets/{_MAIN}sheet")
    rel_id = sheet.get(f"{_REL}id") if sheet is not None else None
    rels = _xml(book, "xl/_rels/workbook.xml.rels")
    if rel_id is not None and rels is not None:
        for rel in rels.iter(f"{_PKG_REL}Relationship"):
            if rel.get("Id") == rel_id:
                target = rel.get("Target") or ""
                if target.startswith("/"):
                    return target.lstrip("/")
                return "xl/" + target if not target.startswith("xl/") else target
    return "xl/worksheets/sheet1.xml"


def _shared_strings(book: zipfile.ZipFile) -> list[str]:
    root = _xml(book, "xl/sharedStrings.xml")
    if root is None:
        return []
    return [_rich_text(item) for item in root.iter(f"{_MAIN}si")]


def _rich_text(element: ElementTree.Element) -> str:
    """<si> 或 <is> 的文字：直接的 <t> 與每一段 <r><t>，不含注音標示（<rPh>）。"""
    parts: list[str] = []
    for child in element:
        if child.tag == f"{_MAIN}t":
            parts.append(child.text or "")
        elif child.tag == f"{_MAIN}r":
            text = child.find(f"{_MAIN}t")
            parts.append(text.text or "" if text is not None else "")
    return "".join(parts)


def _date_styles(book: zipfile.ZipFile) -> dict[int, str]:
    """儲存格樣式的索引 → 日期格式的種類（date、time、datetime）；不是日期的不列。"""
    root = _xml(book, "xl/styles.xml")
    if root is None:
        return {}
    custom: dict[int, str] = {}
    for item in root.iter(f"{_MAIN}numFmt"):
        with contextlib.suppress(TypeError, ValueError):
            custom[int(item.get("numFmtId") or "")] = item.get("formatCode") or ""
    found: dict[int, str] = {}
    xfs = root.find(f"{_MAIN}cellXfs")
    for index, xf in enumerate(xfs.iter(f"{_MAIN}xf") if xfs is not None else ()):
        try:
            number = int(xf.get("numFmtId") or "0")
        except ValueError:
            continue
        kind = _date_kind(number, custom.get(number))
        if kind is not None:
            found[index] = kind
    return found


def _date_kind(number: int, code: str | None) -> str | None:
    """格式代號（與自訂格式）→ date、time、datetime；不是日期時間是 None。"""
    if code is None:
        if number in _TIME_FORMATS:
            return "time"
        if number == 22:
            return "datetime"
        return "date" if number in _DATE_FORMATS else None
    # 去掉引號裡的文字、跳脫的字元與 [$-404] 這類區段；e（科學記號）與 g 不看
    plain = re.sub(r'"[^"]*"|\\.|\[[^\]]*\]', "", code).lower()
    has_date = (
        "y" in plain or "d" in plain or ("m" in plain and "h" not in plain and "s" not in plain)
    )
    has_time = "h" in plain or "s" in plain
    if has_date and has_time:
        return "datetime"
    if has_date:
        return "date"
    return "time" if has_time else None


def _cell_text(
    cell: ElementTree.Element, strings: Sequence[str], dates: Mapping[int, str], epoch_1904: bool
) -> str:
    kind = cell.get("t") or "n"
    value = cell.find(f"{_MAIN}v")
    raw = value.text if value is not None and value.text is not None else ""
    if kind == "s":
        try:
            return strings[int(raw)]
        except (ValueError, IndexError):
            return ""
    if kind == "inlineStr":
        inline = cell.find(f"{_MAIN}is")
        return _rich_text(inline) if inline is not None else ""
    if kind == "b":
        return "true" if raw == "1" else "false" if raw == "0" else raw
    if kind in ("str", "e") or raw == "":
        return raw
    style = int(cell.get("s") or "0") if (cell.get("s") or "0").isdigit() else 0
    date_kind = dates.get(style)
    if date_kind is not None:
        with contextlib.suppress(ValueError, OverflowError):
            return _excel_date(float(raw), date_kind, epoch_1904)
    return _number_text(raw)


def _excel_date(serial: float, kind: str, epoch_1904: bool) -> str:
    """Excel 的日期序號 → 文字。1900 制的序號 60 之前少一天（Excel 把 1900 當閏年）。"""
    base = datetime(1904, 1, 1, tzinfo=UTC) if epoch_1904 else datetime(1899, 12, 30, tzinfo=UTC)
    only_time = serial < 1
    if not epoch_1904 and 1 <= serial < 60:
        serial += 1
    moment = base + timedelta(seconds=round(serial * 86400))
    if kind == "time" and only_time:
        return moment.strftime("%H:%M:%S")
    if kind == "date" or moment.time() == datetime.min.time():
        return moment.strftime("%Y-%m-%d")
    return moment.strftime("%Y-%m-%d %H:%M:%S")


def _number_text(raw: str) -> str:
    """數字：整數不帶小數點（12.0 → 12），其他照原樣。"""
    try:
        number = float(raw)
    except ValueError:
        return raw
    if number.is_integer() and abs(number) < 1e15 and "e" not in raw.lower():
        return str(int(number))
    return raw


def _column_index(reference: str) -> int:
    letters = "".join(char for char in reference if char.isalpha()).upper()
    index = 0
    for char in letters:
        index = index * 26 + ord(char) - ord("A") + 1
    return index


# ---------------------------------------------------------------- 欄位對應與入參


def default_mapping(scenario: Scenario, columns: Sequence[str]) -> dict[str, str | None]:
    """入參 → 欄位：先找標題完全相同的，再找不分大小寫、忽略空白的；找不到是 None。"""
    loose = {_loose(column): column for column in reversed(columns)}
    mapping: dict[str, str | None] = {}
    for name in scenario.inputs:
        if name in columns:
            mapping[name] = name
        else:
            mapping[name] = loose.get(_loose(name))
    return mapping


def _loose(text: str) -> str:
    return re.sub(r"[\s_-]+", "", text).casefold()


def row_values(
    scenario: Scenario, mapping: Mapping[str, str | None], cells: Mapping[str, str]
) -> tuple[dict[str, object], list[RowProblem]]:
    """一列的儲存格 → 入參（只含有值的；空白的用預設值），以及問題。

    文字照原樣；integer、number 可以有千分位（1,200）；boolean 收 true／false、1／0、
    yes／no、是／否；array、object 是 JSON；寫了 ``{{ }}`` 的照原樣交給動態值。
    ``type: file`` 的入參不能從表格給值（留空用預設值）。最後照場景的契約檢查
    （和排入執行前相同的檢查，不展開動態值）。
    """
    values: dict[str, object] = {}
    problems: list[RowProblem] = []
    columns: dict[str, str | None] = {}
    for name, spec in scenario.inputs.items():
        column = mapping.get(name)
        columns[name] = column
        if column is None:
            continue
        raw = cells.get(column, "")
        if raw.strip() == "":
            continue
        if spec.type == "file":
            problems.append(RowProblem(name, column, t("batch.cell_file", column=column)))
            continue
        try:
            values[name] = _convert(spec.type, raw)
        except ValueError:
            problems.append(
                RowProblem(
                    name,
                    column,
                    t(
                        "batch.cell_type",
                        column=column,
                        value=_clip(raw),
                        type=t(f"batch.type_{spec.type}"),
                    ),
                )
            )
    _, checked = prepare_inputs(scenario, values)
    converted = {item.input for item in problems}
    for item in checked:
        if item.name in converted:
            continue  # 轉型就失敗了，契約的「缺少」不用再說一次
        problems.append(RowProblem(item.name, columns.get(item.name), item.message))
    return values, problems


def _convert(kind: str, raw: str) -> object:
    if kind == "string" or has_dynamic(raw):
        return raw
    text = raw.strip()
    if kind in ("integer", "number"):
        if _THOUSANDS.match(text):
            text = text.replace(",", "")
        if kind == "integer":
            if re.fullmatch(r"[+-]?\d+", text):
                return int(text)
            number = float(text)
            if number.is_integer():
                return int(number)
            raise ValueError(raw)
        if re.fullmatch(r"[+-]?\d+", text):
            return int(text)
        number = float(text)
        if number != number or number in (float("inf"), float("-inf")):
            raise ValueError(raw)
        return number
    if kind == "boolean":
        folded = text.casefold()
        if folded in _TRUE:
            return True
        if folded in _FALSE:
            return False
        raise ValueError(raw)
    if kind in ("array", "object"):
        value: object = json.loads(text)
        if kind == "array" and isinstance(value, list):
            return cast("list[object]", value)
        if kind == "object" and isinstance(value, dict):
            return cast("dict[str, object]", value)
        raise ValueError(raw)
    return raw  # pragma: no cover - 型別只有上面這些


def _clip(text: str, limit: int = 40) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "…"


# ---------------------------------------------------------------- 匯出


def _export_header(columns: Sequence[str], outputs: Sequence[str]) -> list[str]:
    return [
        t("batch.export_row"),
        *columns,
        t("batch.export_status"),
        t("batch.export_attempts"),
        t("batch.export_run"),
        *(t("batch.export_output", name=name) for name in outputs),
        t("batch.export_error"),
    ]


def _export_values(row: ExportRow, columns: Sequence[str], outputs: Sequence[str]) -> list[object]:
    output = row.output or {}
    return [
        row.number,
        *(row.cells.get(column, "") for column in columns),
        t(f"status.{row.status}"),
        row.attempts,
        row.run_id or "",
        *(_plain(output.get(name)) for name in outputs),
        row.error or "",
    ]


def _plain(value: object) -> object:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int | float | str):
        return value
    return json.dumps(value, ensure_ascii=False)


def export_csv(columns: Sequence[str], outputs: Sequence[str], rows: Iterable[ExportRow]) -> bytes:
    """結果的 CSV：UTF-8 加 BOM（Excel 直接打開不會亂碼）。

    以 = + - @ 開頭的文字前面加一個 '，避免 Excel 打開時當成公式（出參可能來自網頁）。
    """
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\r\n")
    writer.writerow([_csv_safe(cell) for cell in _export_header(columns, outputs)])
    for row in rows:
        writer.writerow([_csv_safe(cell) for cell in _export_values(row, columns, outputs)])
    return ("﻿" + buffer.getvalue()).encode("utf-8")


def _csv_safe(value: object) -> str:
    text = str(value)
    if isinstance(value, str) and text[:1] in ("=", "+", "-", "@", "\t", "\r"):
        with contextlib.suppress(ValueError):
            float(text)
            return text  # 負數照原樣
        return "'" + text
    return text


def export_xlsx(columns: Sequence[str], outputs: Sequence[str], rows: Iterable[ExportRow]) -> bytes:
    """結果的 .xlsx：一個工作表，文字一律是文字儲存格（不會被當成公式），數字是數字。"""
    lines = [_export_header(columns, outputs)]
    lines += [_export_values(row, columns, outputs) for row in rows]
    sheet = io.StringIO()
    sheet.write(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" '
        'activePane="bottomLeft" state="frozen"/></sheetView></sheetViews><sheetData>'
    )
    for number, values in enumerate(lines, start=1):
        sheet.write(f'<row r="{number}">')
        for index, value in enumerate(values, start=1):
            reference = f"{_column_letters(index)}{number}"
            if isinstance(value, int | float) and not isinstance(value, bool):
                sheet.write(f'<c r="{reference}"><v>{value}</v></c>')
            else:
                text = _xml_text(str(value))
                sheet.write(
                    f'<c r="{reference}" t="inlineStr"><is><t xml:space="preserve">{text}'
                    "</t></is></c>"
                )
        sheet.write("</row>")
    sheet.write("</sheetData></worksheet>")
    files = {
        "[Content_Types].xml": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" '
            'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/'
            'vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/'
            'vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            "</Types>"
        ),
        "_rels/.rels": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/'
            '2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'
        ),
        "xl/workbook.xml": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            f'<sheets><sheet name="{_xml_text(t("batch.export_sheet"))}" sheetId="1" '
            'r:id="rId1"/></sheets></workbook>'
        ),
        "xl/_rels/workbook.xml.rels": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/'
            '2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>'
        ),
        "xl/worksheets/sheet1.xml": sheet.getvalue(),
    }
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as book:
        for name, content in files.items():
            book.writestr(name, content)
    return buffer.getvalue()


def _xml_text(text: str) -> str:
    """XML 不允許的控制字元拿掉，其餘跳脫。"""
    cleaned = "".join(char for char in text if char in "\t\n\r" or ord(char) >= 0x20)
    return escape(cleaned, {'"': "&quot;"})


def _column_letters(index: int) -> str:
    letters = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        letters = chr(ord("A") + remainder) + letters
    return letters


def cells_json(value: object) -> dict[str, str]:
    """資料庫存的儲存格（JSON 物件）→ 欄位 → 文字。"""
    if not isinstance(value, dict):
        return {}
    return {
        str(key): item if isinstance(item, str) else str(item)
        for key, item in cast("dict[object, object]", value).items()
    }
