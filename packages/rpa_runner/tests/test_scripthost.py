"""相容模式 Python 腳本的啟動器（scripthost，2026-11-28）：腳本照原樣執行、步驟紀錄、沒有開瀏覽器。

不需要瀏覽器；真的錄影在 test_video_browser.py。
"""

import json
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

from rpa_core.i18n import use_locale
from rpa_runner.files import STEPS, VIDEO, VIDEO_INFO, VIDEO_TMP
from rpa_runner.run import execute
from rpa_runner.scripthost import MODULE, VIDEO_FLAG, Recorder
from rpa_runner.video import NO_BROWSER

PASS = """\
import argparse
from pathlib import Path
parser = argparse.ArgumentParser()
for name in ('input', 'facts', 'output'):
    parser.add_argument(f'--{name}', required=True)
Path(parser.parse_args().output).write_text('{}', encoding='utf-8')
"""

STEPPED = """\
import argparse, json
from pathlib import Path
import rpa_script

parser = argparse.ArgumentParser()
for name in ('input', 'facts', 'screenshot', 'target-url'):
    parser.add_argument(f'--{name}', required=True)
args = parser.parse_args()
run = rpa_script.current()
with run.step('prepare', '準備資料'):
    print('準備好了')
Path(args.facts).write_text(json.dumps({'ok': True}), encoding='utf-8')
"""

ECHO = """\
import json, sys
print(json.dumps({'argv': sys.argv, 'path0': sys.path[0], 'name': __name__, 'file': __file__}))
"""


@pytest.fixture(autouse=True)
def _zh_hant() -> Iterator[None]:
    with use_locale("zh-Hant"):
        yield


def _compat(folder: Path, automation: str) -> Path:
    """相容模式（沒寫 runtime）的腳本場景。"""
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "automation.py").write_text(automation, encoding="utf-8")
    (folder / "assertion.py").write_text(PASS, encoding="utf-8")
    path = folder / "scenario.yaml"
    path.write_text(
        "schemaVersion: 1\nid: compat\nname: 相容模式\n"
        "script:\n  automation: automation.py\n  assertion: assertion.py\n",
        encoding="utf-8",
    )
    return path


def _run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command, cwd=cwd, capture_output=True, text=True, encoding="utf-8", check=False
    )


@pytest.mark.parametrize("video", [False, True], ids=["plain", "video"])
def test_launcher_runs_the_script_as_python_would(tmp_path: Path, video: bool) -> None:
    script = tmp_path / "scene" / "automation.py"
    script.parent.mkdir()
    script.write_text(ECHO, encoding="utf-8")
    flags = [VIDEO_FLAG, str(tmp_path / "run")] if video else []

    direct = _run([sys.executable, str(script), "--input", "a b", "-x"], tmp_path)
    hosted = _run(
        [sys.executable, "-m", MODULE, *flags, str(script), "--input", "a b", "-x"], tmp_path
    )

    assert direct.returncode == hosted.returncode == 0, hosted.stderr
    assert json.loads(hosted.stdout) == json.loads(direct.stdout)
    assert json.loads(hosted.stdout)["path0"] == str(script.parent)
    # 沒有開瀏覽器就不會有錄影的暫存資料夾
    assert not (tmp_path / "run" / VIDEO_TMP).exists()


@pytest.mark.parametrize(
    ("body", "code", "text"),
    [
        ("import sys\nsys.exit(3)\n", 3, ""),
        ("raise ValueError('壞掉了')\n", 1, "ValueError: 壞掉了"),
        ("import sys\nsys.exit('停下')\n", 1, "停下"),
    ],
    ids=["exit-code", "exception", "exit-message"],
)
def test_exit_codes_and_errors_pass_through(
    tmp_path: Path, body: str, code: int, text: str
) -> None:
    script = tmp_path / "automation.py"
    script.write_text(body, encoding="utf-8")

    direct = _run([sys.executable, str(script)], tmp_path)
    hosted = _run([sys.executable, "-m", MODULE, VIDEO_FLAG, str(tmp_path), str(script)], tmp_path)

    assert direct.returncode == hosted.returncode == code
    assert text in hosted.stderr


def test_launcher_without_a_script_explains_usage(tmp_path: Path) -> None:
    hosted = _run([sys.executable, "-m", MODULE, VIDEO_FLAG, str(tmp_path)], tmp_path)

    assert hosted.returncode == 2
    assert "usage" in hosted.stderr


def test_recording_options_follow_the_page_size(tmp_path: Path) -> None:
    recorder = Recorder(tmp_path)

    given: dict[str, object] = {"viewport": {"width": 1920, "height": 1080}}
    assert recorder.options(given) is True
    assert given["record_video_dir"] == tmp_path / VIDEO_TMP
    assert given["record_video_size"] == {"width": 1280, "height": 720}

    default: dict[str, object] = {"no_viewport": True}
    assert recorder.options(default) is True
    assert default["record_video_size"] == {"width": 1280, "height": 720}

    sized: dict[str, object] = {"record_video_size": {"width": 320, "height": 240}}
    assert recorder.options(sized) is True
    assert sized["record_video_size"] == {"width": 320, "height": 240}


def test_scripts_own_recording_is_left_alone(tmp_path: Path) -> None:
    own: dict[str, object] = {"record_video_dir": "mine"}

    assert Recorder(tmp_path).options(own) is False
    assert own == {"record_video_dir": "mine"}


def test_compat_script_steps_are_recorded(tmp_path: Path) -> None:
    """相容模式也有 RPA_STEPS：rpa_script.current().step() 的步驟寫進 steps.json。"""
    result = execute(_compat(tmp_path / "scene", STEPPED), {}, out_root=tmp_path / "runs")

    assert result.status == "passed", result.error
    assert [(step["id"], step["action"], step["status"]) for step in result.steps] == [
        ("prepare", "python", "passed")
    ]
    assert (result.directory / STEPS).is_file()
    assert not (result.directory / VIDEO_INFO).exists()


def test_compat_script_without_a_browser_says_so(tmp_path: Path) -> None:
    """錄影時腳本沒有開瀏覽器：video.json 記下 no_browser，回看頁照這個說明。"""
    result = execute(
        _compat(tmp_path / "scene", STEPPED), {}, out_root=tmp_path / "runs", record_video=True
    )

    assert result.status == "passed", result.error
    info = json.loads((result.directory / VIDEO_INFO).read_text(encoding="utf-8"))
    assert info["file"] is None
    assert info["error"] == NO_BROWSER
    assert not (result.directory / VIDEO).exists()
    assert not (result.directory / VIDEO_TMP).exists()
    assert [step["id"] for step in result.steps] == ["prepare"]


def test_no_browser_note_only_after_the_automation_ran(tmp_path: Path) -> None:
    """入參沒通過就沒有執行腳本：不說「腳本沒有開瀏覽器」。"""
    path = _compat(tmp_path / "scene", STEPPED)
    path.write_text(
        path.read_text(encoding="utf-8") + "inputs:\n  n: { type: integer }\n", encoding="utf-8"
    )

    result = execute(path, {"n": "不是數字"}, out_root=tmp_path / "runs", record_video=True)

    assert result.status == "failed"
    assert not (result.directory / VIDEO_INFO).exists()
