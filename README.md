# CI 運行耗時紀錄

更新：2026-11-13 21:03 America/Los_Angeles（PST，UTC−08:00）。共 194 次運行。

每次 CI、桌面端建置、一鍵安裝腳本、每晚完整測試、發布結束後，由 `.github/workflows/ci-metrics.yml` 追加到 `data/`；本頁由 `tools/ci_metrics.py report` 產生，不要手改。耗時＝第一個工作建立到最後一個工作結束（含排隊）；機器時間＝各工作實際執行的時間總和。
規則與背景見 main 的 `docs/develop/ci.html`。

## 各流程：近 7 天（前 7 天）

| 流程 | 次數 | 通過 | 耗時中位數 | 耗時 P90 | 最長排隊中位數 | 機器時間（Linux／Windows／macOS） |
|---|---|---|---|---|---|---|
| CI | 56（0） | 40（0） | 4.8 分（0.0 分） | 8.7 分（0.0 分） | 0.1 分（0.0 分） | 421／100／0 分（0／0／0 分） |
| 桌面端建置 | 38（0） | 37（0） | 0.2 分（0.0 分） | 6.3 分（0.0 分） | 0.1 分（0.0 分） | 5／62／54 分（0／0／0 分） |
| 伺服器分發包 | 44（0） | 42（0） | 0.2 分（0.0 分） | 2.7 分（0.0 分） | 0.1 分（0.0 分） | 81／0／0 分（0／0／0 分） |
| 一鍵安裝腳本 | 47（0） | 44（0） | 0.2 分（0.0 分） | 5.1 分（0.0 分） | 0.1 分（0.0 分） | 142／182／184 分（0／0／0 分） |
| 每晚完整測試 | 6（0） | 4（0） | 60.0 分（0.0 分） | 61.5 分（0.0 分） | 0.1 分（0.0 分） | 321／308／338 分（0／0／0 分） |
| 發布 | 3（0） | 3（0） | 8.0 分（0.0 分） | 8.2 分（0.0 分） | 0.1 分（0.0 分） | 16／16／34 分（0／0／0 分） |

## 每天的機器時間（分鐘，洛杉磯日期，最近 14 天）

| 日期 | 運行次數 | Linux | Windows | macOS | 合計 |
|---|---|---|---|---|---|
| 2026-11-13 | 43 | 208 | 157 | 120 | 485 |
| 2026-11-12 | 12 | 117 | 97 | 104 | 318 |
| 2026-11-11 | 41 | 210 | 120 | 96 | 426 |
| 2026-11-10 | 61 | 265 | 177 | 153 | 595 |
| 2026-11-09 | 37 | 186 | 119 | 138 | 442 |

## 最慢的測試檔案（每份報告最近一次，括號是近 7 次的中位數）

### CI · pytest-report-3.12/pytest-report.xml

最近一次：2026-11-13 20:58 America/Los_Angeles（PST，UTC−08:00），合計 749 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 27.5（29.2） | 30 | `apps/server/tests/test_production_api.py` |
| 27.5（29.2） | 30 | `apps/server/tests/test_production_api.py` |
| 23.4（24.8） | 29 | `apps/server/tests/test_api.py` |
| 23.4（24.8） | 29 | `apps/server/tests/test_api.py` |
| 23.1（23.1） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 23.1（23.1） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 21.6（22.8） | 21 | `apps/server/tests/test_workflow_api.py` |
| 21.6（22.8） | 21 | `apps/server/tests/test_workflow_api.py` |
| 20.2（20.1） | 18 | `apps/cli/tests/test_serve.py` |
| 20.2（20.1） | 18 | `apps/cli/tests/test_serve.py` |

### CI · pytest-report-3.13/pytest-report.xml

最近一次：2026-11-13 20:58 America/Los_Angeles（PST，UTC−08:00），合計 1622 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 113.9（113.6） | 13 | `apps/server/tests/test_portal.py` |
| 113.9（113.6） | 13 | `apps/server/tests/test_portal.py` |
| 47.4（46.7） | 4 | `apps/server/tests/test_replay_flow.py` |
| 47.4（46.7） | 4 | `apps/server/tests/test_replay_flow.py` |
| 46.2（45.1） | 3 | `apps/server/tests/test_workflow_flow.py` |
| 46.2（45.1） | 3 | `apps/server/tests/test_workflow_flow.py` |
| 38.2（34.8） | 12 | `packages/rpa_runner/tests/test_debug.py` |
| 38.2（34.8） | 12 | `packages/rpa_runner/tests/test_debug.py` |
| 32.6（31.4） | 5 | `apps/server/tests/test_production_flow.py` |
| 32.6（31.4） | 5 | `apps/server/tests/test_production_flow.py` |

### CI · pytest-report-windows/pytest-report.xml

最近一次：2026-11-13 20:58 America/Los_Angeles（PST，UTC−08:00），合計 4440 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 322.3（246.7） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 322.3（246.7） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 322.3（246.7） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 246.7（224.7） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 246.7（224.7） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 246.7（224.7） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 229.1（229.1） | 16 | `packages\rpa_runner\tests\test_call_browser.py` |
| 229.1（229.1） | 16 | `packages\rpa_runner\tests\test_call_browser.py` |
| 229.1（229.1） | 16 | `packages\rpa_runner\tests\test_call_browser.py` |
| 220.7（150.4） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-1.xml

最近一次：2026-11-13 16:53 America/Los_Angeles（PST，UTC−08:00），合計 1578 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 172.2（168.9） | 16 | `apps/server/tests/test_portal.py` |
| 140.1（111.7） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 123.8（123.8） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 122.6（113.2） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 108.7（110.3） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 89.8（89.8） | 18 | `apps/cli/tests/test_serve.py` |
| 87.4（78.8） | 9 | `apps/server/tests/test_production_flow.py` |
| 75.5（75.5） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 65.2（58.0） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 43.1（43.1） | 4 | `apps/server/tests/test_replay_flow.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-2.xml

最近一次：2026-11-13 16:53 America/Los_Angeles（PST，UTC−08:00），合計 988 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 147.1（156.1） | 16 | `apps/server/tests/test_portal.py` |
| 111.2（109.1） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 106.8（106.8） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 99.2（99.2） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 92.6（107.3） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 60.4（63.1） | 9 | `apps/server/tests/test_production_flow.py` |
| 60.1（60.1） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 52.3（51.9） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 40.3（40.4） | 4 | `apps/server/tests/test_replay_flow.py` |
| 29.8（25.0） | 8 | `packages/rpa_runner/tests/test_tabs.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-3.xml

最近一次：2026-11-13 16:53 America/Los_Angeles（PST，UTC−08:00），合計 1020 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 146.5（146.5） | 16 | `apps/server/tests/test_portal.py` |
| 114.6（114.6） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 111.8（111.8） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 100.2（101.3） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 92.5（87.8） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 76.6（76.6） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 59.6（72.1） | 9 | `apps/server/tests/test_production_flow.py` |
| 50.0（50.0） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 43.4（43.4） | 4 | `apps/server/tests/test_replay_flow.py` |
| 30.8（19.6） | 10 | `packages/rpa_runner/tests/test_frames.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.12/pass-1.xml

最近一次：2026-11-13 16:53 America/Los_Angeles（PST，UTC−08:00），合計 1163 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 123.5（117.9） | 16 | `apps/server/tests/test_portal.py` |
| 96.3（95.5） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 84.8（84.2） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 79.4（78.9） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 73.3（70.0） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 57.0（56.3） | 9 | `apps/server/tests/test_production_flow.py` |
| 53.6（52.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 45.2（45.0） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 37.6（36.2） | 4 | `apps/server/tests/test_replay_flow.py` |
| 24.7（20.9） | 30 | `apps/server/tests/test_production_api.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-1.xml

最近一次：2026-11-13 16:53 America/Los_Angeles（PST，UTC−08:00），合計 1102 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 119.1（119.1） | 16 | `apps/server/tests/test_portal.py` |
| 93.9（94.4） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 81.0（83.0） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 75.5（77.5） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 67.4（69.1） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 53.8（54.7） | 9 | `apps/server/tests/test_production_flow.py` |
| 48.2（48.4） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 43.5（44.3） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 35.3（35.8） | 4 | `apps/server/tests/test_replay_flow.py` |
| 23.8（23.0） | 30 | `apps/server/tests/test_production_api.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-2.xml

最近一次：2026-11-13 16:53 America/Los_Angeles（PST，UTC−08:00），合計 777 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 117.0（117.0） | 16 | `apps/server/tests/test_portal.py` |
| 92.9（94.8） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 81.7（81.7） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 72.9（77.7） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 58.6（60.3） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 54.5（54.5） | 9 | `apps/server/tests/test_production_flow.py` |
| 46.5（47.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 42.4（44.2） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 36.6（36.6） | 4 | `apps/server/tests/test_replay_flow.py` |
| 21.3（21.3） | 4 | `apps/server/tests/test_recorder_flow.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-3.xml

最近一次：2026-11-13 16:53 America/Los_Angeles（PST，UTC−08:00），合計 784 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 117.8（117.8） | 16 | `apps/server/tests/test_portal.py` |
| 93.9（94.9） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 81.1（82.1） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 75.0（77.7） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 59.0（60.4） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 53.7（54.4） | 9 | `apps/server/tests/test_production_flow.py` |
| 47.9（48.9） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 43.2（44.2） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 36.6（36.6） | 4 | `apps/server/tests/test_replay_flow.py` |
| 21.1（21.1） | 4 | `apps/server/tests/test_recorder_flow.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-1.xml

最近一次：2026-11-13 16:53 America/Los_Angeles（PST，UTC−08:00），合計 1526 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 148.5（134.4） | 16 | `apps\server\tests\test_portal.py` |
| 124.0（110.4） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 113.2（112.0） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 108.3（101.2） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 99.2（85.5） | 19 | `packages\rpa_runner\tests\test_debug.py` |
| 77.9（70.8） | 9 | `apps\server\tests\test_production_flow.py` |
| 64.1（61.2） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 56.8（53.7） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 39.5（37.9） | 4 | `apps\server\tests\test_replay_flow.py` |
| 36.2（31.1） | 11 | `apps\server\tests\test_gitsync.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-2.xml

最近一次：2026-11-13 16:53 America/Los_Angeles（PST，UTC−08:00），合計 1026 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 146.3（141.1） | 16 | `apps\server\tests\test_portal.py` |
| 108.7（101.6） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 108.6（102.1） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 105.4（100.9） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 76.6（71.1） | 9 | `apps\server\tests\test_production_flow.py` |
| 75.0（72.3） | 19 | `packages\rpa_runner\tests\test_debug.py` |
| 61.0（61.2） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 58.0（55.5） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 38.8（38.3） | 4 | `apps\server\tests\test_replay_flow.py` |
| 30.1（28.1） | 17 | `packages\rpa_runner\tests\test_upload.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-3.xml

最近一次：2026-11-13 16:53 America/Los_Angeles（PST，UTC−08:00），合計 1031 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 146.2（130.9） | 16 | `apps\server\tests\test_portal.py` |
| 110.3（100.6） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 110.2（103.9） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 105.1（100.5） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 76.3（70.2） | 9 | `apps\server\tests\test_production_flow.py` |
| 76.2（70.6） | 19 | `packages\rpa_runner\tests\test_debug.py` |
| 67.6（58.2） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 55.9（53.8） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 40.9（39.0） | 4 | `apps\server\tests\test_replay_flow.py` |
| 28.6（27.2） | 17 | `packages\rpa_runner\tests\test_upload.py` |

## 最近 40 次運行

| 開始（洛杉磯） | 流程 | 觸發 | 分支 | 結果 | 耗時 | 最長排隊 | 運行 |
|---|---|---|---|---|---|---|---|
| 11-13 20:58 | CI | PR | feat/m7-subscenario | success | 4.9 分 | 0.1 分 | [#43558429211 第 2 次](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43558429211/attempts/2) |
| 11-13 20:55 | 一鍵安裝腳本 | PR | feat/m7-batch | success | 0.2 分 | 0.0 分 | [#43559028341](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43559028341/attempts/1) |
| 11-13 20:55 | 伺服器分發包 | PR | feat/m7-batch | success | 2.8 分 | 0.1 分 | [#43559028374](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43559028374/attempts/1) |
| 11-13 20:55 | CI | PR | feat/m7-batch | failure | 6.2 分 | 0.1 分 | [#43559028340](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43559028340/attempts/1) |
| 11-13 20:48 | 一鍵安裝腳本 | PR | feat/m7-subscenario | success | 0.2 分 | 0.1 分 | [#43558429274](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43558429274/attempts/1) |
| 11-13 20:48 | 伺服器分發包 | PR | feat/m7-subscenario | success | 2.6 分 | 0.1 分 | [#43558429246](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43558429246/attempts/1) |
| 11-13 20:48 | 桌面端建置 | PR | feat/m7-subscenario | success | 2.8 分 | 0.1 分 | [#43558429292](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43558429292/attempts/1) |
| 11-13 20:48 | CI | PR | feat/m7-subscenario | failure | 7.6 分 | 0.1 分 | [#43558429211](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43558429211/attempts/1) |
| 11-13 20:20 | 一鍵安裝腳本 | PR | feat/m7-subscenario | success | 0.1 分 | 0.0 分 | [#43556165365](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43556165365/attempts/1) |
| 11-13 20:20 | 伺服器分發包 | PR | feat/m7-subscenario | success | 2.4 分 | 0.1 分 | [#43556165363](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43556165363/attempts/1) |
| 11-13 20:20 | 桌面端建置 | PR | feat/m7-subscenario | success | 5.8 分 | 0.1 分 | [#43556165396](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43556165396/attempts/1) |
| 11-13 20:20 | CI | PR | feat/m7-subscenario | failure | 6.5 分 | 0.1 分 | [#43556165458](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43556165458/attempts/1) |
| 11-13 20:09 | 伺服器分發包 | PR | docs/refresh-v0-9 | success | 0.2 分 | 0.0 分 | [#43555254579](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43555254579/attempts/1) |
| 11-13 20:09 | 桌面端建置 | PR | docs/refresh-v0-9 | success | 0.2 分 | 0.0 分 | [#43555254510](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43555254510/attempts/1) |
| 11-13 20:09 | CI | PR | docs/refresh-v0-9 | success | 3.9 分 | 0.0 分 | [#43555254574](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43555254574/attempts/1) |
| 11-13 18:23 | 一鍵安裝腳本 | PR | docs/refresh-v0-9 | success | 0.1 分 | 0.0 分 | [#43546061701](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43546061701/attempts/1) |
| 11-13 18:23 | 桌面端建置 | PR | docs/refresh-v0-9 | success | 0.2 分 | 0.1 分 | [#43546061617](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43546061617/attempts/1) |
| 11-13 18:23 | CI | PR | docs/refresh-v0-9 | failure | 5.8 分 | 0.0 分 | [#43546061679](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43546061679/attempts/1) |
| 11-13 18:10 | CI | 推送 | main | failure | 7.8 分 | 0.1 分 | [#43544792797](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43544792797/attempts/1) |
| 11-13 18:10 | 桌面端建置 | 推送 | main | success | 0.2 分 | 0.1 分 | [#43544791520](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43544791520/attempts/1) |
| 11-13 18:10 | 伺服器分發包 | 推送 | main | success | 0.2 分 | 0.1 分 | [#43544768336](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43544768336/attempts/1) |
| 11-13 18:10 | CI | 推送 | main | cancelled | 0.5 分 | 0.1 分 | [#43544768126](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43544768126/attempts/1) |
| 11-13 18:06 | 伺服器分發包 | PR | feat/composite-flow | success | 0.3 分 | 0.1 分 | [#43544422397](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43544422397/attempts/1) |
| 11-13 18:06 | 一鍵安裝腳本 | PR | feat/composite-flow | success | 0.1 分 | 0.0 分 | [#43544420660](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43544420660/attempts/1) |
| 11-13 18:06 | CI | PR | feat/composite-flow | success | 2.5 分 | 0.1 分 | [#43544420508](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43544420508/attempts/1) |
| 11-13 18:03 | 伺服器分發包 | PR | feat/composite-flow | success | 0.2 分 | 0.1 分 | [#43544160605](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43544160605/attempts/1) |
| 11-13 18:03 | 桌面端建置 | PR | feat/composite-flow | success | 0.3 分 | 0.0 分 | [#43544160511](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43544160511/attempts/1) |
| 11-13 18:03 | CI | PR | feat/composite-flow | success | 2.1 分 | 0.1 分 | [#43544160508](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43544160508/attempts/1) |
| 11-13 17:57 | 伺服器分發包 | 推送 | main | success | 0.1 分 | 0.1 分 | [#43543609797](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43543609797/attempts/1) |
| 11-13 17:57 | 一鍵安裝腳本 | 推送 | main | success | 0.2 分 | 0.1 分 | [#43543609685](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43543609685/attempts/1) |
| 11-13 17:57 | CI | 推送 | main | success | 7.3 分 | 0.1 分 | [#43543609703](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43543609703/attempts/1) |
| 11-13 17:04 | 一鍵安裝腳本 | 排程 | main | success | 29.8 分 | 0.1 分 | [#43538291256](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43538291256/attempts/1) |
| 11-13 16:53 | 每晚完整測試 | 排程 | main | success | 61.5 分 | 0.1 分 | [#43537147743](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43537147743/attempts/1) |
| 11-13 07:28 | 一鍵安裝腳本 | PR | feat/composite-flow | success | 0.2 分 | 0.1 分 | [#43452895404](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43452895404/attempts/1) |
| 11-13 07:28 | 伺服器分發包 | PR | feat/composite-flow | success | 2.8 分 | 0.1 分 | [#43452895722](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43452895722/attempts/1) |
| 11-13 07:28 | 桌面端建置 | PR | feat/composite-flow | success | 3.3 分 | 0.1 分 | [#43452895372](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43452895372/attempts/1) |
| 11-13 07:28 | CI | PR | feat/composite-flow | success | 5.4 分 | 0.1 分 | [#43452895789](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43452895789/attempts/1) |
| 11-13 07:21 | CI | PR | feat/m7-flow-control | success | 5.6 分 | 0.1 分 | [#43451778319](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43451778319/attempts/1) |
| 11-13 07:21 | 桌面端建置 | PR | feat/m7-flow-control | success | 6.0 分 | 0.1 分 | [#43451778322](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43451778322/attempts/1) |
| 11-13 07:21 | 伺服器分發包 | PR | feat/m7-flow-control | success | 2.5 分 | 0.1 分 | [#43451778254](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43451778254/attempts/1) |

