"""子場景（M7.2，ADR 0023）的版本檔案：檢查時把 call 用到的場景版本帶進 calls/。不需要資料庫。"""

from pathlib import Path

import pytest

from rpa_core.dsl import validate_file
from rpa_core.dsl.sources import scenario_digest
from rpa_server.storage import SCENARIO_FILE, CallGate, Storage

SUB = """\
schemaVersion: 1
id: sub
name: 子場景
inputs:
  name: { type: string }
steps:
  - { id: open, action: goto, url: 'https://example.test/' }
  - { id: read, action: extract, target: { css: h1 }, as: title }
verify:
  - { name: 有標題, value: '{{ facts.title }}', notEmpty: true }
outputs:
  title: { type: string, from: '{{ facts.title }}' }
"""
CALLER = """\
schemaVersion: 1
id: caller
name: 呼叫場景
steps:
  - { id: go, action: call, scenario: sub, revision: 1, inputs: { name: A }, as: got }
"""
PLAIN = """\
schemaVersion: 1
id: caller
name: 呼叫場景
steps:
  - { id: open, action: goto, url: 'https://example.test/' }
"""
SUB_FILE = "calls/sub/1.yaml"


@pytest.fixture
def storage(tmp_path: Path) -> Storage:
    storage = Storage(tmp_path / "data")
    storage.ensure()
    for scene_id in ("sub", "caller", "middle"):
        storage.place_scene(scene_id, "lab")
    storage.save("sub", 1, {SCENARIO_FILE: SUB})
    return storage


def refuse(reason: str) -> CallGate:
    """一律不讓用的檢查：回傳固定的原因。"""

    def gate(scene_id: str, number: int) -> str | None:
        del scene_id, number
        return reason

    return gate


def codes(storage: Storage, files: dict[str, str], **options: object) -> list[str]:
    return [issue.code for issue in storage.check(files, **options).issues]  # type: ignore[arg-type]


def test_check_brings_the_sub_scenario_in(storage: Storage) -> None:
    asked: list[tuple[str, int]] = []

    def gate(scene_id: str, number: int) -> str | None:
        asked.append((scene_id, number))
        return None

    checked = storage.check({SCENARIO_FILE: CALLER}, scene_id="caller", call_gate=gate)

    assert checked.ok, checked.issues
    assert checked.files == {SCENARIO_FILE: CALLER, SUB_FILE: SUB}
    assert asked == [("sub", 1)]
    # 存下來的版本自己就能載入，雜湊和檢查時算的一樣，子場景的內容也算在裡面
    folder = storage.save("caller", 1, checked.files)
    path = folder / SCENARIO_FILE
    scenario = validate_file(path).scenario
    assert scenario is not None
    assert scenario_digest(path, scenario) == checked.digest
    assert storage.digest("caller", 1) == checked.digest
    assert checked.digest != storage.check({SCENARIO_FILE: PLAIN}, scene_id="caller").digest
    assert storage.load("caller", 1)[SUB_FILE] == SUB


def test_gate_refuses_a_new_sub_scenario(storage: Storage) -> None:
    checked = storage.check(
        {SCENARIO_FILE: CALLER}, scene_id="caller", call_gate=refuse("還沒發布")
    )

    assert [issue.code for issue in checked.issues] == ["server.call_unusable"]
    assert checked.issues[0].message == "還沒發布"
    assert checked.scenario is None


def test_gate_is_not_asked_again_for_a_copy_already_in_the_revision(storage: Storage) -> None:
    """上一個版本已經帶進來的子場景：之後子場景封存或下架，呼叫場景照樣能改別的地方再存。"""

    def gate(scene_id: str, number: int) -> str | None:
        raise AssertionError((scene_id, number))

    files = {SCENARIO_FILE: CALLER.replace("name: A", "name: B"), SUB_FILE: SUB}

    checked = storage.check(files, scene_id="caller", call_gate=gate)

    assert checked.ok, checked.issues
    assert checked.files[SUB_FILE] == SUB


def test_sent_copy_never_replaces_the_real_revision(storage: Storage) -> None:
    """送進來的 calls/ 檔案和這台的版本不同：用這台的（版本不可變），而且當成新加的來問。"""
    tampered = SUB.replace("子場景", "被改過")
    asked: list[tuple[str, int]] = []

    def gate(scene_id: str, number: int) -> str | None:
        asked.append((scene_id, number))
        return None

    checked = storage.check(
        {SCENARIO_FILE: CALLER, SUB_FILE: tampered}, scene_id="caller", call_gate=gate
    )

    assert checked.ok, checked.issues
    assert checked.files[SUB_FILE] == SUB
    assert asked == [("sub", 1)]


def test_unused_call_files_are_dropped(storage: Storage) -> None:
    files = {SCENARIO_FILE: PLAIN, SUB_FILE: SUB, "calls/other/3.yaml": SUB}

    checked = storage.check(files, scene_id="caller")

    assert checked.ok, checked.issues
    assert checked.files == {SCENARIO_FILE: PLAIN}


def test_sub_scenario_this_server_does_not_have(storage: Storage) -> None:
    """子場景所在的領域沒有同步到這台：沿用送進來的那一份；也沒有時說明找不到。"""
    caller = CALLER.replace("scenario: sub", "scenario: elsewhere")
    copy = SUB.replace("id: sub", "id: elsewhere")
    file = "calls/elsewhere/1.yaml"

    assert codes(storage, {SCENARIO_FILE: caller}, scene_id="caller") == ["server.call_missing"]
    kept = storage.check(
        {SCENARIO_FILE: caller, file: copy},
        scene_id="caller",
        call_gate=refuse("不該問到"),
    )
    assert kept.ok, kept.issues
    assert kept.files[file] == copy


def test_nested_sub_scenarios_come_along(storage: Storage) -> None:
    """子場景自己呼叫的場景也帶進來，平放在同一個 calls/；這台沒有最裡面那個時，從中間那一層
    的版本目錄拿。"""
    middle = """\
schemaVersion: 1
id: middle
name: 中間
steps:
  - { id: inner, action: call, scenario: sub, revision: 1, inputs: { name: A } }
"""
    checked = storage.check({SCENARIO_FILE: middle}, scene_id="middle")
    assert checked.ok, checked.issues
    storage.save("middle", 1, checked.files)
    caller = CALLER.replace("scenario: sub", "scenario: middle").replace(
        ", inputs: { name: A }, as: got", ""
    )

    both = storage.check({SCENARIO_FILE: caller}, scene_id="caller")

    assert both.ok, both.issues
    assert sorted(both.files) == ["calls/middle/1.yaml", SUB_FILE, SCENARIO_FILE]
    # 「sub」從這台消失之後，仍然從 middle 的版本目錄找得到
    scene_dir = storage.revision_dir("sub", 1).parent.parent
    scene_dir.rename(scene_dir.with_name("gone"))
    storage.forget_scene("sub")
    assert not storage.revision_dir("sub", 1).exists()
    again = storage.check({SCENARIO_FILE: caller}, scene_id="caller")
    assert again.ok, again.issues
    assert again.files[SUB_FILE] == SUB


def test_contract_problems_point_at_the_call(storage: Storage) -> None:
    wrong = CALLER.replace("inputs: { name: A }", "inputs: { nmae: A }")

    checked = storage.check({SCENARIO_FILE: wrong}, scene_id="caller")

    assert sorted(issue.code for issue in checked.issues) == [
        "call.input_missing",
        "call.input_unknown",
    ]
    assert all(issue.position is not None for issue in checked.issues)


def test_unreadable_scenario_is_left_to_validation(storage: Storage) -> None:
    checked = storage.check({SCENARIO_FILE: "steps: [", SUB_FILE: SUB}, scene_id="caller")

    assert not checked.ok
    assert checked.issues[0].code.startswith("yaml.")
