"""改寫場景檔的一部分，其他內容（包含註解）原樣保留。

管理 Portal 的入參、出參表單存檔時用 :func:`replace_contract`：只替換最上層的
``inputs:``、``outputs:`` 兩段，其他行一個字都不動。入參改名時，場景裡引用舊名稱的
``{{ inputs.舊名稱 }}`` 一併改成新名稱。

改寫後的內容還是要經過完整校驗（存成新版本時）；這裡不負責判斷內容對不對。

**JSON 寫法的場景檔**（2026-11-10）：JSON 也是合法的 YAML，整份寫成一個 JSON 物件的場景檔
（例如 AI 或其他工具產生、壓成一行的）照樣能執行，但沒有一行一個的最上層鍵，不能用行來切段落。
這種檔案改以資料處理：段落的原文是只有那一個鍵的 JSON 物件（``{"steps": [...]}``，縮排兩格），
存檔時把那個鍵的值換掉，整份照原本的寫法（壓成一行或原本的縮排）寫回 JSON，鍵的順序不變。
段落原文寫成 YAML 也可以，會讀成資料再放進去。YAML 寫法的場景檔收到 JSON 寫法的段落時，
轉成區塊寫法再換掉那一段。讀不懂的段落拋出 :class:`SectionError`，位置是段落裡的行號。
"""

import json
import re
from collections.abc import Mapping, Sequence
from typing import Final, cast

from rpa_core.dsl.yaml_loader import Position, YamlLoadError, load_yaml
from rpa_core.dsl.yaml_writer import block

__all__ = [
    "INPUT_KEYS",
    "OUTPUT_KEYS",
    "SECTION_KEYS",
    "SectionError",
    "append_items",
    "contract_section",
    "find_block",
    "json_document",
    "rename_input",
    "replace_contract",
    "replace_section",
    "section_line",
    "section_text",
    "section_value",
]

SECTION_KEYS: Final = ("inputs", "outputs", "steps", "verify")
"""可以單獨編輯的段落：入參、出參、自動化步驟、獨立斷言。"""

INPUT_KEYS: Final = (
    "type",
    "description",
    "default",
    "enum",
    "minLength",
    "maxLength",
    "pattern",
    "minimum",
    "maximum",
    "accept",
    "maxSize",
    "multiple",
)
"""寫出入參時欄位的順序（accept、maxSize、multiple 是檔案入參的，M7c）。"""
OUTPUT_KEYS: Final = (
    "type",
    "description",
    "from",
    "enum",
    "minLength",
    "maxLength",
    "pattern",
    "minimum",
    "maximum",
)
"""寫出出參時欄位的順序。"""

_TOP_LEVEL: Final = re.compile(r"^(?P<key>[A-Za-z_][\w-]*)\s*:")
_INSERT_BEFORE: Final = (
    "secrets",
    "browser",
    "login",
    "defaults",
    "deadline",
    "steps",
    "verify",
    "script",
)
"""新增 inputs 或 outputs 段落時，放在這些段落之前（依場景檔慣用的順序）。"""
_FLOW_KEYS: Final = frozenset({"target", "within", "frame"})
"""JSON 寫法的段落轉成 YAML 區塊寫法時，寫成一行流式寫法的鍵（定位器）。"""


class SectionError(ValueError):
    """段落的原文讀不懂，或不是「只有 ``key`` 這一個最上層的鍵」。

    ``error`` 是讀不懂時的 YAML 錯誤（位置是段落裡的行號、列號）；鍵不對時是 None。
    """

    def __init__(self, key: str, error: YamlLoadError | None = None) -> None:
        super().__init__(key, error)
        self.key = key
        self.error = error

    @property
    def position(self) -> Position | None:
        return self.error.position if self.error is not None else None


def _no_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for name, value in pairs:
        if name in result:
            raise ValueError(name)
        result[name] = value
    return result


def _no_constant(name: str) -> object:
    raise ValueError(name)


def json_document(text: str) -> dict[str, object] | None:
    """整份場景檔是一個 JSON 物件時回傳它（保留鍵的順序）；不是時回傳 None。

    有重複的鍵、NaN 這類 JSON 不允許的寫法時也回傳 None（照 YAML 處理，交給校驗說明問題）。
    """
    body = text.lstrip("\ufeff \t\r\n")
    if not body.startswith("{"):
        return None
    try:
        data = json.loads(body, object_pairs_hook=_no_duplicates, parse_constant=_no_constant)
    except ValueError:
        return None
    return cast("dict[str, object]", data) if isinstance(data, dict) else None


def _json_section(key: str, value: object) -> str:
    return json.dumps({key: value}, ensure_ascii=False, indent=2)


def _json_text(original: str, document: Mapping[str, object]) -> str:
    """把改過的資料照原本的寫法寫回：壓成一行的還是一行，有縮排的用原本的縮排。

    開頭的 BOM、空白與最後的換行保留；原本用 CRLF 換行時照用。
    """
    start = len(original) - len(original.lstrip("\ufeff \t\r\n"))
    body = original[start:].rstrip()
    newline = "\r\n" if "\r\n" in original else "\n"
    if "\n" in body:
        found = re.search(r"\n([ \t]+)\S", body)
        indent = found.group(1) if found else "  "
        text = json.dumps(document, ensure_ascii=False, indent=indent)
    else:
        item = ", " if re.search(r",\s+[\"\[{\dtfn-]", body) else ","
        name = ": " if re.search(r"\"\s*:\s+", body) else ":"
        text = json.dumps(document, ensure_ascii=False, separators=(item, name))
    ending = newline if original.endswith(("\n", "\r\n")) else ""
    return original[:start] + text.replace("\n", newline) + ending


def _json_put(document: Mapping[str, object], key: str, value: object) -> dict[str, object]:
    """換掉（或新增）一個最上層的鍵；新增時的位置和 YAML 寫法相同（_AFTER、_INSERT_BEFORE）。"""
    if key in document:
        return {name: value if name == key else item for name, item in document.items()}
    names = list(document)
    position: int | None = None
    if (after := _AFTER.get(key)) is not None and after in document:
        position = names.index(after) + 1
    if position is None:
        position = next(
            (names.index(name) for name in _INSERT_BEFORE if name in document), len(names)
        )
    items = list(document.items())
    items.insert(position, (key, value))
    return dict(items)


def section_value(key: str, section: str) -> object:
    """段落的原文（YAML 或 JSON 寫法）讀成資料，回傳 ``key`` 的值。

    原文要剛好只有 ``key`` 一個最上層的鍵；讀不懂或鍵不對時拋出 :class:`SectionError`。
    """
    try:
        data, _ = load_yaml(section)
    except YamlLoadError as error:
        raise SectionError(key, error) from error
    if not isinstance(data, dict) or list(cast("dict[str, object]", data)) != [key]:
        raise SectionError(key)
    return cast("dict[str, object]", data)[key]


def _is_json_section(section: str) -> bool:
    return section.lstrip().startswith("{")


def _is_top_level(line: str) -> bool:
    """最上層的鍵（從第一欄開始、不是註解）。

    從第一欄開始的 ``- `` 是上一個鍵的清單項目（YAML 允許清單和鍵對齊），不算新的鍵。
    """
    if not line or line[0].isspace() or line.startswith("#"):
        return False
    return not (line.startswith("-") and (len(line) == 1 or line[1] == " "))


def find_block(lines: Sequence[str], key: str) -> tuple[int, int] | None:
    """最上層 ``key:`` 段落的 (起始行, 結束行之後) 索引；找不到時回傳 None。

    段落包含後面縮排的行與夾在中間的空行；段落最後的空行、以及緊接著下一個鍵的第一欄註解
    （通常是在說明下一段）不算在內。
    """
    start = next(
        (
            index
            for index, line in enumerate(lines)
            if (match := _TOP_LEVEL.match(line)) and match.group("key") == key
        ),
        None,
    )
    if start is None:
        return None
    end = start + 1
    while end < len(lines) and not _is_top_level(lines[end]) and lines[end].strip() != "---":
        end += 1
    while end > start + 1 and (not lines[end - 1].strip() or lines[end - 1].startswith("#")):
        end -= 1
    return start, end


def _ordered(spec: Mapping[str, object], keys: tuple[str, ...]) -> dict[str, object]:
    """依固定順序排列欄位；值為 None 的欄位不寫。"""
    ordered = {name: spec[name] for name in keys if spec.get(name) is not None}
    ordered |= {
        name: value for name, value in spec.items() if name not in keys and value is not None
    }
    return ordered


def _section(
    name: str, specs: Mapping[str, Mapping[str, object]], keys: tuple[str, ...]
) -> list[str]:
    return block({name: {item: _ordered(spec, keys) for item, spec in specs.items()}})


def _contract_specs(
    specs: Mapping[str, Mapping[str, object]], keys: tuple[str, ...]
) -> dict[str, object]:
    return {item: _ordered(spec, keys) for item, spec in specs.items()}


def contract_section(
    key: str, specs: Mapping[str, Mapping[str, object]], *, as_json: bool = False
) -> str:
    """入參或出參段落的原文（表格切換成原文時用）；沒有任何項目時是空字串。

    ``as_json`` 給 JSON 寫法的場景檔：``{"inputs": {...}}``。
    """
    if not specs:
        return ""
    keys = INPUT_KEYS if key == "inputs" else OUTPUT_KEYS
    if as_json:
        return _json_section(key, _contract_specs(specs, keys))
    return "\n".join(_section(key, specs, keys))


def rename_input(text: str, old: str, new: str) -> str:
    """把 ``inputs.舊名稱``、``inputs["舊名稱"]`` 的引用改成新名稱。"""
    pattern = re.compile(
        rf"(?<![\w.])inputs(?:\.{re.escape(old)}(?!\w)|\[\s*(['\"]){re.escape(old)}\1\s*\])"
    )

    def replace(match: re.Match[str]) -> str:
        quote = match.group(1)
        return f"inputs[{quote}{new}{quote}]" if quote else f"inputs.{new}"

    return pattern.sub(replace, text)


def _rename_values(value: object, old: str, new: str) -> object:
    """JSON 寫法的場景檔：資料裡所有字串值的引用改名（鍵不改；字串裡的引號已經還原）。"""
    if isinstance(value, str):
        return rename_input(value, old, new)
    if isinstance(value, list):
        return [_rename_values(item, old, new) for item in cast("list[object]", value)]
    if isinstance(value, dict):
        return {
            name: _rename_values(item, old, new)
            for name, item in cast("dict[str, object]", value).items()
        }
    return value


def _replace(lines: list[str], key: str, new: list[str], after: str | None = None) -> list[str]:
    found = find_block(lines, key)
    if found is not None:
        start, end = found
        if new:
            return lines[:start] + new + lines[end:]
        rest = lines[end:]
        # 移除整段後不要留下兩個連續的空行
        if start > 0 and not lines[start - 1].strip() and rest and not rest[0].strip():
            rest = rest[1:]
        return lines[:start] + rest
    if not new:
        return lines
    position: int | None = None
    if after is not None and (previous := find_block(lines, after)) is not None:
        position = previous[1]
    if position is None:
        for name in _INSERT_BEFORE:
            if (other := find_block(lines, name)) is not None:
                position = other[0]
                break
    if position is None:
        position = len(lines)
        while position > 0 and not lines[position - 1].strip():
            position -= 1
    # 前後各留一個空行，和其他段落分開
    before = [""] if position > 0 and lines[position - 1].strip() else []
    tail = [""] if position < len(lines) and lines[position].strip() else []
    return lines[:position] + before + new + tail + lines[position:]


def _text(lines: Sequence[str], newline: str, ending: bool) -> str:
    result = newline.join(lines)
    return result + newline if ending or not result else result


def section_text(text: str, key: str) -> str:
    """最上層 ``key:`` 段落的原文（含 ``key:`` 那一行，不含最後的換行）；沒有這段時回傳空字串。

    JSON 寫法的場景檔回傳只有這個鍵的 JSON 物件（縮排兩格）。
    """
    document = json_document(text)
    if document is not None:
        return _json_section(key, document[key]) if key in document else ""
    lines = text.splitlines()
    found = find_block(lines, key)
    if found is None:
        return ""
    start, end = found
    return "\n".join(lines[start:end])


def section_line(text: str, key: str, path: Sequence[str | int], line: int | None) -> int | None:
    """場景檔的校驗問題落在 ``key`` 這一段時，它在段落原文（:func:`section_text`）裡的行號。

    YAML 寫法用檔案的行號換算（段落第一行是 ``key:``）；JSON 寫法的檔案可能只有一行，改用問題的
    資料路徑在段落原文裡找位置。不在這一段時回傳 None。
    """
    document = json_document(text)
    if document is None:
        found = find_block(text.splitlines(), key)
        if found is None or line is None:
            return None
        start, end = found
        return line - start if start < line <= end else None
    if not path or path[0] != key or key not in document:
        return None
    try:
        _, source = load_yaml(_json_section(key, document[key]))
    except YamlLoadError:  # pragma: no cover - json.dumps 的輸出一定讀得回來
        return None
    position = source.locate(tuple(path))
    return position.line if position is not None else None


_AFTER: Final = {"outputs": "inputs", "verify": "steps"}
"""新增段落時要接在哪一段後面（找不到時依 _INSERT_BEFORE 的順序）。"""


def replace_section(text: str, key: str, section: str) -> str:
    """把最上層 ``key:`` 段落換成 ``section``（它自己的原文，含 ``key:`` 那一行）。

    ``section`` 是空白時移除整段。其他行一個字都不動；內容對不對由之後的完整校驗判斷。
    JSON 寫法的場景檔（或 JSON 寫法的段落）要先讀成資料，讀不懂時拋出 :class:`SectionError`。
    """
    document = json_document(text)
    if document is not None:
        if not section.strip():
            document.pop(key, None)
        else:
            document = _json_put(document, key, section_value(key, section))
        return _json_text(text, document)
    if section.strip() and _is_json_section(section):
        value = section_value(key, section)
        section = "\n".join(block({key: value}, flow_keys=_FLOW_KEYS))
    newline = "\r\n" if "\r\n" in text else "\n"
    ending = text.endswith(("\n", "\r\n"))
    new = section.strip("\n").splitlines() if section.strip() else []
    lines = _replace(text.splitlines(), key, new, after=_AFTER.get(key))
    return _text(lines, newline, ending)


def _item_indent(lines: Sequence[str]) -> int | None:
    """段落裡第一個項目的縮排（略過空行與註解）。"""
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return len(line) - len(line.lstrip(" "))
    return None


def _shift(line: str, columns: int) -> str:
    """整行往右（正數）或往左（負數，最多移掉行首的空白）平移。"""
    if not line.strip():
        return line
    if columns >= 0:
        return " " * columns + line
    leading = len(line) - len(line.lstrip(" "))
    return line[min(-columns, leading) :]


def append_items(text: str, key: str, items: Sequence[str], *, whole: Sequence[str]) -> str:
    """在最上層 ``key:`` 段落的最後加上項目（例如步驟、入參），原有內容一個字都不動。

    ``items`` 是以兩格縮排寫好的項目原文（``block()`` 的輸出去掉第一行）；原段落用別的縮排時
    整體平移成一樣的縮排。段落寫成一行（例如 ``secrets: [A, B]``）或還沒有這段時，改用
    ``whole``（合併後整段的原文）取代。
    """
    if not items:
        return text
    document = json_document(text)
    if document is not None:
        return _json_text(text, _json_append(document, key, items, whole))
    newline = "\r\n" if "\r\n" in text else "\n"
    ending = text.endswith(("\n", "\r\n"))
    lines = text.splitlines()
    found = find_block(lines, key)
    inline = found is not None and lines[found[0]].split(":", 1)[1].split("#", 1)[0].strip()
    if found is None or inline:
        return _text(_replace(lines, key, list(whole), after=_AFTER.get(key)), newline, ending)
    start, end = found
    indent = _item_indent(lines[start + 1 : end])
    shift = (indent if indent is not None else 2) - 2
    moved = [_shift(item, shift) for item in items]
    return _text([*lines[:end], *moved, *lines[end:]], newline, ending)


def _json_append(
    document: Mapping[str, object], key: str, items: Sequence[str], whole: Sequence[str]
) -> dict[str, object]:
    """JSON 寫法的場景檔：``items``（YAML 項目原文）讀成資料接在原本的清單或物件後面。

    原本沒有這段、或型別對不上時改用 ``whole``（合併後整段的原文）。項目只有註解時不動。
    """
    added = section_value(key, "\n".join([f"{key}:", *items]))
    if added is None:
        return dict(document)
    current = document.get(key)
    if isinstance(current, list) and isinstance(added, list):
        value: object = [*cast("list[object]", current), *cast("list[object]", added)]
    elif isinstance(current, dict) and isinstance(added, dict):
        value = {**cast("dict[str, object]", current), **cast("dict[str, object]", added)}
    else:
        value = section_value(key, "\n".join(whole))
    return _json_put(document, key, value)


def replace_contract(
    text: str,
    *,
    inputs: Mapping[str, Mapping[str, object]] | None,
    outputs: Mapping[str, Mapping[str, object]] | None,
    renames: Mapping[str, str] | None = None,
) -> str:
    """替換場景檔的 inputs 與 outputs 段落；沒有任何項目時移除該段落，None 時不動那一段。

    ``inputs``、``outputs`` 是「名稱 → DSL 寫法的欄位」（camelCase，例如 minLength、from）。
    ``renames`` 是入參的「舊名稱 → 新名稱」，場景其他地方的引用一併改名。
    """
    document = json_document(text)
    if document is not None:
        data: object = document
        for old, new in (renames or {}).items():
            if old != new:
                data = _rename_values(data, old, new)
        result = cast("dict[str, object]", data)
        for key, specs, keys in (("inputs", inputs, INPUT_KEYS), ("outputs", outputs, OUTPUT_KEYS)):
            if specs is None:
                continue
            if specs:
                result = _json_put(result, key, _contract_specs(specs, keys))
            else:
                result.pop(key, None)
        return _json_text(text, result)
    newline = "\r\n" if "\r\n" in text else "\n"
    ending = text.endswith(("\n", "\r\n"))
    for old, new in (renames or {}).items():
        if old != new:
            text = rename_input(text, old, new)
    lines = text.splitlines()
    if inputs is not None:
        lines = _replace(lines, "inputs", _section("inputs", inputs, INPUT_KEYS) if inputs else [])
    if outputs is not None:
        lines = _replace(
            lines,
            "outputs",
            _section("outputs", outputs, OUTPUT_KEYS) if outputs else [],
            after="inputs",
        )
    return _text(lines, newline, ending)
