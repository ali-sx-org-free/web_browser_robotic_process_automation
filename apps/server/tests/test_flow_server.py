"""流程控制（M7.1，ADR 0021）在伺服器端：編輯頁的流程範本、逐步調試的步驟樹與路徑、
回看依路徑對應場景快照。不開瀏覽器；真實的執行在 rpa_runner 的 test_flow_browser.py。"""

import json
from pathlib import Path
from typing import cast

import pytest

from rpa_core.dsl import Scenario, validate_text
from rpa_runner.files import SCENARIO_DIR
from rpa_server import debugging, replay
from rpa_server.debugging import DebugManager, DebugSession, StepState
from rpa_server.errors import ServiceError
from rpa_server.replay import step_targets
from rpa_server.snippets import FLOW_SNIPPETS, flow_snippets

HEAD = """\
schemaVersion: 1
id: flow-demo
name: 流程
inputs:
  items: { type: array }
browser: { baseUrl: 'http://127.0.0.1:8765' }
steps:
"""
FLOW = (
    HEAD
    + """\
  - { id: open, action: goto, url: /flow }
  - id: each
    action: forEach
    items: '{{ inputs.items }}'
    as: item
    steps:
      - id: fill
        action: fill
        target: { label: 標題 }
        value: '{{ item }}'
      - id: check
        action: if
        condition: { title: 流程 }
        then:
          - { id: shot, action: screenshot }
  - id: guard
    action: try
    steps:
      - { id: read, action: extract, target: { testId: x }, as: x }
    catch:
      - { id: back, action: goto, url: / }
"""
)


def scenario(text: str = FLOW) -> Scenario:
    checked = validate_text(text).scenario
    assert checked is not None
    return checked


# ---------------------------------------------------------------- 流程範本


@pytest.mark.parametrize("key", sorted(FLOW_SNIPPETS))
def test_each_flow_snippet_is_a_valid_step(key: str) -> None:
    assert validate_text(HEAD + FLOW_SNIPPETS[key]).issues == ()


def test_flow_snippets_can_all_be_inserted_together() -> None:
    assert validate_text(HEAD + "".join(FLOW_SNIPPETS.values())).issues == ()
    assert [snippet["key"] for snippet in flow_snippets()] == list(FLOW_SNIPPETS)


# ---------------------------------------------------------------- 逐步調試的步驟樹


def test_debug_steps_form_a_tree_with_paths() -> None:
    states = debugging._steps(scenario())  # pyright: ignore[reportPrivateUsage]

    assert [state.id for state in states] == ["open", "each", "guard"]
    each = states[1]
    assert each.loop is True
    assert each.path_key == "steps/1"
    assert [(child.id, child.key, child.depth) for child in each.children] == [
        ("fill", "steps", 1),
        ("check", "steps", 1),
    ]
    shot = each.children[1].children[0]
    assert shot.path == ("steps", 1, "steps", 1, "then", 0)
    assert shot.index == 1
    # 區塊裡有填寫（有副作用），整塊就算有副作用
    assert each.side_effect is True
    assert states[2].side_effect is False
    found = debugging._find(states, ("steps", 2, "catch", 0))  # pyright: ignore[reportPrivateUsage]
    assert found is not None
    assert found.id == "back"
    data = each.to_json()
    assert data["path"] == ["steps", 1]
    assert len(cast("list[object]", data["children"])) == 2


def session_with(steps: list[StepState], tmp_path: Path) -> DebugSession:
    return DebugSession(
        id="s1",
        scene_id="flow-demo",
        revision=1,
        engine="chromium",
        headless=True,
        base_url=None,
        inputs={"items": ["a", "b"]},
        folder=tmp_path,
        scenario=scenario(),
        steps=steps,
        status="ready",
    )


class Replies:
    """代替子程序：記下送出的命令，回覆事先準備好的內容。"""

    def __init__(self, reply: dict[str, object]) -> None:
        self.reply = reply
        self.commands: list[dict[str, object]] = []

    def __call__(
        self, session: DebugSession, timeout: float, **command: object
    ) -> dict[str, object]:
        self.commands.append(command)
        return self.reply


def manager_for(
    session: DebugSession, replies: Replies, monkeypatch: pytest.MonkeyPatch
) -> DebugManager:
    manager = object.__new__(DebugManager)
    monkeypatch.setattr(manager, "get", lambda session_id: session, raising=False)
    monkeypatch.setattr(manager, "_command", replies, raising=False)
    return manager


def record(path: list[object], status: str = "passed", **extra: object) -> dict[str, object]:
    return {"path": path, "status": status, "durationMs": 5, "files": [], "notes": [], **extra}


def test_running_a_block_updates_every_step_inside(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    session = session_with(debugging._steps(scenario()), tmp_path)  # pyright: ignore[reportPrivateUsage]
    block = record(["steps", 1], iterations=2)
    replies = Replies(
        {
            "ok": True,
            "record": block,
            "records": [
                block,
                record(["steps", 1, "steps", 0], iteration=1),
                record(["steps", 1, "steps", 1], iteration=1, branch="then"),
                record(["steps", 1, "steps", 1, "then", 0]),
                record(["steps", 1, "steps", 0], iteration=2),
                record(["steps", 1, "steps", 1], "failed", iteration=2, handled="continued"),
            ],
        }
    )
    manager = manager_for(session, replies, monkeypatch)

    manager.run_step("s1", 1)

    assert replies.commands == [{"cmd": "step", "index": 1}]
    each = session.steps[1]
    assert (each.status, each.runs, each.iterations) == ("passed", 1, 2)
    fill, check = each.children
    assert (fill.status, fill.runs) == ("passed", 2)
    assert (check.status, check.runs, check.handled) == ("failed", 2, "continued")
    assert check.children[0].runs == 1
    assert session.next_index == 2


def test_running_one_step_inside_a_loop_sends_its_path_and_choices(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    session = session_with(debugging._steps(scenario()), tmp_path)  # pyright: ignore[reportPrivateUsage]
    replies = Replies({"ok": True, "record": record(["steps", 1, "steps", 0])})
    manager = manager_for(session, replies, monkeypatch)

    manager.run_step("s1", 1, path=["steps", 1, "steps", 0], choices={"steps/1": 1})

    assert replies.commands == [
        {"cmd": "step", "path": ["steps", 1, "steps", 0], "choices": {"steps/1": 1}}
    ]
    assert session.steps[1].children[0].runs == 1
    assert session.steps[1].runs == 0
    # 單獨執行區塊裡的一步，不改「下一步」
    assert session.next_index == 0
    assert json.loads(json.dumps(session.to_json()))["choices"] == {"steps/1": 1}
    # 有副作用、執行過的步驟要確認才再執行
    with pytest.raises(ServiceError):
        manager.run_step("s1", 1, path=["steps", 1, "steps", 0])
    # 路徑要在第 index 步裡面
    with pytest.raises(ServiceError):
        manager.run_step("s1", 2, path=["steps", 1, "steps", 0])


# ---------------------------------------------------------------- 回看依路徑對應


def test_replay_maps_records_to_nested_definitions(tmp_path: Path) -> None:
    folder = tmp_path / "run"
    (folder / SCENARIO_DIR).mkdir(parents=True)
    (folder / SCENARIO_DIR / "scenario.yaml").write_text(FLOW, encoding="utf-8")

    snapshot = folder / SCENARIO_DIR / "scenario.yaml"
    definitions, sources = replay._definitions(snapshot)  # pyright: ignore[reportPrivateUsage]

    fill = definitions[("steps", 1, "steps", 0)]
    assert fill["value"] == "{{ item }}"
    assert "steps" not in definitions[("steps", 1)]  # 區塊的定義不含裡面的步驟
    line, text = sources[("steps", 1, "steps", 1, "then", 0)]
    assert text.strip() == "- { id: shot, action: screenshot }"
    assert FLOW.splitlines()[line - 1].strip() == "- { id: shot, action: screenshot }"
    block_line, block_text = sources[("steps", 1)]
    assert block_text.splitlines()[0].strip() == "- id: each"
    assert "- { id: shot, action: screenshot }" in block_text
    assert "id: guard" not in block_text
    assert block_line < line

    records: list[dict[str, object]] = [
        {"path": ["steps", 0]},
        {"path": ["steps", 1]},
        {"path": ["steps", 1, "steps", 0]},
        {"id": "old-record-without-path"},
    ]
    assert replay._record_path(records[3], 3) == ("steps", 3)  # pyright: ignore[reportPrivateUsage]
    assert step_targets(folder, records) == ["/flow", None, "{ label: 標題 }", None]
