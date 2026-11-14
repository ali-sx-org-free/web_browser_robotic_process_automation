"""場景編輯頁的「插入流程範本」（M7.1，ADR 0021；M7.2 加上 call）。

每一段都是最外層 ``steps`` 底下的一步（兩格縮排的 ``- id: …``），插在游標所在的那一行之前；
定位器用 ``testId: change-me``，提醒使用者改成實際的定位器。內容只有 DSL，不含要翻譯的文字。
"""

from typing import Final

from rpa_server.i18n import t

__all__ = ["FLOW_SNIPPETS", "flow_snippets"]

FLOW_SNIPPETS: Final = {
    "if": """\
  - id: when-shown
    action: if
    condition:
      target: { testId: change-me }
      state: visible
      wait: 2000
    then:
      - id: when-shown-click
        action: click
        target: { testId: change-me }
""",
    "forEach": """\
  - id: each-item
    action: forEach
    items: '{{ inputs.items }}'
    as: item
    steps:
      - id: each-item-fill
        action: fill
        target: { testId: change-me }
        value: '{{ item }}'
""",
    "repeat": """\
  - id: next-pages
    action: repeat
    while: { target: { testId: next-page }, state: enabled }
    max: 20
    steps:
      - id: next-page-click
        action: click
        target: { testId: next-page }
""",
    "try": """\
  - id: optional-part
    action: try
    steps:
      - id: optional-click
        action: click
        target: { testId: change-me }
    catch:
      - id: optional-failed
        action: screenshot
        file: optional-failed
""",
    "openPage": """\
  - id: open-other
    action: openPage
    as: other
    url: /
  - id: read-other
    action: extract
    page: other
    target: { testId: change-me }
    as: otherValue
  - id: close-other
    action: closePage
    page: other
""",
    "call": """\
  - id: call-sub
    action: call
    scenario: change-me
    revision: 1
    inputs: { name: change-me }
    as: result
""",
}
"""範本的鍵 → YAML 內容。"""


def flow_snippets() -> list[dict[str, str]]:
    """編輯頁的選單：鍵、目前語言的名稱與內容。"""
    return [
        {"key": key, "label": t(f"edit.snippet.{key}"), "text": text}
        for key, text in FLOW_SNIPPETS.items()
    ]
