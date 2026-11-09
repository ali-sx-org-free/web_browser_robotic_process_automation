# CI 運行耗時紀錄

更新：2026-11-09 06:27 America/Los_Angeles（PST，UTC−08:00）。共 14 次運行。

每次 CI、桌面端建置、一鍵安裝腳本、每晚完整測試、發布結束後，由 `.github/workflows/ci-metrics.yml` 追加到 `data/`；本頁由 `tools/ci_metrics.py report` 產生，不要手改。耗時＝第一個工作建立到最後一個工作結束（含排隊）；機器時間＝各工作實際執行的時間總和。
規則與背景見 main 的 `docs/develop/ci.html`。

## 各流程：近 7 天（前 7 天）

| 流程 | 次數 | 通過 | 耗時中位數 | 耗時 P90 | 最長排隊中位數 | 機器時間（Linux／Windows／macOS） |
|---|---|---|---|---|---|---|
| CI | 4（0） | 3（0） | 6.5 分（0.0 分） | 8.3 分（0.0 分） | 0.4 分（0.0 分） | 33／8／0 分（0／0／0 分） |
| 桌面端建置 | 4（0） | 4（0） | 3.6 分（0.0 分） | 8.7 分（0.0 分） | 0.1 分（0.0 分） | 0／12／24 分（0／0／0 分） |
| 伺服器分發包 | 3（0） | 3（0） | 0.2 分（0.0 分） | 2.5 分（0.0 分） | 0.1 分（0.0 分） | 5／0／0 分（0／0／0 分） |
| 一鍵安裝腳本 | 3（0） | 2（0） | 3.1 分（0.0 分） | 5.1 分（0.0 分） | 0.1 分（0.0 分） | 7／4／6 分（0／0／0 分） |
| 每晚完整測試 | 0（0） | 0（0） | 0.0 分（0.0 分） | 0.0 分（0.0 分） | 0.0 分（0.0 分） | 0／0／0 分（0／0／0 分） |
| 發布 | 0（0） | 0（0） | 0.0 分（0.0 分） | 0.0 分（0.0 分） | 0.0 分（0.0 分） | 0／0／0 分（0／0／0 分） |

## 每天的機器時間（分鐘，洛杉磯日期，最近 14 天）

| 日期 | 運行次數 | Linux | Windows | macOS | 合計 |
|---|---|---|---|---|---|
| 2026-11-09 | 14 | 45 | 25 | 30 | 100 |

## 最慢的測試檔案（每份報告最近一次，括號是近 7 次的中位數）

### CI · pytest-report-3.12/pytest-report.xml

最近一次：2026-11-09 06:22 America/Los_Angeles（PST，UTC−08:00），合計 322 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 20.4（25.5） | 25 | `apps/server/tests/test_production_api.py` |
| 20.0（20.3） | 18 | `apps/cli/tests/test_serve.py` |
| 19.7（25.1） | 29 | `apps/server/tests/test_api.py` |
| 19.0（24.0） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 14.2（14.2） | 17 | `apps/worker/tests/test_recorder.py` |
| 14.0（16.6） | 14 | `apps/server/tests/test_workflow_api.py` |
| 14.0（15.9） | 20 | `apps/server/tests/test_recorder_api.py` |
| 13.2（18.7） | 11 | `apps/server/tests/test_gitsync.py` |
| 13.0（13.6） | 14 | `apps/worker/tests/test_gateway.py` |
| 12.5（16.5） | 13 | `apps/server/tests/test_replay.py` |

### CI · pytest-report-3.13/pytest-report.xml

最近一次：2026-11-09 06:22 America/Los_Angeles（PST，UTC−08:00），合計 747 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 109.8（107.2） | 12 | `apps/server/tests/test_portal.py` |
| 46.6（46.5） | 4 | `apps/server/tests/test_replay_flow.py` |
| 44.3（44.2） | 3 | `apps/server/tests/test_workflow_flow.py` |
| 35.7（31.1） | 3 | `apps/server/tests/test_remote_worker_flow.py` |
| 33.6（32.8） | 10 | `packages/rpa_runner/tests/test_debug.py` |
| 31.2（31.1） | 5 | `apps/server/tests/test_production_flow.py` |
| 23.6（22.5） | 15 | `apps/server/tests/test_replay.py` |
| 23.3（23.2） | 29 | `apps/server/tests/test_api.py` |
| 22.6（22.6） | 25 | `apps/server/tests/test_production_api.py` |
| 20.8（20.6） | 22 | `apps/server/tests/test_remote_worker_api.py` |

### CI · pytest-report-windows/pytest-report.xml

最近一次：2026-11-09 05:59 America/Los_Angeles（PST，UTC−08:00），合計 813 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 254.2（233.9） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 133.7（118.4） | 10 | `packages\rpa_runner\tests\test_frames.py` |
| 122.4（119.0） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 94.3（70.8） | 17 | `packages\rpa_runner\tests\test_upload.py` |
| 87.3（82.3） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 45.4（42.5） | 8 | `packages\rpa_runner\tests\test_tabs.py` |
| 42.0（37.7） | 2 | `packages\rpa_runner\tests\test_download_browser.py` |
| 22.5（23.9） | 1 | `packages\rpa_runner\tests\test_profiles.py` |
| 4.3（4.0） | 2 | `tests\smoke\test_browser.py` |
| 4.0（3.2） | 1 | `apps\desktop\tests\test_selftest.py` |

## 最近 40 次運行

| 開始（洛杉磯） | 流程 | 觸發 | 分支 | 結果 | 耗時 | 最長排隊 | 運行 |
|---|---|---|---|---|---|---|---|
| 11-09 06:22 | 桌面端建置 | PR | docs/refresh-v0-8-2 | success | 0.1 分 | 0.0 分 | [#42634027287](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42634027287/attempts/1) |
| 11-09 06:22 | 一鍵安裝腳本 | PR | docs/refresh-v0-8-2 | success | 0.1 分 | 0.1 分 | [#42634027107](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42634027107/attempts/1) |
| 11-09 06:22 | CI | PR | docs/refresh-v0-8-2 | success | 4.3 分 | 0.1 分 | [#42634027049](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42634027049/attempts/1) |
| 11-09 06:17 | 伺服器分發包 | 推送 | main | success | 0.2 分 | 0.1 分 | [#42633234661](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42633234661/attempts/1) |
| 11-09 06:17 | 桌面端建置 | 推送 | main | success | 0.2 分 | 0.1 分 | [#42633234814](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42633234814/attempts/1) |
| 11-09 06:17 | CI | 推送 | main | failure | 8.3 分 | 0.1 分 | [#42633235249](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42633235249/attempts/1) |
| 11-09 05:59 | 伺服器分發包 | PR | docs/refresh-v0-8-2 | success | 0.2 分 | 0.1 分 | [#42630330392](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42630330392/attempts/1) |
| 11-09 05:59 | 一鍵安裝腳本 | PR | docs/refresh-v0-8-2 | failure | 3.1 分 | 0.1 分 | [#42630330654](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42630330654/attempts/1) |
| 11-09 05:59 | CI | PR | docs/refresh-v0-8-2 | success | 4.8 分 | 0.8 分 | [#42630330465](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42630330465/attempts/1) |
| 11-09 05:59 | 桌面端建置 | PR | docs/refresh-v0-8-2 | success | 8.7 分 | 1.3 分 | [#42630330366](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42630330366/attempts/1) |
| 11-09 05:50 | 伺服器分發包 | PR | chore/github-migration-2 | success | 2.5 分 | 0.1 分 | [#42629078946](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42629078946/attempts/1) |
| 11-09 05:50 | 一鍵安裝腳本 | PR | chore/github-migration-2 | success | 5.1 分 | 2.8 分 | [#42629077646](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42629077646/attempts/1) |
| 11-09 05:50 | 桌面端建置 | PR | chore/github-migration-2 | success | 7.0 分 | 0.1 分 | [#42629077664](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42629077664/attempts/1) |
| 11-09 05:50 | CI | PR | chore/github-migration-2 | success | 8.1 分 | 3.9 分 | [#42629077625](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42629077625/attempts/1) |

