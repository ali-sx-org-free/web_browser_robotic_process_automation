"""在頁面上點選元素，產生 DSL 定位器（登入角色「已登入時看得到的元素」的引導，2026-11-10）。

使用者回報「已登入時看得到的元素」要自己寫 DSL 定位器太難。管理 Portal 的登入角色表單因此有引導：
開瀏覽器視窗到登入網址、使用者自己登入，按「開始點選」後在頁面上點一個只有登入後才看得到的元素。
這裡負責頁面上的部分（子程序的命令與事件在 :func:`rpa_runner.login.pick`）：

- :func:`install` 在頁面放一個點選層：滑過的元素框起來，點一下記下那個元素與往上幾層的資料，
  **這次點擊不會傳給網頁**（不會真的登出或跳頁）。換頁之後點選層不見了，再呼叫一次就好。
- :func:`candidates` 依記下的資料列出幾種寫法，依建議的順序：測試代號（``data-testid``）、
  角色與名稱（按鈕、連結、標題、圖片）、文字、標題（title）、替代文字（alt）、CSS 的 ``#id``。
  只看點到的元素與往上兩層（例如按鈕裡的圖示），再往上的容器在登入前多半也看得到。
- :func:`verify` 每一種寫法實際在頁面上找一次：找不到的不列，頁面上只有一個、而且看得到的排前面。

iframe 裡的元素點不到（點選層只放在最外層的頁面）；需要時仍可以自己寫定位器的 ``frame``。
"""

import contextlib
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final, cast

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page
from pydantic import ValidationError

from rpa_core.dsl import ARIA_ROLES, Locator
from rpa_core.dsl.yaml_writer import flow
from rpa_runner.browser import resolve

__all__ = [
    "DEPTH",
    "MAX_CANDIDATES",
    "Candidate",
    "candidates",
    "install",
    "picked",
    "remove",
    "verify",
]

DEPTH: Final = 3
"""產生寫法時看幾層：點到的元素與往上兩層。"""
MAX_CANDIDATES: Final = 6
_MAX_NAME: Final = 80
"""名稱、標題這類寫法最長幾個字；太長的多半是整段內容，不適合當定位器。"""
_MAX_TEXT: Final = 40
"""文字寫法最長幾個字。"""
_STABLE_ID: Final = re.compile(r"[A-Za-z][\w-]{0,40}")
_GENERATED: Final = re.compile(r"\d{3,}|[0-9a-f]{8,}", re.IGNORECASE)
"""看起來是程式產生、每次載入都不同的 id（連續數字、雜湊）：不拿來當 CSS 寫法。"""
_BUTTON_TYPES: Final = frozenset({"button", "submit", "reset", "image"})
_HEADINGS: Final = frozenset({"h1", "h2", "h3", "h4", "h5", "h6"})

_INSTALL: Final = r"""
() => {
  const current = window.__rpaPick;
  if (current && current.active) return;
  const state = {active: true, result: null};
  window.__rpaPick = state;
  const layer = (css) => {
    const element = document.createElement('div');
    element.setAttribute('data-rpa-pick', '');
    element.style.cssText =
      'position:fixed;z-index:2147483647;pointer-events:none;display:none;' + css;
    document.documentElement.appendChild(element);
    return element;
  };
  const box = layer('border:2px solid #2563eb;background:rgba(37,99,235,.12);border-radius:3px;');
  const tip = layer(
    'background:#1e3a8a;color:#fff;font:12px/1.5 system-ui,sans-serif;padding:2px 6px;' +
    'border-radius:3px;max-width:360px;overflow:hidden;white-space:nowrap;' +
    'text-overflow:ellipsis;');
  const clean = (value, limit) => (value || '').replace(/\s+/g, ' ').trim().slice(0, limit);
  const info = (element) => ({
    tag: element.tagName.toLowerCase(),
    role: element.getAttribute('role'),
    testId: element.getAttribute('data-testid'),
    id: element.id || null,
    text: clean(element.innerText || element.textContent, 200),
    ariaLabel: clean(element.getAttribute('aria-label'), 200) || null,
    title: clean(element.getAttribute('title'), 200) || null,
    alt: clean(element.getAttribute('alt'), 200) || null,
    type: element.getAttribute('type'),
    value: element.tagName === 'INPUT' ? clean(element.value, 200) : null,
    href: element.hasAttribute('href'),
  });
  const show = (element) => {
    const rect = element.getBoundingClientRect();
    Object.assign(box.style, {display: 'block', left: rect.left + 'px', top: rect.top + 'px',
      width: rect.width + 'px', height: rect.height + 'px'});
    const label = element.getAttribute('aria-label') || element.getAttribute('alt');
    const text = clean(element.innerText || label, 40);
    tip.textContent = element.tagName.toLowerCase() + (text ? ' · ' + text : '');
    Object.assign(tip.style, {display: 'block', left: Math.max(0, rect.left) + 'px',
      top: Math.max(0, rect.top - 22) + 'px'});
  };
  const block = (event) => {
    if (!state.active) return;
    event.preventDefault();
    event.stopPropagation();
    event.stopImmediatePropagation();
  };
  const over = (event) => {
    if (state.active && event.target instanceof Element) show(event.target);
  };
  const types = [
    'pointerdown', 'mousedown', 'pointerup', 'mouseup', 'dblclick', 'auxclick', 'contextmenu',
  ];
  const stop = () => {
    state.active = false;
    types.forEach((type) => window.removeEventListener(type, block, true));
    window.removeEventListener('click', click, true);
    window.removeEventListener('mouseover', over, true);
    box.remove();
    tip.remove();
  };
  const click = (event) => {
    if (!state.active) return;
    block(event);
    const chain = [];
    let element = event.target;
    while (element instanceof Element && chain.length < 5) {
      chain.push(info(element));
      element = element.parentElement;
    }
    state.result = chain;
    stop();
  };
  state.stop = stop;
  types.forEach((type) => window.addEventListener(type, block, true));
  window.addEventListener('click', click, true);
  window.addEventListener('mouseover', over, true);
}
"""
_RESULT: Final = "() => (window.__rpaPick && window.__rpaPick.result) || null"
_REMOVE: Final = "() => { const s = window.__rpaPick; if (s && s.active && s.stop) s.stop(); }"


def install(page: Page) -> None:
    """在頁面放點選層（已經在了就不動）；頁面正在換頁時略過，下一輪再放。"""
    with contextlib.suppress(PlaywrightError):
        page.evaluate(_INSTALL)


def remove(page: Page) -> None:
    """拿掉點選層（還沒點選就結束時）。"""
    with contextlib.suppress(PlaywrightError):
        page.evaluate(_REMOVE)


def picked(page: Page) -> list[dict[str, object]] | None:
    """使用者點到的元素與往上幾層的資料；還沒點、或頁面正在換頁時回傳 None。"""
    try:
        result: object = page.evaluate(_RESULT)
    except PlaywrightError:
        return None
    if not isinstance(result, list) or not result:
        return None
    return [
        cast("dict[str, object]", item)
        for item in cast("list[object]", result)
        if isinstance(item, dict)
    ]


def _text(value: object, limit: int) -> str | None:
    if not isinstance(value, str):
        return None
    text = " ".join(value.split())
    return text if 0 < len(text) <= limit else None


def _role(element: Mapping[str, object]) -> str | None:
    """元素的角色：寫明的 role，或常見標籤的隱含角色。"""
    written = element.get("role")
    if isinstance(written, str) and written.strip():
        first = written.split()[0]
        return first if first in ARIA_ROLES else None
    tag = element.get("tag")
    kind = str(element.get("type") or "").lower()
    if tag == "button" or (tag == "input" and kind in _BUTTON_TYPES):
        return "button"
    if tag == "a" and element.get("href") is True:
        return "link"
    if tag in _HEADINGS:
        return "heading"
    if tag == "img" and _text(element.get("alt"), _MAX_NAME):
        return "img"
    return None


def _name(element: Mapping[str, object], role: str) -> str | None:
    """角色的名稱（近似無障礙名稱：aria-label、圖片的 alt、按鈕的 value、文字、title）。"""
    for key in ("ariaLabel", "alt" if role == "img" else "value", "text", "title"):
        if (name := _text(element.get(key), _MAX_NAME)) is not None:
            return name
    return None


def candidates(chain: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    """點到的元素（第一個）與往上幾層的資料 → 幾種 DSL 定位器（camelCase 欄位），依建議的順序。"""
    near = list(chain[:DEPTH])
    found: list[dict[str, object]] = []

    def add(locator: dict[str, object]) -> None:
        if locator not in found:
            found.append(locator)

    for element in near:
        if (test_id := _text(element.get("testId"), _MAX_NAME)) is not None:
            add({"testId": test_id})
            break
    for element in near:
        if (role := _role(element)) is not None and (name := _name(element, role)) is not None:
            add({"role": role, "name": name})
            break
    for element in near:
        if (text := _text(element.get("text"), _MAX_TEXT)) is not None:
            add({"text": text})
            break
    for key, field in (("title", "title"), ("alt", "altText")):
        for element in near:
            if (value := _text(element.get(key), _MAX_NAME)) is not None:
                add({field: value})
                break
    for element in near:
        value = element.get("id")
        if isinstance(value, str) and _STABLE_ID.fullmatch(value) and not _GENERATED.search(value):
            add({"css": f"#{value}"})
            break
    return found


@dataclass(frozen=True, slots=True)
class Candidate:
    """一種寫法，以及在頁面上找到的結果。"""

    locator: Mapping[str, object]
    """DSL 定位器（camelCase 欄位）。"""
    count: int
    """頁面上符合的元素有幾個；執行時用第一個。"""
    visible: bool
    """第一個符合的元素現在看不看得到。"""

    @property
    def text(self) -> str:
        """填進「已登入時看得到的元素」的寫法，例如 ``{ role: button, name: 登出 }``。"""
        return flow(self.locator)

    def to_json(self) -> dict[str, object]:
        return {
            "locator": dict(self.locator),
            "text": self.text,
            "count": self.count,
            "visible": self.visible,
        }


def verify(page: Page, found: Sequence[Mapping[str, object]]) -> list[Candidate]:
    """每一種寫法在頁面上找一次：找不到的不列；只有一個、看得到的排前面，同樣時照建議的順序。"""
    checked: list[tuple[int, Candidate]] = []
    for order, data in enumerate(found):
        try:
            matches = resolve(page, Locator.model_validate(dict(data)))
            count = matches.count()
            visible = count > 0 and matches.first.is_visible()
        except (PlaywrightError, ValidationError, ValueError):
            continue
        if count > 0:
            checked.append((order, Candidate(dict(data), count, visible)))
    checked.sort(key=lambda item: (item[1].count != 1, not item[1].visible, item[0]))
    return [candidate for _, candidate in checked[:MAX_CANDIDATES]]
