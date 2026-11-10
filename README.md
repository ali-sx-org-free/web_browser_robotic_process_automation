# CI 運行耗時紀錄

更新：2026-11-10 07:47 America/Los_Angeles（PST，UTC−08:00）。共 64 次運行。

每次 CI、桌面端建置、一鍵安裝腳本、每晚完整測試、發布結束後，由 `.github/workflows/ci-metrics.yml` 追加到 `data/`；本頁由 `tools/ci_metrics.py report` 產生，不要手改。耗時＝第一個工作建立到最後一個工作結束（含排隊）；機器時間＝各工作實際執行的時間總和。
規則與背景見 main 的 `docs/develop/ci.html`。

## 各流程：近 7 天（前 7 天）

| 流程 | 次數 | 通過 | 耗時中位數 | 耗時 P90 | 最長排隊中位數 | 機器時間（Linux／Windows／macOS） |
|---|---|---|---|---|---|---|
| CI | 18（0） | 14（0） | 4.4 分（0.0 分） | 8.1 分（0.0 分） | 0.1 分（0.0 分） | 136／21／0 分（0／0／0 分） |
| 桌面端建置 | 14（0） | 13（0） | 0.2 分（0.0 分） | 7.0 分（0.0 分） | 0.1 分（0.0 分） | 2／25／31 分（0／0／0 分） |
| 伺服器分發包 | 14（0） | 14（0） | 0.2 分（0.0 分） | 2.6 分（0.0 分） | 0.1 分（0.0 分） | 15／0／0 分（0／0／0 分） |
| 一鍵安裝腳本 | 16（0） | 14（0） | 0.2 分（0.0 分） | 5.1 分（0.0 分） | 0.1 分（0.0 分） | 33／39／37 分（0／0／0 分） |
| 每晚完整測試 | 1（0） | 0（0） | 64.9 分（0.0 分） | 64.9 分（0.0 分） | 0.1 分（0.0 分） | 60／55／76 分（0／0／0 分） |
| 發布 | 1（0） | 1（0） | 8.0 分（0.0 分） | 8.0 分（0.0 分） | 0.1 分（0.0 分） | 5／6／11 分（0／0／0 分） |

## 每天的機器時間（分鐘，洛杉磯日期，最近 14 天）

| 日期 | 運行次數 | Linux | Windows | macOS | 合計 |
|---|---|---|---|---|---|
| 2026-11-10 | 27 | 65 | 27 | 18 | 109 |
| 2026-11-09 | 37 | 186 | 119 | 138 | 442 |

## 最慢的測試檔案（每份報告最近一次，括號是近 7 次的中位數）

### CI · pytest-report-3.12/pytest-report.xml

最近一次：2026-11-10 07:27 America/Los_Angeles（PST，UTC−08:00），合計 403 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 27.4（19.5） | 27 | `apps/server/tests/test_production_api.py` |
| 27.3（19.5） | 29 | `apps/server/tests/test_api.py` |
| 25.4（24.1） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 20.2（20.0） | 18 | `apps/cli/tests/test_serve.py` |
| 20.1（17.1） | 11 | `apps/server/tests/test_gitsync.py` |
| 17.7（15.9） | 13 | `apps/server/tests/test_replay.py` |
| 17.5（14.2） | 14 | `apps/server/tests/test_workflow_api.py` |
| 16.4（15.6） | 20 | `apps/server/tests/test_recorder_api.py` |
| 14.4（14.2） | 17 | `apps/worker/tests/test_recorder.py` |
| 14.2（12.8） | 10 | `apps/server/tests/test_videos.py` |

### CI · pytest-report-3.13/pytest-report.xml

最近一次：2026-11-10 07:27 America/Los_Angeles（PST，UTC−08:00），合計 310 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 20.1（19.9） | 18 | `apps/cli/tests/test_serve.py` |
| 20.0（20.0） | 27 | `apps/server/tests/test_production_api.py` |
| 18.2（18.2） | 29 | `apps/server/tests/test_api.py` |
| 18.0（18.0） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 13.8（13.9） | 17 | `apps/worker/tests/test_recorder.py` |
| 13.1（13.6） | 14 | `apps/worker/tests/test_gateway.py` |
| 12.4（13.0） | 20 | `apps/server/tests/test_recorder_api.py` |
| 12.3（12.3） | 11 | `apps/server/tests/test_gitsync.py` |
| 11.7（14.2） | 13 | `apps/server/tests/test_replay.py` |
| 11.2（12.8） | 14 | `apps/server/tests/test_workflow_api.py` |

### CI · pytest-report-windows/pytest-report.xml

最近一次：2026-11-10 07:20 America/Los_Angeles（PST，UTC−08:00），合計 708 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 222.7（224.9） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 125.2（125.2） | 10 | `packages\rpa_runner\tests\test_frames.py` |
| 117.2（122.4） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 82.9（87.3） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 48.8（59.3） | 17 | `packages\rpa_runner\tests\test_upload.py` |
| 39.4（35.6） | 2 | `packages\rpa_runner\tests\test_download_browser.py` |
| 38.2（45.1） | 8 | `packages\rpa_runner\tests\test_tabs.py` |
| 23.7（23.7） | 1 | `packages\rpa_runner\tests\test_profiles.py` |
| 4.9（4.5） | 2 | `tests\smoke\test_browser.py` |
| 2.9（3.9） | 1 | `apps\desktop\tests\test_selftest.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-1.xml

最近一次：2026-11-09 13:03 America/Los_Angeles（PST，UTC−08:00），合計 1556 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 179.6（179.6） | 15 | `apps/server/tests/test_portal.py` |
| 132.3（132.3） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 125.0（125.0） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 118.1（118.1） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 111.7（111.7） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 90.6（90.6） | 18 | `apps/cli/tests/test_serve.py` |
| 83.8（83.8） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 80.9（80.9） | 9 | `apps/server/tests/test_production_flow.py` |
| 58.0（58.0） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 44.9（44.9） | 4 | `apps/server/tests/test_replay_flow.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-2.xml

最近一次：2026-11-09 13:03 America/Los_Angeles（PST，UTC−08:00），合計 1059 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 163.8（163.8） | 15 | `apps/server/tests/test_portal.py` |
| 117.8（117.8） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 110.9（110.9） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 109.7（109.7） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 107.4（107.4） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 76.0（76.0） | 9 | `apps/server/tests/test_production_flow.py` |
| 60.0（60.0） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 51.9（51.9） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 43.5（43.5） | 4 | `apps/server/tests/test_replay_flow.py` |
| 31.3（31.3） | 10 | `packages/rpa_runner/tests/test_frames.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-3.xml

最近一次：2026-11-09 13:03 America/Los_Angeles（PST，UTC−08:00），合計 1172 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 179.7（179.7） | 15 | `apps/server/tests/test_portal.py` |
| 134.3（134.3） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 133.9（133.9） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 119.6（119.6） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 119.5（119.5） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 78.7（78.7） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 72.1（72.1） | 9 | `apps/server/tests/test_production_flow.py` |
| 63.0（63.0） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 43.5（43.5） | 4 | `apps/server/tests/test_replay_flow.py` |
| 33.1（33.1） | 3 | `apps/server/tests/test_flow.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.12/pass-1.xml

最近一次：2026-11-09 13:03 America/Los_Angeles（PST，UTC−08:00），合計 1123 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 117.9（117.9） | 15 | `apps/server/tests/test_portal.py` |
| 95.5（95.5） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 84.6（84.6） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 79.2（79.2） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 71.2（71.2） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 56.3（56.3） | 9 | `apps/server/tests/test_production_flow.py` |
| 52.2（52.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 45.2（45.2） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 36.2（36.2） | 4 | `apps/server/tests/test_replay_flow.py` |
| 22.0（22.0） | 4 | `apps/server/tests/test_recorder_flow.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-1.xml

最近一次：2026-11-09 13:03 America/Los_Angeles（PST，UTC−08:00），合計 955 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 105.3（105.3） | 15 | `apps/server/tests/test_portal.py` |
| 88.7（88.7） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 72.1（72.1） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 65.5（65.5） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 62.7（62.7） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 45.9（45.9） | 9 | `apps/server/tests/test_production_flow.py` |
| 43.2（43.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 38.6（38.6） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 34.8（34.8） | 4 | `apps/server/tests/test_replay_flow.py` |
| 19.8（19.8） | 18 | `apps/cli/tests/test_serve.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-2.xml

最近一次：2026-11-09 13:03 America/Los_Angeles（PST，UTC−08:00），合計 681 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 104.8（104.8） | 15 | `apps/server/tests/test_portal.py` |
| 88.8（88.8） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 70.4（70.4） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 64.5（64.5） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 52.9（52.9） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 44.8（44.8） | 9 | `apps/server/tests/test_production_flow.py` |
| 43.2（43.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 38.9（38.9） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 34.3（34.3） | 4 | `apps/server/tests/test_replay_flow.py` |
| 18.0（18.0） | 4 | `apps/server/tests/test_recorder_flow.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-3.xml

最近一次：2026-11-09 13:03 America/Los_Angeles（PST，UTC−08:00），合計 680 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 105.8（105.8） | 15 | `apps/server/tests/test_portal.py` |
| 88.4（88.4） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 70.6（70.6） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 64.9（64.9） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 51.5（51.5） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 44.5（44.5） | 9 | `apps/server/tests/test_production_flow.py` |
| 43.2（43.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 39.5（39.5） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 34.6（34.6） | 4 | `apps/server/tests/test_replay_flow.py` |
| 17.8（17.8） | 4 | `apps/server/tests/test_recorder_flow.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-1.xml

最近一次：2026-11-09 13:03 America/Los_Angeles（PST，UTC−08:00），合計 1367 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 132.1（132.1） | 15 | `apps\server\tests\test_portal.py` |
| 114.4（114.4） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 102.2（102.2） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 101.1（101.1） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 84.9（84.9） | 19 | `packages\rpa_runner\tests\test_debug.py` |
| 67.0（67.0） | 9 | `apps\server\tests\test_production_flow.py` |
| 57.8（57.8） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 55.1（55.1） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 40.4（40.4） | 18 | `packages\rpa_runner\tests\test_profiles.py` |
| 37.6（37.6） | 4 | `apps\server\tests\test_replay_flow.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-2.xml

最近一次：2026-11-09 13:03 America/Los_Angeles（PST，UTC−08:00），合計 924 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 128.1（128.1） | 15 | `apps\server\tests\test_portal.py` |
| 102.1（102.1） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 100.9（100.9） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 99.3（99.3） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 69.1（69.1） | 9 | `apps\server\tests\test_production_flow.py` |
| 69.0（69.0） | 19 | `packages\rpa_runner\tests\test_debug.py` |
| 61.2（61.2） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 52.3（52.3） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 38.1（38.1） | 4 | `apps\server\tests\test_replay_flow.py` |
| 29.0（29.0） | 17 | `packages\rpa_runner\tests\test_upload.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-3.xml

最近一次：2026-11-09 13:03 America/Los_Angeles（PST，UTC−08:00），合計 924 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 129.5（129.5） | 15 | `apps\server\tests\test_portal.py` |
| 103.9（103.9） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 100.5（100.5） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 99.4（99.4） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 70.4（70.4） | 9 | `apps\server\tests\test_production_flow.py` |
| 69.2（69.2） | 19 | `packages\rpa_runner\tests\test_debug.py` |
| 58.2（58.2） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 53.5（53.5） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 38.3（38.3） | 4 | `apps\server\tests\test_replay_flow.py` |
| 27.3（27.3） | 10 | `packages\rpa_runner\tests\test_frames.py` |

## 最近 40 次運行

| 開始（洛杉磯） | 流程 | 觸發 | 分支 | 結果 | 耗時 | 最長排隊 | 運行 |
|---|---|---|---|---|---|---|---|
| 11-10 07:47 | 一鍵安裝腳本 | PR | fix/json-scene-sections | success | 0.2 分 | 0.1 分 | [#42847985514](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42847985514/attempts/1) |
| 11-10 07:44 | 桌面端建置 | 推送 | main | success | 0.2 分 | 0.1 分 | [#42847532709](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42847532709/attempts/1) |
| 11-10 07:44 | 一鍵安裝腳本 | 推送 | main | success | 0.2 分 | 0.1 分 | [#42847532714](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42847532714/attempts/1) |
| 11-10 07:27 | 伺服器分發包 | PR | feat/login-locator-guide | success | 0.2 分 | 0.1 分 | [#42844572816](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42844572816/attempts/1) |
| 11-10 07:27 | 一鍵安裝腳本 | PR | feat/login-locator-guide | success | 0.2 分 | 0.1 分 | [#42844572993](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42844572993/attempts/1) |
| 11-10 07:27 | CI | PR | feat/login-locator-guide | success | 2.5 分 | 0.1 分 | [#42844572800](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42844572800/attempts/1) |
| 11-10 07:20 | 桌面端建置 | PR | feat/login-locator-guide | success | 6.2 分 | 0.1 分 | [#42843257654](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42843257654/attempts/1) |
| 11-10 07:20 | CI | PR | feat/login-locator-guide | success | 5.3 分 | 0.1 分 | [#42843257444](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42843257444/attempts/1) |
| 11-10 07:20 | 伺服器分發包 | PR | feat/login-locator-guide | success | 2.6 分 | 0.1 分 | [#42843257347](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42843257347/attempts/1) |
| 11-10 07:19 | 一鍵安裝腳本 | PR | feat/login-locator-guide | success | 0.3 分 | 0.1 分 | [#42843145781](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42843145781/attempts/1) |
| 11-10 07:19 | 桌面端建置 | PR | feat/login-locator-guide | cancelled | 1.0 分 | 0.1 分 | [#42843145836](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42843145836/attempts/1) |
| 11-10 07:18 | 伺服器分發包 | PR | fix/json-scene-sections | success | 0.1 分 | 0.1 分 | [#42842909226](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42842909226/attempts/1) |
| 11-10 07:18 | 一鍵安裝腳本 | PR | fix/json-scene-sections | success | 0.2 分 | 0.0 分 | [#42842909244](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42842909244/attempts/1) |
| 11-10 07:18 | CI | PR | fix/json-scene-sections | success | 2.2 分 | 0.1 分 | [#42842909367](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42842909367/attempts/1) |
| 11-10 07:08 | 桌面端建置 | PR | fix/json-scene-sections | success | 6.3 分 | 0.1 分 | [#42841329845](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42841329845/attempts/1) |
| 11-10 07:08 | 一鍵安裝腳本 | PR | fix/json-scene-sections | success | 0.2 分 | 0.1 分 | [#42841329610](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42841329610/attempts/1) |
| 11-10 07:08 | 伺服器分發包 | PR | fix/json-scene-sections | success | 2.8 分 | 0.1 分 | [#42841329579](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42841329579/attempts/1) |
| 11-10 07:08 | CI | PR | fix/json-scene-sections | success | 4.4 分 | 0.1 分 | [#42841329725](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42841329725/attempts/1) |
| 11-10 00:53 | 發布 | 推送 | v0.9.0 | success | 8.0 分 | 0.1 分 | [#42786155487](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42786155487/attempts/1) |
| 11-10 00:29 | CI | 推送 | main | failure | 7.0 分 | 0.1 分 | [#42782959381](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42782959381/attempts/1) |
| 11-10 00:28 | 桌面端建置 | 推送 | main | success | 0.1 分 | 0.1 分 | [#42782959614](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42782959614/attempts/1) |
| 11-10 00:25 | 伺服器分發包 | 推送 | main | success | 0.1 分 | 0.1 分 | [#42782485184](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42782485184/attempts/1) |
| 11-10 00:25 | 一鍵安裝腳本 | 推送 | main | success | 0.2 分 | 0.1 分 | [#42782485307](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42782485307/attempts/1) |
| 11-10 00:25 | CI | 推送 | main | cancelled | 3.9 分 | 0.1 分 | [#42782485344](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42782485344/attempts/1) |
| 11-10 00:15 | 伺服器分發包 | PR | chore/release-0.9.0 | success | 0.1 分 | 0.1 分 | [#42781274474](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42781274474/attempts/1) |
| 11-10 00:15 | 桌面端建置 | PR | chore/release-0.9.0 | success | 0.2 分 | 0.1 分 | [#42781274285](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42781274285/attempts/1) |
| 11-10 00:15 | CI | PR | chore/release-0.9.0 | success | 3.3 分 | 0.1 分 | [#42781274275](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42781274275/attempts/1) |
| 11-09 18:40 | 一鍵安裝腳本 | PR | claude/project-thread-j92asl | success | 0.2 分 | 0.1 分 | [#42744340496](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42744340496/attempts/1) |
| 11-09 18:40 | 伺服器分發包 | PR | claude/project-thread-j92asl | success | 0.1 分 | 0.1 分 | [#42744339806](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42744339806/attempts/1) |
| 11-09 18:40 | CI | PR | claude/project-thread-j92asl | success | 1.8 分 | 0.1 分 | [#42744339937](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42744339937/attempts/1) |
| 11-09 18:33 | 桌面端建置 | PR | claude/project-thread-j92asl | success | 0.2 分 | 0.1 分 | [#42743540981](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42743540981/attempts/1) |
| 11-09 18:33 | 一鍵安裝腳本 | PR | claude/project-thread-j92asl | success | 0.2 分 | 0.1 分 | [#42743540953](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42743540953/attempts/1) |
| 11-09 18:33 | CI | PR | claude/project-thread-j92asl | success | 4.6 分 | 0.1 分 | [#42743540767](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42743540767/attempts/1) |
| 11-09 16:56 | 一鍵安裝腳本 | 推送 | main | success | 0.1 分 | 0.1 分 | [#42732096119](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42732096119/attempts/1) |
| 11-09 16:56 | 伺服器分發包 | 推送 | main | success | 0.2 分 | 0.1 分 | [#42732096334](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42732096334/attempts/1) |
| 11-09 16:56 | CI | 推送 | main | success | 2.4 分 | 0.1 分 | [#42732096075](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42732096075/attempts/1) |
| 11-09 16:50 | 桌面端建置 | PR | docs/migration-server-2026-11-09 | success | 0.1 分 | 0.1 分 | [#42731311936](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42731311936/attempts/1) |
| 11-09 16:50 | CI | PR | docs/migration-server-2026-11-09 | success | 3.5 分 | 0.1 分 | [#42731311750](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42731311750/attempts/1) |
| 11-09 16:50 | 一鍵安裝腳本 | PR | docs/migration-server-2026-11-09 | success | 0.2 分 | 0.1 分 | [#42731311556](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42731311556/attempts/1) |
| 11-09 13:33 | 一鍵安裝腳本 | 排程 | main | failure | 26.0 分 | 0.1 分 | [#42703656541](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42703656541/attempts/1) |

