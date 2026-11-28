"""相容模式 Python 腳本的啟動器：替腳本自己開的瀏覽器錄影（ADR 0016 2026-11-28 修訂、ADR 0020）。

``python -m rpa_runner.scripthost --video 執行目錄 automation.py --input … --facts …``

Runner 錄影時用它執行相容模式（沒寫 ``runtime``）的 automation.py；不錄影時照舊直接執行腳本。

- 掛在 Playwright 的公開 API 上（同步與 asyncio 兩套）：腳本用 ``Browser.new_context``、
  ``Browser.new_page``、``BrowserType.launch_persistent_context`` 開的 context 自動加上錄影，
  寫到執行目錄的 ``.video/``；畫面大小照 DSL 的規則（:func:`rpa_runner.video.video_size`）。
  腳本自己指定 ``record_video_dir`` 的 context 不改，那段錄影也不收。
- 每個分頁記成 page-1、page-2…（開頁時間、影片檔名、Chromium 的首格觀測時間），寫在
  ``.video/pages.json``，格式和 DSL 的子程序相同（:class:`rpa_runner.video.PageVideos`），
  Runner 照樣用 :func:`rpa_runner.video.finalize` 整理。
- 腳本關瀏覽器（``browser.close()``）或結束 Playwright（離開 ``with sync_playwright()``、呼叫
  ``playwright.stop()``）之前，先關掉錄影中的 context：Playwright 關 context 時才把影片寫完
  （DSL 的子程序也是先關 context，見 contexts.py）。2026-11-28 在雲端容器實測：只關瀏覽器時影片
  是 0 位元組；沒關瀏覽器就離開 ``with`` 時只有開頭一格。
- 以 ``__main__`` 執行腳本，``sys.argv`` 與 import 路徑和直接 ``python automation.py …`` 相同
  （打包後和 ``rpa-child --rpa-script`` 相同），腳本不用改。腳本的例外與 ``sys.exit`` 照原樣往外拋。
- 錄影的掛勾出錯只會少了影片，不會讓腳本失敗：錯誤吞掉，主控台留一行說明。

只有 ``PlaywrightContextManager`` 的結束是 Playwright 的內部模組；升級 Playwright 時由
packages/rpa_runner/tests/test_scripthost.py 確認。
"""

import asyncio
import contextlib
import functools
import importlib
import runpy
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any, Final, cast

from playwright import async_api, sync_api
from playwright.sync_api import ScreencastFrame, ViewportSize

from rpa_runner.commands import is_frozen
from rpa_runner.files import VIDEO_TMP
from rpa_runner.i18n import t
from rpa_runner.video import PageVideos, video_size

__all__ = ["MODULE", "VIDEO_FLAG", "Recorder", "install", "main"]

MODULE: Final = "rpa_runner.scripthost"
VIDEO_FLAG: Final = "--video"
"""後面接執行目錄：錄影寫到它的 ``.video/``。"""


def _warn(error: BaseException) -> None:
    """錄影的掛勾出錯：主控台（automation.log）留一行，腳本照常執行。"""
    with contextlib.suppress(Exception):
        detail = f"{type(error).__name__}: {error}"
        sys.stderr.write(t("scripthost.video_failed", error=detail) + "\n")
        sys.stderr.flush()


class Recorder:
    """一次執行的錄影：替腳本開的 context 加上參數、記下分頁、結束前關掉 context。"""

    def __init__(self, folder: Path) -> None:
        self.folder = folder
        self.videos = PageVideos(folder, engine="chromium")
        self.contexts: list[sync_api.BrowserContext] = []
        self.async_contexts: list[async_api.BrowserContext] = []
        self._tasks: set[asyncio.Future[None]] = set()
        """停止 Chromium 首格觀測的工作（留著參照，免得還沒做完就被回收）。"""

    def options(self, kwargs: dict[str, Any]) -> bool:
        """在開 context 的參數加上錄影；腳本自己錄影時不改，回傳 False。"""
        if kwargs.get("record_video_dir") is not None:
            return False
        viewport = kwargs.get("viewport")
        kwargs["record_video_dir"] = self.folder / VIDEO_TMP
        if kwargs.get("record_video_size") is None:
            kwargs["record_video_size"] = video_size(
                cast("ViewportSize", viewport) if isinstance(viewport, dict) else None
            )
        return True

    # ------------------------------------------------------------ 同步 API

    def watch(self, context: sync_api.BrowserContext, engine: str) -> None:
        try:
            self.contexts.append(context)
            context.on("close", lambda _: self._forget(context))
            self.videos.watch(context, engine=engine)
        except Exception as error:
            _warn(error)

    def _forget(self, context: sync_api.BrowserContext) -> None:
        with contextlib.suppress(ValueError):
            self.contexts.remove(context)

    def close(self, among: Sequence[sync_api.BrowserContext] | None = None) -> None:
        """關掉還開著的 context（後開的先關；``among`` 是只關這個瀏覽器的）：影片在這時寫完。"""
        for context in reversed(list(self.contexts)):
            if among is not None and context not in among:
                continue
            self._forget(context)
            with contextlib.suppress(Exception):  # 瀏覽器已經被結束（取消、當掉）也沒關係
                context.close()

    # ------------------------------------------------------------ asyncio API

    async def watch_async(self, context: async_api.BrowserContext, engine: str) -> None:
        try:
            self.async_contexts.append(context)

            def closed(_: object) -> None:
                with contextlib.suppress(ValueError):
                    self.async_contexts.remove(context)

            async def opened(page: async_api.Page) -> None:
                await self._identify_async(page, engine)

            context.on("close", closed)
            context.on("page", opened)
            for page in list(context.pages):
                await self._identify_async(page, engine)
        except Exception as error:
            _warn(error)

    async def _identify_async(self, page: async_api.Page, engine: str) -> None:
        """和 :meth:`PageVideos.identify` 相同，只是影片檔名與首格時間要 await。"""
        mark = self.videos.add(page)
        if mark is None:
            return
        with contextlib.suppress(Exception):
            if page.video is not None:
                mark["file"] = (await page.video.path()).name

        async def stop() -> None:
            with contextlib.suppress(Exception):
                await page.screencast.stop()

        def frame_seen(frame: ScreencastFrame) -> None:
            if self.videos.observed(mark, frame["timestamp"]):
                task = asyncio.ensure_future(stop())
                self._tasks.add(task)
                task.add_done_callback(self._tasks.discard)

        if engine == "chromium":
            with contextlib.suppress(Exception):
                await page.screencast.start(on_frame=frame_seen)
        self.videos.save()

    async def close_async(self, among: Sequence[async_api.BrowserContext] | None = None) -> None:
        for context in reversed(list(self.async_contexts)):
            if among is not None and context not in among:
                continue
            with contextlib.suppress(ValueError):
                self.async_contexts.remove(context)
            with contextlib.suppress(Exception):
                await context.close()


# ---------------------------------------------------------------- 掛勾


def _patch(owner: type, name: str, make: Callable[[Any], Any]) -> None:
    original = getattr(owner, name)
    setattr(owner, name, functools.wraps(original)(make(original)))


def _sync_hooks(recorder: Recorder) -> None:
    def new_context(original: Any) -> Any:
        def wrapper(self: sync_api.Browser, **kwargs: Any) -> sync_api.BrowserContext:
            recorded = recorder.options(kwargs)
            context = cast("sync_api.BrowserContext", original(self, **kwargs))
            if recorded:
                recorder.watch(context, self.browser_type.name)
            return context

        return wrapper

    def new_page(original: Any) -> Any:
        def wrapper(self: sync_api.Browser, **kwargs: Any) -> sync_api.Page:
            recorded = recorder.options(kwargs)
            page = cast("sync_api.Page", original(self, **kwargs))
            if recorded:
                recorder.watch(page.context, self.browser_type.name)
            return page

        return wrapper

    def persistent(original: Any) -> Any:
        def wrapper(
            self: sync_api.BrowserType, user_data_dir: object, **kwargs: Any
        ) -> sync_api.BrowserContext:
            recorded = recorder.options(kwargs)
            context = cast("sync_api.BrowserContext", original(self, user_data_dir, **kwargs))
            if recorded:
                recorder.watch(context, self.name)
            return context

        return wrapper

    def close(original: Any) -> Any:
        def wrapper(self: sync_api.Browser, **kwargs: Any) -> None:
            recorder.close(among=self.contexts)
            original(self, **kwargs)

        return wrapper

    _patch(sync_api.Browser, "new_context", new_context)
    _patch(sync_api.Browser, "new_page", new_page)
    _patch(sync_api.Browser, "close", close)
    _patch(sync_api.BrowserType, "launch_persistent_context", persistent)
    manager = cast("Any", importlib.import_module("playwright.sync_api._context_manager"))

    def exit_(original: Any) -> Any:
        def wrapper(self: object, *args: object) -> object:
            recorder.close()
            return original(self, *args)

        return wrapper

    _patch(manager.PlaywrightContextManager, "__exit__", exit_)


def _async_hooks(recorder: Recorder) -> None:
    def new_context(original: Any) -> Any:
        async def wrapper(self: async_api.Browser, **kwargs: Any) -> async_api.BrowserContext:
            recorded = recorder.options(kwargs)
            context = cast("async_api.BrowserContext", await original(self, **kwargs))
            if recorded:
                await recorder.watch_async(context, self.browser_type.name)
            return context

        return wrapper

    def new_page(original: Any) -> Any:
        async def wrapper(self: async_api.Browser, **kwargs: Any) -> async_api.Page:
            recorded = recorder.options(kwargs)
            page = cast("async_api.Page", await original(self, **kwargs))
            if recorded:
                await recorder.watch_async(page.context, self.browser_type.name)
            return page

        return wrapper

    def persistent(original: Any) -> Any:
        async def wrapper(
            self: async_api.BrowserType, user_data_dir: object, **kwargs: Any
        ) -> async_api.BrowserContext:
            recorded = recorder.options(kwargs)
            context = cast(
                "async_api.BrowserContext", await original(self, user_data_dir, **kwargs)
            )
            if recorded:
                await recorder.watch_async(context, self.name)
            return context

        return wrapper

    def close(original: Any) -> Any:
        async def wrapper(self: async_api.Browser, **kwargs: Any) -> None:
            await recorder.close_async(among=self.contexts)
            await original(self, **kwargs)

        return wrapper

    _patch(async_api.Browser, "new_context", new_context)
    _patch(async_api.Browser, "new_page", new_page)
    _patch(async_api.Browser, "close", close)
    _patch(async_api.BrowserType, "launch_persistent_context", persistent)
    manager = cast("Any", importlib.import_module("playwright.async_api._context_manager"))

    def exit_(original: Any) -> Any:
        async def wrapper(self: object, *args: object) -> object:
            await recorder.close_async()
            return await original(self, *args)

        return wrapper

    _patch(manager.PlaywrightContextManager, "__aexit__", exit_)


def install(folder: Path) -> Recorder | None:
    """掛上錄影；掛不上（Playwright 改了公開 API）時回傳 None，腳本照常執行、沒有錄影。"""
    recorder = Recorder(folder)
    try:
        _sync_hooks(recorder)
        _async_hooks(recorder)
    except Exception as error:
        _warn(error)
        return None
    return recorder


# ---------------------------------------------------------------- 啟動


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    folder: Path | None = None
    if len(args) >= 2 and args[0] == VIDEO_FLAG:
        folder = Path(args[1])
        args = args[2:]
    if not args:
        sys.stderr.write(f"usage: python -m {MODULE} [{VIDEO_FLAG} RUN_DIR] SCRIPT [ARGS...]\n")
        return 2
    script = Path(args[0]).resolve()
    if folder is not None:
        install(folder)
    sys.argv = [str(script), *args[1:]]
    # 和直接 ``python 腳本`` 一樣，腳本所在的資料夾排在 import 路徑的最前面：``-m`` 放的是
    # 工作目錄，換掉。打包後 sys.path[0] 是 App 自己的程式庫，不能換，插在前面
    # （同 rpa_desktop.entry.run_script）
    if is_frozen() or not sys.path:
        sys.path.insert(0, str(script.parent))
    else:
        sys.path[0] = str(script.parent)
    runpy.run_path(str(script), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
