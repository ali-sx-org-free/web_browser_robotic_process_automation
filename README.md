# CI 運行耗時紀錄

更新：2026-11-20 18:41 America/Los_Angeles（PST，UTC−08:00）。共 330 次運行。

每次 CI、桌面端建置、一鍵安裝腳本、每晚完整測試、發布結束後，由 `.github/workflows/ci-metrics.yml` 追加到 `data/`；本頁由 `tools/ci_metrics.py report` 產生，不要手改。耗時＝第一個工作建立到最後一個工作結束（含排隊）；機器時間＝各工作實際執行的時間總和。
規則與背景見 main 的 `docs/develop/ci.html`。

## 各流程：近 7 天（前 7 天）

| 流程 | 次數 | 通過 | 耗時中位數 | 耗時 P90 | 最長排隊中位數 | 機器時間（Linux／Windows／macOS） |
|---|---|---|---|---|---|---|
| CI | 42（51） | 25（38） | 4.8 分（4.7 分） | 8.0 分（8.7 分） | 0.1 分（0.1 分） | 314／56／0 分（387／76／0 分） |
| 桌面端建置 | 30（35） | 26（34） | 0.2 分（0.2 分） | 5.8 分（6.3 分） | 0.1 分（0.1 分） | 4／37／53 分（4／55／48 分） |
| 伺服器分發包 | 34（40） | 31（38） | 0.3 分（0.2 分） | 2.8 分（2.7 分） | 0.1 分（0.1 分） | 70／0／0 分（67／0／0 分） |
| 一鍵安裝腳本 | 35（44） | 34（41） | 0.2 分（0.2 分） | 32.8 分（26.0 分） | 0.1 分（0.1 分） | 235／304／298 分（142／182／184 分） |
| 每晚完整測試 | 8（6） | 7（4） | 73.3 分（60.0 分） | 78.5 分（61.5 分） | 0.1 分（0.1 分） | 515／473／598 分（321／308／338 分） |
| 發布 | 2（3） | 2（3） | 8.1 分（8.0 分） | 8.3 分（8.2 分） | 0.1 分（0.1 分） | 11／11／23 分（16／16／34 分） |

## 每天的機器時間（分鐘，洛杉磯日期，最近 14 天）

| 日期 | 運行次數 | Linux | Windows | macOS | 合計 |
|---|---|---|---|---|---|
| 2026-11-20 | 26 | 183 | 114 | 141 | 439 |
| 2026-11-19 | 2 | 104 | 110 | 127 | 342 |
| 2026-11-18 | 2 | 112 | 113 | 131 | 356 |
| 2026-11-17 | 2 | 116 | 111 | 133 | 361 |
| 2026-11-16 | 16 | 152 | 115 | 138 | 405 |
| 2026-11-15 | 2 | 98 | 113 | 123 | 335 |
| 2026-11-14 | 76 | 310 | 172 | 171 | 652 |
| 2026-11-13 | 53 | 233 | 157 | 120 | 509 |
| 2026-11-12 | 12 | 117 | 97 | 104 | 318 |
| 2026-11-11 | 41 | 210 | 120 | 96 | 426 |
| 2026-11-10 | 61 | 265 | 177 | 153 | 595 |
| 2026-11-09 | 37 | 186 | 119 | 138 | 442 |

## 最慢的測試檔案（每份報告最近一次，括號是近 7 次的中位數）

### CI · pytest-report-3.12/pytest-report.xml

最近一次：2026-11-20 08:14 America/Los_Angeles（PST，UTC−08:00），合計 476 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 29.6（29.6） | 30 | `apps/server/tests/test_production_api.py` |
| 25.4（25.4） | 29 | `apps/server/tests/test_api.py` |
| 23.8（24.5） | 21 | `apps/server/tests/test_workflow_api.py` |
| 23.2（23.2） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 21.1（21.1） | 11 | `apps/server/tests/test_gitsync.py` |
| 20.6（20.5） | 18 | `apps/cli/tests/test_serve.py` |
| 18.1（18.1） | 20 | `apps/server/tests/test_recorder_api.py` |
| 17.6（18.5） | 13 | `apps/server/tests/test_replay.py` |
| 15.9（14.8） | 10 | `apps/server/tests/test_videos.py` |
| 15.9（15.6） | 8 | `apps/server/tests/test_batches_api.py` |

### CI · pytest-report-3.13/pytest-report.xml

最近一次：2026-11-20 08:14 America/Los_Angeles（PST，UTC−08:00），合計 438 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 25.3（26.5） | 30 | `apps/server/tests/test_production_api.py` |
| 23.2（23.2） | 21 | `apps/server/tests/test_workflow_api.py` |
| 21.9（21.9） | 29 | `apps/server/tests/test_api.py` |
| 19.9（22.3） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 19.7（19.8） | 18 | `apps/cli/tests/test_serve.py` |
| 18.9（18.9） | 11 | `apps/server/tests/test_gitsync.py` |
| 17.3（17.3） | 20 | `apps/server/tests/test_recorder_api.py` |
| 14.8（14.8） | 10 | `apps/server/tests/test_videos.py` |
| 14.6（13.9） | 17 | `apps/worker/tests/test_recorder.py` |
| 14.6（14.6） | 8 | `apps/server/tests/test_batches_api.py` |

### CI · pytest-report-windows/pytest-report.xml

最近一次：2026-11-14 16:58 America/Los_Angeles（PST，UTC−08:00），合計 990 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 215.1（254.8） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 168.5（194.4） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |
| 153.7（215.1） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 129.5（158.6） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 85.8（117.4） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 64.9（75.1） | 10 | `packages\rpa_runner\tests\test_frames.py` |
| 58.0（73.3） | 17 | `packages\rpa_runner\tests\test_upload.py` |
| 47.0（47.1） | 8 | `packages\rpa_runner\tests\test_tabs.py` |
| 33.9（40.0） | 2 | `packages\rpa_runner\tests\test_download_browser.py` |
| 22.9（30.8） | 1 | `packages\rpa_runner\tests\test_profiles.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-1.xml

最近一次：2026-11-20 17:32 America/Los_Angeles（PST，UTC−08:00），合計 1736 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 154.2（171.6） | 16 | `apps/server/tests/test_portal.py` |
| 111.7（118.1） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 111.2（111.2） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 104.2（120.3） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 100.9（72.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 97.3（118.3） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 91.1（78.8） | 9 | `apps/server/tests/test_production_flow.py` |
| 89.8（90.4） | 18 | `apps/cli/tests/test_serve.py` |
| 84.7（88.5） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 79.5（108.0） | 23 | `packages/rpa_runner/tests/test_debug.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-2.xml

最近一次：2026-11-20 17:32 America/Los_Angeles（PST，UTC−08:00），合計 1146 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 159.0（179.7） | 16 | `apps/server/tests/test_portal.py` |
| 105.0（116.4） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 102.5（120.5） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 93.9（93.9） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 86.3（93.6） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 83.4（106.1） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 69.2（72.7） | 9 | `apps/server/tests/test_production_flow.py` |
| 67.3（82.4） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 63.7（72.7） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 43.3（56.8） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-3.xml

最近一次：2026-11-20 17:32 America/Los_Angeles（PST，UTC−08:00），合計 1181 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 153.8（171.2） | 16 | `apps/server/tests/test_portal.py` |
| 120.2（113.1） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 108.4（108.4） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 89.0（98.4） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 85.4（90.7） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 82.5（74.4） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 79.1（87.5） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 71.3（85.4） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 67.0（84.9） | 9 | `apps/server/tests/test_production_flow.py` |
| 49.3（49.3） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.12/pass-1.xml

最近一次：2026-11-20 17:32 America/Los_Angeles（PST，UTC−08:00），合計 1341 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 121.9（112.7） | 16 | `apps/server/tests/test_portal.py` |
| 93.7（90.1） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 83.2（76.9） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 75.7（66.4） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 66.8（58.7） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 62.1（56.7） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 58.0（47.5） | 9 | `apps/server/tests/test_production_flow.py` |
| 49.9（45.9） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 49.0（48.8） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 43.7（39.6） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-1.xml

最近一次：2026-11-20 17:32 America/Los_Angeles（PST，UTC−08:00），合計 1120 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 106.1（113.8） | 16 | `apps/server/tests/test_portal.py` |
| 87.5（89.9） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 68.7（77.0） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 61.2（69.0） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 55.7（61.3） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 51.8（55.9） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 47.1（47.1） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 45.5（51.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 43.8（49.5） | 9 | `apps/server/tests/test_production_flow.py` |
| 37.1（40.0） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-2.xml

最近一次：2026-11-20 17:32 America/Los_Angeles（PST，UTC−08:00），合計 774 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 105.8（110.9） | 16 | `apps/server/tests/test_portal.py` |
| 87.2（90.2） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 70.2（73.9） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 60.3（68.4） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 55.6（62.1） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 51.3（57.4） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 43.8（48.4） | 9 | `apps/server/tests/test_production_flow.py` |
| 43.1（46.1） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 37.2（40.9） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 34.1（35.3） | 4 | `apps/server/tests/test_replay_flow.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-3.xml

最近一次：2026-11-20 17:32 America/Los_Angeles（PST，UTC−08:00），合計 776 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 103.8（110.7） | 16 | `apps/server/tests/test_portal.py` |
| 87.4（90.2） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 68.2（74.2） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 61.3（66.6） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 56.2（59.5） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 52.3（55.6） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 44.8（44.8） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 43.6（47.4） | 9 | `apps/server/tests/test_production_flow.py` |
| 37.4（39.9） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 34.6（35.7） | 4 | `apps/server/tests/test_replay_flow.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-1.xml

最近一次：2026-11-20 17:32 America/Los_Angeles（PST，UTC−08:00），合計 1512 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 123.0（136.5） | 16 | `apps\server\tests\test_portal.py` |
| 96.6（101.5） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 92.0（105.8） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 87.4（111.1） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 71.8（81.7） | 23 | `packages\rpa_runner\tests\test_debug.py` |
| 68.1（78.8） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 67.2（74.5） | 9 | `apps\server\tests\test_production_flow.py` |
| 62.7（63.1） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 56.7（65.4） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |
| 50.4（57.3） | 20 | `packages\rpa_runner\tests\test_run.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-2.xml

最近一次：2026-11-20 17:32 America/Los_Angeles（PST，UTC−08:00），合計 1002 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 123.8（140.5） | 16 | `apps\server\tests\test_portal.py` |
| 96.5（100.5） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 90.5（105.2） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 88.1（96.6） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 71.5（82.8） | 23 | `packages\rpa_runner\tests\test_debug.py` |
| 66.8（76.3） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 60.9（70.0） | 9 | `apps\server\tests\test_production_flow.py` |
| 55.9（60.9） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 49.7（55.0） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 42.8（47.5） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-3.xml

最近一次：2026-11-20 17:32 America/Los_Angeles（PST，UTC−08:00），合計 1022 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 124.4（141.4） | 16 | `apps\server\tests\test_portal.py` |
| 97.4（103.7） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 89.7（104.6） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 89.0（104.7） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 76.1（77.7） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 70.1（83.3） | 23 | `packages\rpa_runner\tests\test_debug.py` |
| 63.7（69.9） | 9 | `apps\server\tests\test_production_flow.py` |
| 60.7（60.7） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 51.4（56.0） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 42.4（48.6） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |

## 最近 40 次運行

| 開始（洛杉磯） | 流程 | 觸發 | 分支 | 結果 | 耗時 | 最長排隊 | 運行 |
|---|---|---|---|---|---|---|---|
| 11-20 17:46 | 一鍵安裝腳本 | 排程 | main | success | 32.7 分 | 0.1 分 | [#44852128665](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44852128665/attempts/1) |
| 11-20 17:32 | 每晚完整測試 | 排程 | main | success | 69.3 分 | 0.1 分 | [#44850749504](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44850749504/attempts/1) |
| 11-20 08:14 | 伺服器分發包 | 推送 | main | success | 0.2 分 | 0.0 分 | [#44771297098](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44771297098/attempts/1) |
| 11-20 08:14 | 一鍵安裝腳本 | 推送 | main | success | 0.2 分 | 0.1 分 | [#44771296444](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44771296444/attempts/1) |
| 11-20 08:14 | CI | 推送 | main | success | 2.6 分 | 0.1 分 | [#44771296435](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44771296435/attempts/1) |
| 11-20 06:19 | 伺服器分發包 | PR | m14/expected-revision | success | 0.1 分 | 0.1 分 | [#44752382719](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44752382719/attempts/1) |
| 11-20 06:19 | 桌面端建置 | PR | m14/expected-revision | success | 0.2 分 | 0.1 分 | [#44752382641](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44752382641/attempts/1) |
| 11-20 06:19 | CI | PR | m14/expected-revision | success | 5.2 分 | 0.1 分 | [#44752382681](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44752382681/attempts/1) |
| 11-20 06:08 | 發布 | 推送 | v0.10.1 | success | 8.3 分 | 0.1 分 | [#44750615230](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44750615230/attempts/1) |
| 11-20 06:08 | 伺服器分發包 | 推送 | main | success | 0.1 分 | 0.1 分 | [#44750575305](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44750575305/attempts/1) |
| 11-20 06:08 | 桌面端建置 | 推送 | main | success | 0.3 分 | 0.1 分 | [#44750574482](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44750574482/attempts/1) |
| 11-20 06:08 | CI | 推送 | main | success | 8.6 分 | 0.1 分 | [#44750575277](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44750575277/attempts/1) |
| 11-20 05:55 | 伺服器分發包 | 手動 | chore/release-0.10.1 | success | 3.7 分 | 0.1 分 | [#44748630657](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44748630657/attempts/1) |
| 11-20 05:55 | 桌面端建置 | 手動 | chore/release-0.10.1 | success | 6.4 分 | 0.1 分 | [#44748623130](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44748623130/attempts/1) |
| 11-20 05:55 | 伺服器分發包 | PR | chore/release-0.10.1 | success | 0.1 分 | 0.0 分 | [#44748617026](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44748617026/attempts/1) |
| 11-20 05:55 | 一鍵安裝腳本 | PR | chore/release-0.10.1 | success | 0.2 分 | 0.1 分 | [#44748617341](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44748617341/attempts/1) |
| 11-20 05:55 | CI | PR | chore/release-0.10.1 | success | 4.4 分 | 0.0 分 | [#44748617034](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44748617034/attempts/1) |
| 11-20 05:50 | CI | PR | m14/expected-revision | success | 4.3 分 | 0.1 分 | [#44747159524](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44747159524/attempts/1) |
| 11-20 05:50 | 桌面端建置 | 推送 | main | success | 0.1 分 | 0.0 分 | [#44747872971](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44747872971/attempts/1) |
| 11-20 05:50 | CI | 推送 | main | success | 10.7 分 | 0.1 分 | [#44747872987](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44747872987/attempts/1) |
| 11-20 05:45 | 伺服器分發包 | PR | m14/expected-revision | success | 2.7 分 | 0.1 分 | [#44747159573](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44747159573/attempts/1) |
| 11-20 05:45 | 一鍵安裝腳本 | PR | m14/expected-revision | success | 0.3 分 | 0.1 分 | [#44747159432](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44747159432/attempts/1) |
| 11-20 05:45 | 桌面端建置 | PR | m14/expected-revision | success | 0.2 分 | 0.1 分 | [#44747159403](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44747159403/attempts/1) |
| 11-20 05:45 | CI | PR | m14/expected-revision | cancelled | 5.2 分 | 0.1 分 | [#44747124682](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44747124682/attempts/1) |
| 11-20 05:45 | 桌面端建置 | PR | m14/expected-revision | success | 0.2 分 | 0.1 分 | [#44747124672](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44747124672/attempts/1) |
| 11-20 05:45 | 伺服器分發包 | PR | m14/expected-revision | cancelled | 0.2 分 | 0.1 分 | [#44747124873](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44747124873/attempts/1) |
| 11-19 17:54 | 一鍵安裝腳本 | 排程 | main | success | 33.5 分 | 0.1 分 | [#44656964332](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44656964332/attempts/1) |
| 11-19 17:46 | 每晚完整測試 | 排程 | main | success | 75.7 分 | 0.1 分 | [#44656057698](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44656057698/attempts/1) |
| 11-18 18:01 | 一鍵安裝腳本 | 排程 | main | success | 38.7 分 | 0.1 分 | [#44441238925](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44441238925/attempts/1) |
| 11-18 17:53 | 每晚完整測試 | 排程 | main | success | 75.9 分 | 0.1 分 | [#44440221457](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44440221457/attempts/1) |
| 11-17 18:37 | 一鍵安裝腳本 | 排程 | main | success | 34.8 分 | 0.1 分 | [#44224618237](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44224618237/attempts/1) |
| 11-17 18:26 | 每晚完整測試 | 排程 | main | success | 82.4 分 | 0.1 分 | [#44223299599](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44223299599/attempts/1) |
| 11-16 22:00 | 發布 | 推送 | v0.10.0 | success | 7.8 分 | 0.1 分 | [#44028056829](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44028056829/attempts/1) |
| 11-16 21:54 | 一鍵安裝腳本 | 推送 | main | success | 0.2 分 | 0.0 分 | [#44027323838](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44027323838/attempts/1) |
| 11-16 21:54 | 桌面端建置 | 推送 | main | success | 0.1 分 | 0.1 分 | [#44027323798](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44027323798/attempts/1) |
| 11-16 21:54 | CI | 推送 | main | success | 8.8 分 | 0.1 分 | [#44027323816](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44027323816/attempts/1) |
| 11-16 20:47 | 桌面端建置 | PR | chore/release-0.10.0 | success | 0.1 分 | 0.0 分 | [#44019625800](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44019625800/attempts/1) |
| 11-16 20:47 | 一鍵安裝腳本 | PR | chore/release-0.10.0 | success | 0.2 分 | 0.0 分 | [#44019625786](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44019625786/attempts/1) |
| 11-16 20:47 | CI | PR | chore/release-0.10.0 | success | 2.7 分 | 0.1 分 | [#44019625829](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44019625829/attempts/1) |
| 11-16 20:41 | 伺服器分發包 | PR | chore/release-0.10.0 | success | 0.1 分 | 0.0 分 | [#44018922488](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44018922488/attempts/1) |

