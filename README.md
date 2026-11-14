# CI 運行耗時紀錄

更新：2026-11-14 07:11 America/Los_Angeles（PST，UTC−08:00）。共 219 次運行。

每次 CI、桌面端建置、一鍵安裝腳本、每晚完整測試、發布結束後，由 `.github/workflows/ci-metrics.yml` 追加到 `data/`；本頁由 `tools/ci_metrics.py report` 產生，不要手改。耗時＝第一個工作建立到最後一個工作結束（含排隊）；機器時間＝各工作實際執行的時間總和。
規則與背景見 main 的 `docs/develop/ci.html`。

## 各流程：近 7 天（前 7 天）

| 流程 | 次數 | 通過 | 耗時中位數 | 耗時 P90 | 最長排隊中位數 | 機器時間（Linux／Windows／macOS） |
|---|---|---|---|---|---|---|
| CI | 63（0） | 44（0） | 4.8 分（0.0 分） | 8.3 分（0.0 分） | 0.1 分（0.0 分） | 476／105／0 分（0／0／0 分） |
| 桌面端建置 | 45（0） | 42（0） | 0.2 分（0.0 分） | 6.3 分（0.0 分） | 0.1 分（0.0 分） | 6／68／59 分（0／0／0 分） |
| 伺服器分發包 | 50（0） | 48（0） | 0.2 分（0.0 分） | 2.7 分（0.0 分） | 0.1 分（0.0 分） | 90／0／0 分（0／0／0 分） |
| 一鍵安裝腳本 | 52（0） | 49（0） | 0.2 分（0.0 分） | 5.1 分（0.0 分） | 0.1 分（0.0 分） | 143／182／184 分（0／0／0 分） |
| 每晚完整測試 | 6（0） | 4（0） | 60.0 分（0.0 分） | 61.5 分（0.0 分） | 0.1 分（0.0 分） | 321／308／338 分（0／0／0 分） |
| 發布 | 3（0） | 3（0） | 8.0 分（0.0 分） | 8.2 分（0.0 分） | 0.1 分（0.0 分） | 16／16／34 分（0／0／0 分） |

## 每天的機器時間（分鐘，洛杉磯日期，最近 14 天）

| 日期 | 運行次數 | Linux | Windows | macOS | 合計 |
|---|---|---|---|---|---|
| 2026-11-14 | 15 | 42 | 10 | 5 | 58 |
| 2026-11-13 | 53 | 233 | 157 | 120 | 509 |
| 2026-11-12 | 12 | 117 | 97 | 104 | 318 |
| 2026-11-11 | 41 | 210 | 120 | 96 | 426 |
| 2026-11-10 | 61 | 265 | 177 | 153 | 595 |
| 2026-11-09 | 37 | 186 | 119 | 138 | 442 |

## 最慢的測試檔案（每份報告最近一次，括號是近 7 次的中位數）

### CI · pytest-report-3.12/pytest-report.xml

最近一次：2026-11-14 07:05 America/Los_Angeles（PST，UTC−08:00），合計 516 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 37.4（31.1） | 30 | `apps/server/tests/test_production_api.py` |
| 30.9（25.7） | 29 | `apps/server/tests/test_api.py` |
| 28.7（27.1） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 28.2（27.2） | 21 | `apps/server/tests/test_workflow_api.py` |
| 22.6（20.5） | 11 | `apps/server/tests/test_gitsync.py` |
| 20.4（20.2） | 18 | `apps/cli/tests/test_serve.py` |
| 19.6（19.9） | 20 | `apps/server/tests/test_recorder_api.py` |
| 19.2（19.2） | 13 | `apps/server/tests/test_replay.py` |
| 16.1（16.5） | 8 | `apps/server/tests/test_batches_api.py` |
| 15.8（15.1） | 10 | `apps/server/tests/test_videos.py` |

### CI · pytest-report-3.13/pytest-report.xml

最近一次：2026-11-14 07:05 America/Los_Angeles（PST，UTC−08:00），合計 884 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 114.1（104.8） | 13 | `apps/server/tests/test_portal.py` |
| 47.9（44.5） | 4 | `apps/server/tests/test_replay_flow.py` |
| 47.0（41.2） | 3 | `apps/server/tests/test_workflow_flow.py` |
| 37.2（35.7） | 12 | `packages/rpa_runner/tests/test_debug.py` |
| 35.5（32.0） | 3 | `apps/server/tests/test_remote_worker_flow.py` |
| 34.3（29.6） | 5 | `apps/server/tests/test_production_flow.py` |
| 31.0（31.0） | 30 | `apps/server/tests/test_production_api.py` |
| 26.2（25.4） | 29 | `apps/server/tests/test_api.py` |
| 25.5（25.0） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 24.8（24.8） | 21 | `apps/server/tests/test_workflow_api.py` |

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
| 11-14 07:05 | 一鍵安裝腳本 | PR | feat/m7-wrapup | success | 0.2 分 | 0.1 分 | [#43608294923](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43608294923/attempts/1) |
| 11-14 07:05 | 伺服器分發包 | PR | feat/m7-wrapup | success | 2.4 分 | 0.1 分 | [#43608294878](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43608294878/attempts/1) |
| 11-14 07:05 | CI | PR | feat/m7-wrapup | cancelled | 5.4 分 | 0.1 分 | [#43608294857](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43608294857/attempts/1) |
| 11-14 07:05 | 桌面端建置 | PR | feat/m7-wrapup | cancelled | 5.5 分 | 0.1 分 | [#43608294948](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43608294948/attempts/1) |
| 11-14 07:05 | 桌面端建置 | PR | docs/m7-accepted | success | 0.1 分 | 0.0 分 | [#43608262739](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43608262739/attempts/1) |
| 11-14 07:05 | 一鍵安裝腳本 | PR | docs/m7-accepted | success | 0.2 分 | 0.0 分 | [#43608262870](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43608262870/attempts/1) |
| 11-14 07:05 | CI | PR | docs/m7-accepted | success | 4.8 分 | 0.1 分 | [#43608262735](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43608262735/attempts/1) |
| 11-14 06:23 | 一鍵安裝腳本 | PR | docs/m7-accepted | success | 0.1 分 | 0.0 分 | [#43604615875](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43604615875/attempts/1) |
| 11-14 06:23 | 伺服器分發包 | PR | docs/m7-accepted | success | 0.3 分 | 0.1 分 | [#43604615582](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43604615582/attempts/1) |
| 11-14 06:23 | CI | PR | docs/m7-accepted | failure | 4.8 分 | 0.1 分 | [#43604615660](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43604615660/attempts/1) |
| 11-14 06:06 | CI | 推送 | main | success | 7.4 分 | 0.1 分 | [#43603079118](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43603079118/attempts/1) |
| 11-14 06:06 | 一鍵安裝腳本 | 推送 | main | success | 0.2 分 | 0.0 分 | [#43603079092](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43603079092/attempts/1) |
| 11-14 06:05 | 桌面端建置 | 推送 | main | success | 0.2 分 | 0.0 分 | [#43603058129](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43603058129/attempts/1) |
| 11-14 06:05 | 伺服器分發包 | 推送 | main | success | 0.1 分 | 0.0 分 | [#43603036793](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43603036793/attempts/1) |
| 11-14 06:05 | 桌面端建置 | 推送 | main | cancelled | 0.2 分 | 0.1 分 | [#43603036810](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43603036810/attempts/1) |
| 11-13 21:11 | 伺服器分發包 | PR | feat/m7-batch | success | 0.1 分 | 0.0 分 | [#43560281826](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43560281826/attempts/1) |
| 11-13 21:11 | 桌面端建置 | PR | feat/m7-batch | success | 0.2 分 | 0.1 分 | [#43560281824](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43560281824/attempts/1) |
| 11-13 21:11 | CI | PR | feat/m7-batch | success | 4.8 分 | 0.1 分 | [#43560281785](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43560281785/attempts/1) |
| 11-13 21:04 | 桌面端建置 | PR | feat/m7-subscenario | success | 0.2 分 | 0.1 分 | [#43559700728](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43559700728/attempts/1) |
| 11-13 21:04 | 伺服器分發包 | PR | feat/m7-subscenario | success | 0.3 分 | 0.1 分 | [#43559700694](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43559700694/attempts/1) |
| 11-13 21:04 | CI | PR | feat/m7-subscenario | success | 2.5 分 | 0.1 分 | [#43559700668](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43559700668/attempts/1) |
| 11-13 21:03 | 一鍵安裝腳本 | PR | feat/m7-batch | success | 0.1 分 | 0.0 分 | [#43559649089](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43559649089/attempts/1) |
| 11-13 21:03 | 桌面端建置 | PR | feat/m7-batch | success | 0.2 分 | 0.0 分 | [#43559649075](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43559649075/attempts/1) |
| 11-13 21:03 | 伺服器分發包 | PR | feat/m7-batch | success | 2.5 分 | 0.1 分 | [#43559649143](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43559649143/attempts/1) |
| 11-13 21:03 | CI | PR | feat/m7-batch | failure | 4.0 分 | 0.1 分 | [#43559649158](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43559649158/attempts/1) |
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

