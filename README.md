# CI 運行耗時紀錄

更新：2026-11-27 19:57 America/Los_Angeles（PST，UTC−08:00）。共 456 次運行。

每次 CI、桌面端建置、一鍵安裝腳本、每晚完整測試、發布結束後，由 `.github/workflows/ci-metrics.yml` 追加到 `data/`；本頁由 `tools/ci_metrics.py report` 產生，不要手改。耗時＝第一個工作建立到最後一個工作結束（含排隊）；機器時間＝各工作實際執行的時間總和。
規則與背景見 main 的 `docs/develop/ci.html`。

## 各流程：近 7 天（前 7 天）

| 流程 | 次數 | 通過 | 耗時中位數 | 耗時 P90 | 最長排隊中位數 | 機器時間（Linux／Windows／macOS） |
|---|---|---|---|---|---|---|
| CI | 29（42） | 23（25） | 5.6 分（4.8 分） | 9.1 分（8.0 分） | 0.1 分（0.1 分） | 260／57／0 分（314／56／0 分） |
| 桌面端建置 | 23（30） | 22（26） | 0.2 分（0.2 分） | 6.7 分（5.8 分） | 0.1 分（0.1 分） | 3／33／39 分（4／37／53 分） |
| 伺服器分發包 | 30（34） | 29（31） | 1.5 分（0.3 分） | 2.8 分（2.8 分） | 0.1 分（0.1 分） | 75／0／0 分（70／0／0 分） |
| 一鍵安裝腳本 | 30（35） | 28（34） | 0.2 分（0.2 分） | 33.0 分（32.8 分） | 0.1 分（0.1 分） | 256／340／345 分（235／304／298 分） |
| 每晚完整測試 | 13（8） | 11（7） | 72.8 分（73.3 分） | 76.3 分（78.5 分） | 0.1 分（0.1 分） | 677／611／634 分（515／473／598 分） |
| 發布 | 1（2） | 1（2） | 7.0 分（8.1 分） | 7.0 分（8.3 分） | 0.1 分（0.1 分） | 5／5／11 分（11／11／23 分） |

## 每天的機器時間（分鐘，洛杉磯日期，最近 14 天）

| 日期 | 運行次數 | Linux | Windows | macOS | 合計 |
|---|---|---|---|---|---|
| 2026-11-27 | 74 | 287 | 120 | 149 | 556 |
| 2026-11-26 | 23 | 192 | 159 | 139 | 490 |
| 2026-11-25 | 15 | 295 | 256 | 127 | 678 |
| 2026-11-24 | 2 | 95 | 104 | 123 | 323 |
| 2026-11-23 | 7 | 198 | 180 | 231 | 609 |
| 2026-11-22 | 2 | 101 | 108 | 127 | 335 |
| 2026-11-21 | 3 | 109 | 119 | 133 | 360 |
| 2026-11-20 | 26 | 183 | 114 | 141 | 439 |
| 2026-11-19 | 2 | 104 | 110 | 127 | 342 |
| 2026-11-18 | 2 | 112 | 113 | 131 | 356 |
| 2026-11-17 | 2 | 116 | 111 | 133 | 361 |
| 2026-11-16 | 16 | 152 | 115 | 138 | 405 |
| 2026-11-15 | 2 | 98 | 113 | 123 | 335 |
| 2026-11-14 | 76 | 310 | 172 | 171 | 652 |
| 2026-11-13 | 25 | 74 | 32 | 6 | 111 |

## 最慢的測試檔案（每份報告最近一次，括號是近 7 次的中位數）

### CI · pytest-report-3.12/pytest-report.xml

最近一次：2026-11-27 05:43 America/Los_Angeles（PST，UTC−08:00），合計 417 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 25.6（33.9） | 30 | `apps/server/tests/test_production_api.py` |
| 21.1（29.4） | 29 | `apps/server/tests/test_api.py` |
| 21.0（28.9） | 21 | `apps/server/tests/test_workflow_api.py` |
| 20.3（20.3） | 18 | `apps/cli/tests/test_serve.py` |
| 20.1（27.3） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 16.6（19.2） | 20 | `apps/server/tests/test_recorder_api.py` |
| 16.6（22.2） | 12 | `apps/server/tests/test_gitsync.py` |
| 14.6（14.6） | 15 | `apps/worker/tests/test_gateway.py` |
| 13.8（13.9） | 17 | `apps/worker/tests/test_recorder.py` |
| 12.1（18.0） | 13 | `apps/server/tests/test_replay.py` |

### CI · pytest-report-3.13/pytest-report.xml

最近一次：2026-11-27 05:43 America/Los_Angeles（PST，UTC−08:00），合計 989 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 112.2（98.1） | 13 | `apps/server/tests/test_portal.py` |
| 50.1（44.2） | 3 | `apps/server/tests/test_workflow_flow.py` |
| 47.6（43.7） | 4 | `apps/server/tests/test_replay_flow.py` |
| 36.8（31.6） | 30 | `apps/server/tests/test_production_api.py` |
| 35.2（32.0） | 12 | `packages/rpa_runner/tests/test_debug.py` |
| 32.9（26.1） | 3 | `apps/server/tests/test_remote_worker_flow.py` |
| 32.4（26.1） | 21 | `apps/server/tests/test_workflow_api.py` |
| 31.7（26.8） | 29 | `apps/server/tests/test_api.py` |
| 31.1（25.0） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 30.4（26.1） | 5 | `apps/server/tests/test_production_flow.py` |

### CI · pytest-report-windows/pytest-report.xml

最近一次：2026-11-27 05:03 America/Los_Angeles（PST，UTC−08:00），合計 1124 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 236.2（231.8） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 196.7（185.0） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 161.7（159.2） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |
| 137.8（136.8） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 135.9（98.7） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 68.8（68.8） | 17 | `packages\rpa_runner\tests\test_upload.py` |
| 58.3（56.0） | 8 | `packages\rpa_runner\tests\test_tabs.py` |
| 51.5（53.4） | 10 | `packages\rpa_runner\tests\test_frames.py` |
| 40.6（34.3） | 2 | `packages\rpa_runner\tests\test_download_browser.py` |
| 25.4（25.0） | 1 | `packages\rpa_runner\tests\test_profiles.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-1.xml

最近一次：2026-11-27 03:00 America/Los_Angeles（PST，UTC−08:00），合計 1329 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 134.3（186.9） | 16 | `apps/server/tests/test_portal.py` |
| 96.0（119.0） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 89.9（90.7） | 18 | `apps/cli/tests/test_serve.py` |
| 86.1（121.7） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 78.7（118.1） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 68.3（133.3） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 59.6（92.2） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 59.6（93.9） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 51.8（80.1） | 9 | `apps/server/tests/test_production_flow.py` |
| 50.7（69.9） | 5 | `apps/server/tests/test_remote_worker_flow.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-2.xml

最近一次：2026-11-26 18:51 America/Los_Angeles（PST，UTC−08:00），合計 1231 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 162.8（167.8） | 16 | `apps/server/tests/test_portal.py` |
| 110.0（110.0） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 109.1（114.9） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 96.9（96.9） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 93.4（78.2） | 9 | `apps/server/tests/test_production_flow.py` |
| 85.1（79.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 81.0（81.0） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 76.5（94.6） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 72.6（86.5） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 55.2（53.5） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-3.xml

最近一次：2026-11-26 18:51 America/Los_Angeles（PST，UTC−08:00），合計 1278 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 157.4（169.1） | 16 | `apps/server/tests/test_portal.py` |
| 127.7（124.3） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 118.1（105.5） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 110.6（110.6） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 95.7（89.2） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 84.0（84.0） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 83.5（91.1） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 73.7（81.8） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 71.2（88.4） | 9 | `apps/server/tests/test_production_flow.py` |
| 57.9（52.5） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.12/pass-1.xml

最近一次：2026-11-26 18:51 America/Los_Angeles（PST，UTC−08:00），合計 1349 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 122.0（107.8） | 16 | `apps/server/tests/test_portal.py` |
| 95.5（87.7） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 84.5（70.6） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 78.3（63.4） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 68.4（58.3） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 63.5（54.8） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 57.5（47.3） | 9 | `apps/server/tests/test_production_flow.py` |
| 50.8（44.9） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 49.9（42.9） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 44.6（38.2） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-1.xml

最近一次：2026-11-26 18:51 America/Los_Angeles（PST，UTC−08:00），合計 1334 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 121.8（119.8） | 16 | `apps/server/tests/test_portal.py` |
| 94.2（93.7） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 82.4（81.0） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 76.2（75.4） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 66.6（65.6） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 61.6（62.4） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 56.0（55.0） | 9 | `apps/server/tests/test_production_flow.py` |
| 50.3（49.3） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 48.1（47.4） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 43.4（43.0） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-2.xml

最近一次：2026-11-26 18:51 America/Los_Angeles（PST，UTC−08:00），合計 909 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 119.8（117.4） | 16 | `apps/server/tests/test_portal.py` |
| 94.3（93.2） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 82.2（79.9） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 74.9（72.7） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 66.3（64.2） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 60.9（60.8） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 55.1（54.5） | 9 | `apps/server/tests/test_production_flow.py` |
| 49.8（53.0） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 42.8（42.0） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 37.6（36.3） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-3.xml

最近一次：2026-11-26 18:51 America/Los_Angeles（PST，UTC−08:00），合計 910 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 120.4（117.5） | 16 | `apps/server/tests/test_portal.py` |
| 94.2（92.7） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 82.1（80.0） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 74.7（72.5） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 66.4（65.1） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 61.1（62.2） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 55.1（53.0） | 9 | `apps/server/tests/test_production_flow.py` |
| 47.5（51.5） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 43.5（42.8） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 37.6（36.0） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-1.xml

最近一次：2026-11-26 18:51 America/Los_Angeles（PST，UTC−08:00），合計 1955 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 156.8（134.0） | 16 | `apps\server\tests\test_portal.py` |
| 153.2（104.4） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 112.8（94.0） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 109.9（101.0） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 92.0（78.0） | 23 | `packages\rpa_runner\tests\test_debug.py` |
| 85.2（79.1） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 83.9（69.0） | 9 | `apps\server\tests\test_production_flow.py` |
| 76.0（72.1） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |
| 73.1（62.6） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 58.9（60.0） | 20 | `packages\rpa_runner\tests\test_run.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-2.xml

最近一次：2026-11-26 18:51 America/Los_Angeles（PST，UTC−08:00），合計 1253 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 152.3（128.2） | 16 | `apps\server\tests\test_portal.py` |
| 120.2（100.2） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 112.9（95.1） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 106.7（99.7） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 89.7（76.7） | 23 | `packages\rpa_runner\tests\test_debug.py` |
| 85.6（76.4） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 80.8（66.6） | 9 | `apps\server\tests\test_production_flow.py` |
| 69.0（56.6） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 59.8（53.7） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 58.0（47.4） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-3.xml

最近一次：2026-11-26 18:51 America/Los_Angeles（PST，UTC−08:00），合計 1274 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 153.3（135.9） | 16 | `apps\server\tests\test_portal.py` |
| 121.3（107.6） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 112.1（95.1） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 108.3（99.2） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 93.4（75.0） | 23 | `packages\rpa_runner\tests\test_debug.py` |
| 90.8（74.2） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 81.5（67.6） | 9 | `apps\server\tests\test_production_flow.py` |
| 68.6（61.1） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 61.1（47.5） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |
| 59.9（51.9） | 20 | `packages\rpa_runner\tests\test_run.py` |

## 最近 40 次運行

| 開始（洛杉磯） | 流程 | 觸發 | 分支 | 結果 | 耗時 | 最長排隊 | 運行 |
|---|---|---|---|---|---|---|---|
| 11-27 19:57 | 伺服器分發包 | 推送 | main | success | 0.1 分 | 0.0 分 | [#46105262637](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46105262637/attempts/1) |
| 11-27 18:57 | 一鍵安裝腳本 | 排程 | main | failure | 33.4 分 | 0.1 分 | [#46100551790](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46100551790/attempts/1) |
| 11-27 05:43 | CI | PR | claude/project-thread-70yx5u | success | 5.6 分 | 0.1 分 | [#46009524897](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46009524897/attempts/1) |
| 11-27 05:43 | 伺服器分發包 | PR | claude/project-thread-70yx5u | success | 2.9 分 | 0.2 分 | [#46009524765](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46009524765/attempts/1) |
| 11-27 05:43 | 一鍵安裝腳本 | PR | claude/project-thread-70yx5u | success | 0.2 分 | 0.0 分 | [#46009524640](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46009524640/attempts/1) |
| 11-27 05:43 | 一鍵安裝腳本 | PR | claude/project-thread-70yx5u | success | 0.2 分 | 0.1 分 | [#46009499723](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46009499723/attempts/1) |
| 11-27 05:30 | 桌面端建置 | PR | claude/project-thread-70yx5u | success | 0.2 分 | 0.1 分 | [#46007636226](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46007636226/attempts/1) |
| 11-27 05:30 | 一鍵安裝腳本 | PR | claude/project-thread-70yx5u | success | 0.2 分 | 0.1 分 | [#46007636262](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46007636262/attempts/1) |
| 11-27 05:30 | 伺服器分發包 | PR | claude/project-thread-70yx5u | success | 2.6 分 | 0.1 分 | [#46007636304](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46007636304/attempts/1) |
| 11-27 05:30 | CI | PR | claude/project-thread-70yx5u | success | 5.7 分 | 0.1 分 | [#46007636366](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46007636366/attempts/1) |
| 11-27 05:03 | 一鍵安裝腳本 | PR | claude/project-thread-70yx5u | success | 0.2 分 | 0.0 分 | [#46003833155](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46003833155/attempts/1) |
| 11-27 05:03 | 伺服器分發包 | PR | claude/project-thread-70yx5u | success | 2.8 分 | 0.1 分 | [#46003833283](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46003833283/attempts/1) |
| 11-27 05:03 | 桌面端建置 | PR | claude/project-thread-70yx5u | success | 5.8 分 | 0.1 分 | [#46003833346](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46003833346/attempts/1) |
| 11-27 05:03 | CI | PR | claude/project-thread-70yx5u | success | 6.3 分 | 0.1 分 | [#46003833222](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46003833222/attempts/1) |
| 11-27 04:45 | 一鍵安裝腳本 | PR | claude/project-thread-70yx5u | success | 0.2 分 | 0.0 分 | [#46001364654](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46001364654/attempts/1) |
| 11-27 04:45 | 伺服器分發包 | PR | claude/project-thread-70yx5u | success | 2.7 分 | 0.1 分 | [#46001364587](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46001364587/attempts/1) |
| 11-27 04:45 | CI | PR | claude/project-thread-70yx5u | failure | 5.0 分 | 0.1 分 | [#46001364664](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46001364664/attempts/1) |
| 11-27 04:45 | 桌面端建置 | PR | claude/project-thread-70yx5u | success | 6.7 分 | 0.1 分 | [#46001364438](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46001364438/attempts/1) |
| 11-27 04:22 | 一鍵安裝腳本 | PR | claude/project-thread-70yx5u | success | 0.3 分 | 0.1 分 | [#45998132082](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45998132082/attempts/1) |
| 11-27 04:22 | 伺服器分發包 | PR | claude/project-thread-70yx5u | success | 2.5 分 | 0.1 分 | [#45998131931](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45998131931/attempts/1) |
| 11-27 04:22 | 桌面端建置 | PR | claude/project-thread-70yx5u | success | 3.2 分 | 0.0 分 | [#45998131899](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45998131899/attempts/1) |
| 11-27 04:22 | CI | PR | claude/project-thread-70yx5u | success | 6.0 分 | 0.1 分 | [#45998131807](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45998131807/attempts/1) |
| 11-27 04:01 | 一鍵安裝腳本 | PR | claude/project-thread-70yx5u | success | 0.2 分 | 0.0 分 | [#45995174002](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45995174002/attempts/1) |
| 11-27 04:01 | 伺服器分發包 | PR | claude/project-thread-70yx5u | success | 0.2 分 | 0.0 分 | [#45995173863](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45995173863/attempts/1) |
| 11-27 04:01 | CI | PR | claude/project-thread-70yx5u | success | 2.7 分 | 0.1 分 | [#45995174216](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45995174216/attempts/1) |
| 11-27 03:50 | 桌面端建置 | PR | claude/project-thread-70yx5u | success | 0.2 分 | 0.0 分 | [#45993802364](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45993802364/attempts/1) |
| 11-27 03:50 | CI | PR | claude/project-thread-70yx5u | success | 3.1 分 | 0.1 分 | [#45993802434](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45993802434/attempts/1) |
| 11-27 03:45 | 桌面端建置 | PR | claude/project-thread-g6e2z3 | success | 0.1 分 | 0.0 分 | [#45993124899](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45993124899/attempts/1) |
| 11-27 03:45 | 伺服器分發包 | PR | claude/project-thread-g6e2z3 | success | 0.2 分 | 0.0 分 | [#45993124890](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45993124890/attempts/1) |
| 11-27 03:45 | CI | PR | claude/project-thread-g6e2z3 | success | 5.5 分 | 0.1 分 | [#45993124896](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45993124896/attempts/1) |
| 11-27 03:18 | 一鍵安裝腳本 | PR | claude/project-thread-70yx5u | success | 3.7 分 | 0.1 分 | [#45989398419](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45989398419/attempts/1) |
| 11-27 03:18 | CI | PR | claude/project-thread-70yx5u | success | 4.5 分 | 0.1 分 | [#45989398323](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45989398323/attempts/1) |
| 11-27 03:18 | 伺服器分發包 | PR | claude/project-thread-70yx5u | success | 0.2 分 | 0.0 分 | [#45989398348](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45989398348/attempts/1) |
| 11-27 03:18 | 桌面端建置 | PR | claude/project-thread-70yx5u | success | 0.2 分 | 0.1 分 | [#45989343546](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45989343546/attempts/1) |
| 11-27 03:18 | 伺服器分發包 | PR | claude/project-thread-70yx5u | success | 0.2 分 | 0.1 分 | [#45989339433](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45989339433/attempts/1) |
| 11-27 03:18 | 一鍵安裝腳本 | PR | claude/project-thread-70yx5u | cancelled | 0.8 分 | 0.1 分 | [#45989339925](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45989339925/attempts/1) |
| 11-27 03:01 | 一鍵安裝腳本 | 手動 | main | success | 33.8 分 | 1.2 分 | [#45986921389](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45986921389/attempts/1) |
| 11-27 03:00 | 每晚完整測試 | 手動 | main | success | 22.9 分 | 0.1 分 | [#45986822848](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45986822848/attempts/1) |
| 11-27 02:56 | 桌面端建置 | 推送 | main | success | 0.1 分 | 0.0 分 | [#45986339944](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45986339944/attempts/1) |
| 11-27 02:56 | 伺服器分發包 | 推送 | main | success | 0.2 分 | 0.0 分 | [#45986338807](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45986338807/attempts/1) |

