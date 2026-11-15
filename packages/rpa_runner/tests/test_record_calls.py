"""接著錄製（rpa_runner.record）用到子場景的場景（M7.2 收尾）：伺服器把版本的 calls/ 包成
JSON 交給 --calls，子程序放回場景檔旁邊再校驗、解析子場景。不開瀏覽器。"""

import argparse
import json
from pathlib import Path

import pytest

from rpa_core.dsl.calls import call_file
from rpa_core.i18n import use_locale
from rpa_runner.record import load_replay

CALL = Path(__file__).resolve().parents[3] / "scenarios" / "examples" / "call"
SUB = (CALL / call_file("call-create-record", 1)).read_text(encoding="utf-8")
CALLER = (CALL / "create-and-check.yaml").read_text(encoding="utf-8")


def args(folder: Path, calls: Path | None) -> argparse.Namespace:
    (folder / "input.json").write_text("{}", encoding="utf-8")
    return argparse.Namespace(
        scenario=str(folder / "base.yaml"),
        input=str(folder / "input.json"),
        calls=str(calls) if calls else None,
    )


def test_replay_puts_the_sub_scenarios_back_next_to_the_scenario(tmp_path: Path) -> None:
    (tmp_path / "base.yaml").write_text(CALLER, encoding="utf-8")
    bundle = tmp_path / "calls.json"
    bundle.write_text(
        json.dumps({call_file("call-create-record", 1): SUB, "../escape.yaml": "x"}),
        encoding="utf-8",
    )

    scenario, inputs, calls = load_replay(args(tmp_path, bundle))

    assert scenario.id == "call-create-and-check"
    assert inputs == {"title": "子場景範例"}
    assert list(calls) == [("call-create-record", 1)]
    assert (tmp_path / call_file("call-create-record", 1)).read_text(encoding="utf-8") == SUB
    assert not (tmp_path.parent / "escape.yaml").exists()


def test_replay_without_the_sub_scenarios_is_refused(tmp_path: Path) -> None:
    """沒有子場景檔：校驗不過（舊的伺服器、或伺服器沒帶 --calls 時）。"""
    (tmp_path / "base.yaml").write_text(CALLER, encoding="utf-8")
    with use_locale("zh-Hant"), pytest.raises(ValueError, match="場景校驗失敗"):
        load_replay(args(tmp_path, None))
