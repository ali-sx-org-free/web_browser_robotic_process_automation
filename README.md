# CI 運行耗時紀錄

更新：2026-11-23 04:11 America/Los_Angeles（PST，UTC−08:00）。共 340 次運行。

每次 CI、桌面端建置、一鍵安裝腳本、每晚完整測試、發布結束後，由 `.github/workflows/ci-metrics.yml` 追加到 `data/`；本頁由 `tools/ci_metrics.py report` 產生，不要手改。耗時＝第一個工作建立到最後一個工作結束（含排隊）；機器時間＝各工作實際執行的時間總和。
規則與背景見 main 的 `docs/develop/ci.html`。

## 各流程：近 7 天（前 7 天）

| 流程 | 次數 | 通過 | 耗時中位數 | 耗時 P90 | 最長排隊中位數 | 機器時間（Linux／Windows／macOS） |
|---|---|---|---|---|---|---|
| CI | 12（82） | 11（53） | 5.3 分（4.7 分） | 10.4 分（8.1 分） | 0.1 分（0.1 分） | 114／6／0 分（594／132／0 分） |
| 桌面端建置 | 10（56） | 10（51） | 0.2 分（0.2 分） | 6.4 分（6.3 分） | 0.1 分（0.1 分） | 1／11／23 分（7／86／89 分） |
| 伺服器分發包 | 10（65） | 9（61） | 0.2 分（0.2 分） | 2.7 分（2.8 分） | 0.1 分（0.1 分） | 16／0／0 分（124／0／0 分） |
| 一鍵安裝腳本 | 15（67） | 15（63） | 0.3 分（0.2 分） | 34.8 分（5.1 分） | 0.1 分（0.1 分） | 230／302／294 分（210／271／271 分） |
| 每晚完整測試 | 9（9） | 9（6） | 75.7 分（61.2 分） | 82.4 分（69.5 分） | 0.1 分（0.1 分） | 592／546／698 分（466／449／511 分） |
| 發布 | 2（3） | 2（3） | 8.1 分（8.0 分） | 8.3 分（8.2 分） | 0.1 分（0.1 分） | 11／11／23 分（16／16／34 分） |

## 每天的機器時間（分鐘，洛杉磯日期，最近 14 天）

| 日期 | 運行次數 | Linux | Windows | macOS | 合計 |
|---|---|---|---|---|---|
| 2026-11-23 | 5 | 88 | 86 | 108 | 283 |
| 2026-11-22 | 2 | 101 | 108 | 127 | 335 |
| 2026-11-21 | 3 | 109 | 119 | 133 | 360 |
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

最近一次：2026-11-23 02:47 America/Los_Angeles（PST，UTC−08:00），合計 446 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 28.2（28.2） | 30 | `apps/server/tests/test_production_api.py` |
| 24.8（24.8） | 29 | `apps/server/tests/test_api.py` |
| 23.9（23.2） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 23.7（23.8） | 21 | `apps/server/tests/test_workflow_api.py` |
| 20.4（20.5） | 18 | `apps/cli/tests/test_serve.py` |
| 19.1（18.1） | 20 | `apps/server/tests/test_recorder_api.py` |
| 17.3（17.5） | 11 | `apps/server/tests/test_gitsync.py` |
| 15.0（15.0） | 15 | `apps/worker/tests/test_gateway.py` |
| 15.0（17.6） | 13 | `apps/server/tests/test_replay.py` |
| 13.8（13.9） | 17 | `apps/worker/tests/test_recorder.py` |

### CI · pytest-report-3.13/pytest-report.xml

最近一次：2026-11-23 02:47 America/Los_Angeles（PST，UTC−08:00），合計 819 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 102.7（97.7） | 13 | `apps/server/tests/test_portal.py` |
| 44.4（41.8） | 3 | `apps/server/tests/test_workflow_flow.py` |
| 43.1（42.1） | 4 | `apps/server/tests/test_replay_flow.py` |
| 34.7（33.5） | 12 | `packages/rpa_runner/tests/test_debug.py` |
| 26.7（26.5） | 30 | `apps/server/tests/test_production_api.py` |
| 26.5（26.0） | 3 | `apps/server/tests/test_remote_worker_flow.py` |
| 25.6（24.5） | 5 | `apps/server/tests/test_production_flow.py` |
| 24.4（23.2） | 21 | `apps/server/tests/test_workflow_api.py` |
| 24.2（20.4） | 15 | `apps/server/tests/test_replay.py` |
| 23.8（21.9） | 29 | `apps/server/tests/test_api.py` |

### CI · pytest-report-windows/pytest-report.xml

最近一次：2026-11-23 02:47 America/Los_Angeles（PST，UTC−08:00），合計 1156 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 246.8（254.8） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 191.6（201.6） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 181.8（194.4） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |
| 149.4（158.6） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 108.4（117.4） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 69.8（69.8） | 17 | `packages\rpa_runner\tests\test_upload.py` |
| 64.8（75.1） | 10 | `packages\rpa_runner\tests\test_frames.py` |
| 58.8（47.1） | 8 | `packages\rpa_runner\tests\test_tabs.py` |
| 38.4（40.0） | 2 | `packages\rpa_runner\tests\test_download_browser.py` |
| 25.9（29.0） | 1 | `packages\rpa_runner\tests\test_profiles.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-1.xml

最近一次：2026-11-23 02:47 America/Los_Angeles（PST，UTC−08:00），合計 2050 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 196.8（180.0） | 16 | `apps/server/tests/test_portal.py` |
| 142.8（129.7） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 139.9（126.7） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 127.1（123.3） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 124.2（120.3） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 111.9（108.4） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 101.1（93.9） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 91.9（85.2） | 9 | `apps/server/tests/test_production_flow.py` |
| 90.7（90.5） | 18 | `apps/cli/tests/test_serve.py` |
| 77.7（77.7） | 5 | `apps/server/tests/test_remote_worker_flow.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-2.xml

最近一次：2026-11-23 02:47 America/Los_Angeles（PST，UTC−08:00），合計 1430 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 188.9（174.6） | 16 | `apps/server/tests/test_portal.py` |
| 131.8（114.8） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 125.4（102.2） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 123.4（114.2） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 100.8（95.7） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 97.5（71.5） | 9 | `apps/server/tests/test_production_flow.py` |
| 94.6（94.6） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 86.6（79.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 81.4（80.8） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 63.8（55.5） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-3.xml

最近一次：2026-11-23 02:47 America/Los_Angeles（PST，UTC−08:00），合計 1462 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 193.0（171.2） | 16 | `apps/server/tests/test_portal.py` |
| 127.0（100.4） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 122.7（120.2） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 119.5（108.4） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 111.4（88.2） | 9 | `apps/server/tests/test_production_flow.py` |
| 102.9（90.8） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 98.9（82.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 91.1（91.1） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 84.0（81.8） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 61.3（49.7） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.12/pass-1.xml

最近一次：2026-11-23 02:47 America/Los_Angeles（PST，UTC−08:00），合計 1170 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 110.9（115.7） | 16 | `apps/server/tests/test_portal.py` |
| 89.1（91.4） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 72.6（79.6） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 67.9（71.0） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 58.9（62.3） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 56.6（57.8） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 47.9（50.3） | 9 | `apps/server/tests/test_production_flow.py` |
| 43.9（49.5） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 42.6（48.8） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 39.5（41.4） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-1.xml

最近一次：2026-11-23 02:47 America/Los_Angeles（PST，UTC−08:00），合計 1365 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 124.4（120.8） | 16 | `apps/server/tests/test_portal.py` |
| 96.3（93.1） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 85.1（80.5） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 78.7（76.4） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 68.3（66.3） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 63.6（62.3） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 58.2（49.0） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 57.2（53.5） | 9 | `apps/server/tests/test_production_flow.py` |
| 50.7（50.3） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 44.9（44.0） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-2.xml

最近一次：2026-11-23 02:47 America/Los_Angeles（PST，UTC−08:00），合計 944 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 120.7（120.7） | 16 | `apps/server/tests/test_portal.py` |
| 95.7（94.2） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 85.3（81.0） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 79.8（75.6） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 68.4（64.6） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 63.2（59.7） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 56.9（56.1） | 9 | `apps/server/tests/test_production_flow.py` |
| 55.3（50.5） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 44.6（43.5） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 40.1（37.5） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-3.xml

最近一次：2026-11-23 02:47 America/Los_Angeles（PST，UTC−08:00），合計 942 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 121.3（115.7） | 16 | `apps/server/tests/test_portal.py` |
| 95.5（91.6） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 86.0（75.9） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 79.4（72.3） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 68.6（64.5） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 63.4（58.5） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 57.7（55.7） | 9 | `apps/server/tests/test_production_flow.py` |
| 51.4（47.7） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 44.8（41.6） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 40.0（37.5） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-1.xml

最近一次：2026-11-23 02:47 America/Los_Angeles（PST，UTC−08:00），合計 1884 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 153.5（137.7） | 16 | `apps\server\tests\test_portal.py` |
| 120.5（111.1） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 113.4（105.3） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 107.5（101.8） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 87.9（79.0） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 87.2（83.8） | 23 | `packages\rpa_runner\tests\test_debug.py` |
| 79.7（74.2） | 9 | `apps\server\tests\test_production_flow.py` |
| 73.1（64.0） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 72.7（67.6） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |
| 60.0（56.3） | 20 | `packages\rpa_runner\tests\test_run.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-2.xml

最近一次：2026-11-23 02:47 America/Los_Angeles（PST，UTC−08:00），合計 1219 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 150.7（133.3） | 16 | `apps\server\tests\test_portal.py` |
| 111.8（105.2） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 110.3（100.8） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 106.4（101.5） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 86.9（83.0） | 23 | `packages\rpa_runner\tests\test_debug.py` |
| 83.1（75.9） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 79.4（68.6） | 9 | `apps\server\tests\test_production_flow.py` |
| 65.5（60.9） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 59.8（54.4） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 56.7（47.5） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-3.xml

最近一次：2026-11-23 02:47 America/Los_Angeles（PST，UTC−08:00），合計 1240 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 153.1（137.6） | 16 | `apps\server\tests\test_portal.py` |
| 118.3（105.5） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 112.8（100.9） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 105.4（103.7） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 85.5（81.2） | 23 | `packages\rpa_runner\tests\test_debug.py` |
| 83.7（79.4） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 81.3（69.9） | 9 | `apps\server\tests\test_production_flow.py` |
| 70.0（61.9） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 59.3（54.9） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 55.7（48.6） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |

## 最近 40 次運行

| 開始（洛杉磯） | 流程 | 觸發 | 分支 | 結果 | 耗時 | 最長排隊 | 運行 |
|---|---|---|---|---|---|---|---|
| 11-23 02:47 | 每晚完整測試 | PR | dependabot/github_actions/actions-ab053d56de | success | 83.9 分 | 0.7 分 | [#45159294696](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45159294696/attempts/1) |
| 11-23 02:47 | 一鍵安裝腳本 | PR | dependabot/github_actions/actions-ab053d56de | success | 0.2 分 | 0.1 分 | [#45159294505](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45159294505/attempts/1) |
| 11-23 02:47 | 伺服器分發包 | PR | dependabot/github_actions/actions-ab053d56de | success | 2.6 分 | 0.1 分 | [#45159294351](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45159294351/attempts/1) |
| 11-23 02:47 | CI | PR | dependabot/github_actions/actions-ab053d56de | success | 6.5 分 | 0.1 分 | [#45159294498](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45159294498/attempts/1) |
| 11-23 02:47 | 桌面端建置 | PR | dependabot/github_actions/actions-ab053d56de | success | 7.3 分 | 0.1 分 | [#45159294402](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45159294402/attempts/1) |
| 11-22 17:08 | 一鍵安裝腳本 | 排程 | main | success | 33.0 分 | 0.1 分 | [#45092865743](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45092865743/attempts/1) |
| 11-22 16:55 | 每晚完整測試 | 排程 | main | success | 74.5 分 | 0.1 分 | [#45091601896](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45091601896/attempts/1) |
| 11-21 18:40 | 每晚完整測試 | 排程 | main | success | 7.1 分 | 0.1 分 | [#44977205698](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44977205698/attempts/1) |
| 11-21 16:41 | 一鍵安裝腳本 | 排程 | main | success | 32.1 分 | 0.1 分 | [#44967885165](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44967885165/attempts/1) |
| 11-21 16:21 | 每晚完整測試 | 排程 | main | success | 73.2 分 | 0.1 分 | [#44966213178](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44966213178/attempts/1) |
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

