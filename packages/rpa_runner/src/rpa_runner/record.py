"""接著既有場景錄製（M4）：先在瀏覽器執行既有的步驟，再從那個畫面開始錄製。

由管理 Portal 啟動::

    python -m rpa_runner.record --scenario 場景.yaml --input input.json --output 錄製稿.py \
        --out 目錄 [--engine 瀏覽器] [--base-url 網址] [--storage-state 登入狀態檔] \
        [--calls 子場景.json]

- 瀏覽器視窗與 Playwright Inspector 開在這台電腦上（有頭模式）。
- 先依序執行既有的步驟（``{{ }}`` 以入參的預設值與 Secrets 代入）；任何一步失敗就結束，不錄製。
  檔案入參（M7c）同調試：``--file 入參 檔案`` 是管理 Portal 準備好的檔案。執行既有步驟時攔下
  選擇檔案的視窗，開始錄製前解除，使用者錄製時才能在系統的視窗選檔。
- 之後開始錄製：使用者的操作由 Playwright 的錄製器寫進 ``--output``，寫法和 ``playwright codegen``
  相同。既有的步驟不會出現在錄製稿（也不會出現在 Inspector）裡；轉換後由管理 Portal 接在既有
  場景的最後。
- 使用者關掉瀏覽器視窗就結束。
- 用到子場景（M7.2）的場景：``--calls`` 是伺服器把版本的 ``calls/`` 包成的 JSON，放回場景檔旁邊
  再校驗，既有的 ``call`` 照樣在同一個分頁執行整個子場景。

Playwright 沒有公開「在已經開好的瀏覽器上開始錄製」的 API，這裡用 codegen 自己用的通訊命令：
1.64 以前是 ``enableRecorder``，1.65 起改名 ``showRecorder``，由 ``BrowserContext._show_recorder``
送出。Playwright 改版時由 ``tests/test_record_browser.py`` 的真實瀏覽器測試發現。

標準輸出一行一個 JSON 事件：``replaying``、``recording``、``error``（含 step、message）。
結束碼：0 正常結束、3 既有步驟執行失敗、1 其他錯誤。
"""

import argparse
import contextlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Final, cast

from playwright.sync_api import BrowserContext, sync_playwright

from rpa_core.dsl import Scenario, validate_file
from rpa_core.dsl.calls import CallKey, load_calls, read_call_bundle, write_call_files
from rpa_core.i18n import DEFAULT_LOCALE, ENV_VAR, parse_locale, set_locale
from rpa_runner.browser import Deadline, Tabs, plan_records, run_steps
from rpa_runner.contexts import Engine, open_context
from rpa_runner.contract import check_inputs
from rpa_runner.i18n import t
from rpa_runner.inputfiles import given_files, remove_staging, session_files
from rpa_runner.secrets import mask, read_secrets

__all__ = ["EXIT_REPLAY_FAILED", "REPLAY_SECONDS", "enable_recorder", "load_replay", "main"]

EXIT_REPLAY_FAILED: Final = 3
REPLAY_SECONDS: Final = 300.0
"""執行既有步驟最多這麼久（場景有 deadline 時用它）。"""


def _emit(event: str, **details: object) -> None:
    sys.stdout.write(json.dumps({"event": event, **details}, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def enable_recorder(context: BrowserContext, output: Path) -> None:
    """在已經開好的 context 上開始錄製，錄製稿（Python）寫到 ``output``。"""
    impl = context._impl_obj  # pyright: ignore[reportPrivateUsage]
    params = {
        "language": "python",
        "mode": "recording",
        "outputFile": str(output.absolute()),
        "handleSIGINT": False,
    }
    # 內部 API：Playwright 1.65 起 Channel 沒有 send，enableRecorder 改名 showRecorder，
    # 由 BrowserContext._show_recorder 送出（codegen 也是這樣開始錄製）
    context._sync(impl._show_recorder(params))  # pyright: ignore[reportPrivateUsage]


def _wait_closed(context: BrowserContext) -> None:
    """等使用者關掉所有分頁（瀏覽器視窗）。"""
    while True:
        pages = [page for page in context.pages if not page.is_closed()]
        if not pages:
            return
        try:
            pages[0].wait_for_event("close", timeout=0)  # pyright: ignore[reportUnknownMemberType]
        except Exception:  # 瀏覽器被關掉（或當掉）：一樣當作錄製結束
            return


def load_replay(
    args: argparse.Namespace,
) -> tuple[Scenario, dict[str, object], dict[CallKey, Scenario]]:
    """要先執行的場景、入參與子場景（子場景檔先從 ``--calls`` 放回場景檔旁邊）。"""
    path = Path(args.scenario)
    bundle = getattr(args, "calls", None)
    if bundle:
        write_call_files(path.parent, read_call_bundle(Path(bundle)))
    validated = validate_file(path)
    if validated.scenario is None:
        raise ValueError(t("child.invalid_scenario"))
    inputs = cast("dict[str, object]", json.loads(Path(args.input).read_text(encoding="utf-8")))
    resolved, problems = check_inputs(validated.scenario, inputs)
    if problems:
        raise ValueError("; ".join(problem.message for problem in problems))
    # 子場景的問題校驗時已經擋下（同 rpa_runner.child）
    calls = load_calls(path.parent, validated.scenario)[0]
    return validated.scenario, resolved, calls


def _files(
    args: argparse.Namespace, scenario: Scenario, inputs: dict[str, object], staging: Path
) -> dict[str, list[Path]]:
    """檔案入參（M7c）：準備好的檔案；input.json 與表達式裡換成名稱、大小、sha256。"""
    prepared = session_files(
        scenario,
        inputs,
        given_files(cast("list[list[str]] | None", getattr(args, "file", None))),
        Path(args.scenario).parent,
        staging,
    )
    if prepared.problems:
        raise ValueError("; ".join(problem.message for problem in prepared.problems))
    inputs.update(prepared.meta)
    return prepared.paths


def record(args: argparse.Namespace) -> int:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="rpa-record-files-"))
    try:
        return _record(args, out, staging)
    finally:
        remove_staging(staging)


def _record(args: argparse.Namespace, out: Path, staging: Path) -> int:
    scenario, inputs, calls = load_replay(args)
    files = _files(args, scenario, inputs, staging)
    (out / "input.json").write_text(json.dumps(inputs, ensure_ascii=False), encoding="utf-8")
    secrets = read_secrets(scenario)
    with sync_playwright() as playwright, contextlib.ExitStack() as stack:
        viewport = scenario.browser.viewport
        context = open_context(
            playwright,
            cast("Engine", args.engine),
            headed=True,
            timeout_ms=120_000,
            budget_seconds=120,
            stack=stack,
            viewport={"width": viewport.width, "height": viewport.height} if viewport else None,
            locale=scenario.browser.locale,
            storage_state=Path(args.storage_state) if args.storage_state else None,
        )
        page = context.pages[0] if context.pages else context.new_page()
        tabs = Tabs(page)
        records = plan_records(scenario)
        _emit("replaying", steps=len(records))
        seconds = scenario.deadline / 1000 if scenario.deadline else REPLAY_SECONDS
        try:
            run_steps(
                page,
                scenario,
                records=records,
                context={"inputs": inputs, "secrets": secrets, "env": dict(os.environ)},
                base_url=args.base_url or scenario.browser.base_url,
                artifacts=out,
                deadline=Deadline.after(seconds),
                tabs=tabs,
                files=files,
                calls=calls,
            )
        except Exception as error:
            failed = next((item for item in records if item.status == "failed"), None)
            message = mask(f"{type(error).__name__}: {error}".splitlines()[0], secrets)
            _emit("error", step=failed.id if failed else None, message=message)
            return EXIT_REPLAY_FAILED
        tabs.release()
        enable_recorder(context, Path(args.output))
        _emit("recording")
        _wait_closed(context)
    return 0


def main(argv: list[str] | None = None) -> int:
    set_locale(parse_locale(os.environ.get(ENV_VAR, "")) or DEFAULT_LOCALE)
    parser = argparse.ArgumentParser(prog="python -m rpa_runner.record")
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--engine", choices=["chromium", "firefox", "webkit"], default="chromium")
    parser.add_argument("--base-url")
    parser.add_argument("--storage-state")
    parser.add_argument(
        "--file",
        nargs=2,
        action="append",
        metavar=("INPUT", "PATH"),
        help="準備好的檔案入參（M7c）",
    )
    parser.add_argument("--calls", help="子場景檔的 JSON（M7.2）：calls/… 的相對路徑 → 內容")
    args = parser.parse_args(argv)
    try:
        return record(args)
    except Exception as error:
        _emit("error", step=None, message=f"{type(error).__name__}: {error}".splitlines()[0])
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
