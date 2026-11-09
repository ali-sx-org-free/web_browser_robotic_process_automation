# 舊 GitHub 倉庫的資料（截至 2026-11-08）

整理者：Claude。GitHub 從 2026-11-06 約 18:15 America/Los_Angeles（PST，UTC−08:00）起對這個帳號的 API 與 git 都回 403「Sorry. Your account was suspended」，2026-11-08 再試仍然一樣，所以這裡只有之前取得、或從程式碼與 git 歷史整理得到的資料。沒有把握的地方明寫「不知道」。

## 帳號與倉庫

| 項目 | 內容 |
|---|---|
| 帳號 | `DevopsLeaDevops`（GitHub 回應是「帳號已停權」，不只是密碼問題） |
| 主倉庫 | `DevopsLeaDevops/web_browser_robotic_process_automation`，預設分支 `main`；2026-11-06 查證時是公開的（API `private: false`）。2026-10-22 的決定是改成私有，何時改回沒有紀錄 |
| 資料倉庫 | `DevopsLeaDevops/web_browser_robotic_process_automation_site`：RPA 伺服器的「git 同步」推送的領域資料夾 `testsite/`；2026-11-07 列出時是公開的 |
| main 最後一個提交 | `673dc4c`（Merge PR #112），2026-11-06 17:50 PST |
| 最新的正式 Release | v0.8.0（2026-10-29 06:53 PDT 發布） |
| 未合併的 PR | #114 `docs/refresh-v0-8` → main：文檔對齊 v0.8.0 與 Python 節點（Claude 建立，見 `open-pr-114.md`）。開著的只有它（2026-11-06 查證） |

## 分支

| 分支 | 在這個包裡嗎 | 說明 |
|---|---|---|
| `main` | 有，完整歷史 | 從第一個提交 `d548c06`（chore: 初始化倉庫）到 `673dc4c` |
| `docs/refresh-v0-8` | 有 | PR #114；本機比 GitHub 多一個提交 `c48f095`（帳號停權後只在本機） |
| `ci-metrics` | **沒有** | `.github/workflows/ci-metrics.yml` 每次 CI 後把各工作的耗時追加到這個分支；只是統計資料，在新倉庫會重新累積 |
| 其他功能分支 | 沒有 | 已合併的內容都在 main 的歷史裡；沒合併、也沒開 PR 的分支不知道有沒有 |

資料倉庫只有 `main` 一個提交 `5c98ad6`（2026-10-21 10:09 新加坡時間，作者 `mac-a <rpa-portal@localhost>`）。它是根提交，所以這就是 GitHub 上的全部歷史；之後如果伺服器還推送過，較新的提交在 RPA 伺服器的 `<資料目錄>/git/repos/testsite.git` 裡（見教程第 7 節）。

## 標籤與 Release

11 個標籤都在包裡（`git tag` 看得到）。Release 的安裝檔（DMG、Windows 安裝檔、zip、伺服器分發包、更新檔、SHA256SUMS.txt）只在舊 GitHub 上，這裡沒有，要在新倉庫重新建置（教程第 6 節）。Release 說明是發布流程用 `--generate-notes`（GitHub 依 PR 自動產生）加上執行環境比較的段落組成，原文沒有存進倉庫；各版做了什麼、驗證與已知問題記在任務紀錄。

| 標籤 | 提交 | 種類 | 提交時間 | Release 發布時間 | 發布的任務紀錄 |
|---|---|---|---|---|---|
| v0.2.0 | `d71f513` | 附註標籤 | 2026-10-18 08:53 PDT | 未記錄 | — |
| v0.3.0 | `2cf3c9f` | 附註標籤 | 2026-10-19 09:27 PDT | 未記錄 | — |
| v0.4.0 | `fcb8e8f` | 輕量標籤 | 2026-10-21 05:54 PDT | 未記錄 | `handoff/tasks/20261021-release-0-4-0.html` |
| v0.5.0 | `6522d74` | 附註標籤 | 2026-10-22 21:00 PDT | 未記錄 | `handoff/tasks/20261022-release-0-5-0.html` |
| v0.6.0 | `f76a950` | 附註標籤 | 2026-10-25 17:31 PDT | 未記錄 | `handoff/tasks/20261025-release-0-6-0.html` |
| v0.6.1 | `262e107` | 附註標籤 | 2026-10-26 01:35 PDT | 未記錄 | — |
| v0.6.2 | `8e84c6a` | 附註標籤 | 2026-10-26 05:03 PDT | 未記錄 | `handoff/tasks/20261026-release-0-6-2.html` |
| v0.6.3 | `066ded2` | 附註標籤 | 2026-10-26 08:45 PDT | 2026-10-26 19:20 PDT | `handoff/tasks/20261026-release-0-6-3.html` |
| v0.7.0 | `469c3be` | 輕量標籤 | 2026-10-28 02:30 PDT | 2026-10-28 02:41 PDT | `handoff/tasks/20261028-release-0-7-0.html` |
| v0.7.1 | `2089d48` | 附註標籤 | 2026-10-29 04:08 PDT | 2026-10-29 04:24 PDT | — |
| v0.8.0 | `e5b585e` | 附註標籤 | 2026-10-29 06:37 PDT | 2026-10-29 06:53 PDT | `handoff/tasks/20261029-release-0-8-0.html` |

v0.8.0 的檔案（依當時的 Release）：RPA 錄製端 DMG 約 90 MB、RPA Worker 的 DMG 約 89 MB、Windows 安裝檔約 63 MB、免安裝 zip 約 80 MB、更新檔 `RPA-Update-0.8.0.zip` 約 2.4 MB、伺服器分發包（Linux x64、arm64 的 tar.gz）、`SHA256SUMS.txt`。v0.6.3～v0.8.0 從上一版升級都只要更新檔；v0.6.2 的錄製端與 Worker 要完整安裝包。

## Actions 的 Secrets（值無法匯出）

GitHub 不讓任何人讀回 Secret 的值，帳號停權後更拿不到。新倉庫要重新設定：

| 名稱 | 用途 | 舊值在哪裡 | 新倉庫怎麼辦 |
|---|---|---|---|
| `RPA_UPDATE_SIGNING_KEY` | 發布時簽署更新檔 `RPA-Update-<版本>.zip`（Ed25519 私鑰 PEM）。已安裝的伺服器與裝置只接受對得上 `packages/rpa_update/src/rpa_update/keys.py` 公鑰的更新檔 | 2026-10-25 05:52 PDT 由你自己產生；文件要求另外備份到密碼管理器。對應的公鑰是 `+zBkjVUh9RensU1hgeWNOeJuRqH82tguO7byaNXCr6w=` | 找得到原本的 `rpa-update-signing.pem` 就照舊設定；找不到就產生新的一把（教程第 5 節） |
| `RPA_UPDATE_CI_KEY` | CI 試用包的測試金鑰，讓桌面端建置能沿用快取的外殼 | 不確定是否設定過（2026-10-26 時還沒設） | 直接產生新的；沒有也能跑，只是每次完整建置並留下警告 |

工作流程沒有用到 `vars.*`（Variables），也沒有自架的 runner（全部是 `ubuntu-latest`、`windows-latest` 與 matrix 的 GitHub 主機）。

## 工作流程與倉庫設定

| 工作流程 | 觸發 | 新倉庫要注意 |
|---|---|---|
| `ci.yml` CI | push、PR、手動 | 推送 main 後會自動跑 |
| `desktop.yml` 桌面端建置 | PR、push、被發布呼叫、手動 | 沒有 `RPA_UPDATE_CI_KEY` 時完整建置並警告 |
| `server-package.yml` 伺服器分發包 | PR、push、被呼叫、手動 | — |
| `python-runtime.yml` RPA Python 運行環境 | PR、push、被呼叫、手動 | — |
| `setup-scripts.yml` 一鍵安裝腳本 | push、PR、每天 20:47 UTC、手動 | 失敗時開 issue（要開啟 Issues） |
| `nightly.yml` 每晚測試 | 每天 20:17 UTC、每週六 22:47 UTC、PR、手動 | 失敗時開 issue |
| `release.yml` 發布 | 推 `v*` 標籤 | 用 `RPA_UPDATE_SIGNING_KEY`；一次推超過 3 個標籤時 GitHub 不產生事件，不會觸發 |
| `bootstrap.yml` | push（提交訊息帶 `[bootstrap]`）、手動 | 產生簡中並推回分支 |
| `ci-metrics.yml` | CI 結束後、PR、手動 | 推送 `ci-metrics` 分支（第一次會自己建立） |
| `uv-upgrade.yml` Python 依賴更新 | 每週日 22:17 UTC、手動 | 用 GITHUB_TOKEN 開 PR：新倉庫要開啟「Allow GitHub Actions to create and approve pull requests」 |
| `cleanup-artifacts.yml` | 手動 | — |

`.github/dependabot.yml` 只更新 GitHub Actions 的版本（Python 依賴改由 `uv-upgrade.yml`）。分支保護規則、Webhook、部署金鑰、協作者：舊倉庫有沒有設定我不知道；資料倉庫如果用 SSH 同步，舊倉庫上有一把 RPA 伺服器產生的部署金鑰。

Claude 的 GitHub App 裝在舊帳號上（這幾次的 session 靠它推送與開 PR）；新帳號要重新安裝並在 claude.ai 連接 GitHub。

## 程式與文件裡寫死的舊網址

只換 `DevopsLeaDevops/web_browser_robotic_process_automation` 這串路徑（`03-tools/update-repo-url.sh` 會做，見教程第 4 節）：

- `apps/desktop/src/rpa_desktop/release.py`：App 的「下載新版」連到舊倉庫的 Releases。已安裝的 App 要等下一次更新才會換成新網址。
- `apps/desktop/packaging/rpa_worker.iss`：Windows 安裝檔的「關於」網址。
- `scripts/setup.sh`、`scripts/setup.ps1`、`scripts/setup-linux.sh`：一鍵安裝時 clone 的網址與下載腳本的網址。
- `docs/`：開發環境、本機從零運行、macOS、遠端 Worker、桌面端分發（繁中、英文、簡中各一份）。

**不要改的**：`io.github.devopsleadevops.rpa.recorder`、`io.github.devopsleadevops.rpa.worker`（macOS App 的識別碼與開機自動啟動的 LaunchAgent 名稱，改了已安裝的 App 會被當成另一個程式）、`rpa_worker.iss` 的 `AppId`（檔案裡註明「永遠不要改」）。`AppPublisher=DevopsLeaDevops` 只是顯示用的發行者名稱，可改可不改。`handoff/` 裡的舊連結是歷史紀錄（指向舊的 PR、提交與 CI 頁），建議保留不改。

## 只在舊 GitHub 上、這個包裡沒有的

- PR 的說明、討論、審閱留言（程式改動都在 git 歷史裡；PR 對照表見 `pull-requests-merged.md`）
- Issues（每晚測試與一鍵安裝腳本失敗時自動開的）
- Release 的安裝檔與原始說明
- Actions 的執行紀錄、日誌與產物
- `ci-metrics` 分支
- Secrets 的值、倉庫設定、Star 與 Watch

找回帳號時這些都還在：用 GitHub 的「Transfer」把倉庫轉到新帳號，issues、PR、wiki、star 與 watcher 會一起轉過去（教程第 1 節）。
