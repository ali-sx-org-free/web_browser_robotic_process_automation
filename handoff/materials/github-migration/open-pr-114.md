# PR #114（未合併）：docs: 文檔站對齊 v0.8.0 與 Python 節點

- 分支：`docs/refresh-v0-8` → `main`
- 舊 GitHub 上的 head：`491890c`（之後 bootstrap 可能又推了一個簡中的提交，帳號停權後無法確認）
- 這個包裡的分支：`c48f095`（比 GitHub 多一個只在本機的提交）
- 下面是當時 PR 的說明原文。

---

## 做了什麼

把 `docs/` 裡還停在 v0.6.3 的頁面對齊 main `673dc4c`：v0.7.0、v0.7.1、v0.8.0 三次發布，以及 v0.8.0 之後合併、尚未發布的 Python 節點（#109，ADR 0020）。只改文件，不改程式。

- 首頁、路線圖、ADR 索引（19 項）、頁首標籤 v0.8.0；路線圖補上 #101、#103、#105、#106 的版本，Python 節點改成「#109 已合併、main 上尚未發布、人工驗收未執行」。
- 系統架構、技術選型、產品定位：加上 Python 節點、`rpa-script`、RPA Python 運行環境（部署圖、資料目錄的 `workspaces/`、執行目錄的 `outputs/`／`previews/`／`files.json`、套件表、目錄結構、資料流）。
- 桌面端分發：發布歷史到 v0.8.0；v0.6.3～v0.8.0 從上一版升級都只要更新檔；main 起 RPA Worker 與伺服器分發包把運行環境算進環境代號，**下一個版本這兩樣要用完整的安裝包**（錄製端照 Release 說明）。
- Agent 使用指南新增「Python 節點」面板（存檔的 `files`、`debug_script`、要有運行環境的 Worker、array／object 入參與產出檔案、不能用登入角色）。
- 開發文件：版本範例；本機 `uv run pytest` 的 skipped 說明（只在 Windows 測的、要真的運行環境的 2 項）；遠端 Worker、部署與操作、CI 的 Python 節點與運行環境流程。
- **待你確認**：倉庫在 2026-11-06 查證時是公開的（API `private: false`），但 2026-10-22 的決定是維持私有，`handoff/` 與事件紀錄都查不到改回的時間。桌面端分發與 CI 頁改成「2026-10-22 改成私有；2026-11-06 查證時是公開的（何時改回沒有紀錄）」，沒有補寫決定。
- 另外回填 `20261024-python-scripts` 在任務索引的狀態與一條追加紀錄（PR #109 已在 2026-11-06 04:55 PST 合併）。

- 任務紀錄：[handoff/tasks/20261106-docs-refresh-v0-8.html](https://github.com/DevopsLeaDevops/web_browser_robotic_process_automation/blob/docs/refresh-v0-8/handoff/tasks/20261106-docs-refresh-v0-8.html)
- 主責／審閱者：Claude（文檔更新）；審閱：未審閱
- 目標分支／相依 PR：main；無相依

## 怎麼驗證

- 本地（`a93123f`，雲端 Linux、系統 Python 3.13.18、pytest 9.1.1；連不到 PyPI，沒有 OpenCC）：每個改過的英文頁 `python3 tools/i18n.py stamp`；`python3 -m pytest -q tests/docs tests/i18n` 365 passed，3 failed 都是簡中還沒產生（兩頁的新錨點 `python-nodes`、`test_simplified_chinese_is_generated`），由本次推送的 `[bootstrap]` 產生；`git diff --check` 通過；`handoff/` 改到的三頁相對連結與錨點 0 個問題；Chromium 截圖檢查系統架構部署圖（繁中、英文）與發布流程圖，文字沒有超出方框。基準 main `673dc4c` 同樣的測試是 367 passed、1 failed（OpenCC）。
- CI：見本 PR 最新 head（bootstrap 提交簡中之後）。
- 人工驗收：不適用（只改文件）。
- 審閱：未審閱。

## 還沒做的部分

- 簡中由 bootstrap 產生，之後確認最新 head 的 CI。
- 倉庫可見度要你確認；`handoff/` 的狀態總表與驗收紀錄、其他任務紀錄的狀態欄不在這次範圍。

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01RSqXu3z8vtbCSoPXB6sFYT
