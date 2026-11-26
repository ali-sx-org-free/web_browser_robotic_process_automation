# CI 運行耗時紀錄

更新：2026-11-25 19:45 America/Los_Angeles（PST，UTC−08:00）。共 345 次運行。

每次 CI、桌面端建置、一鍵安裝腳本、每晚完整測試、發布結束後，由 `.github/workflows/ci-metrics.yml` 追加到 `data/`；本頁由 `tools/ci_metrics.py report` 產生，不要手改。耗時＝第一個工作建立到最後一個工作結束（含排隊）；機器時間＝各工作實際執行的時間總和。
規則與背景見 main 的 `docs/develop/ci.html`。

## 各流程：近 7 天（前 7 天）

| 流程 | 次數 | 通過 | 耗時中位數 | 耗時 P90 | 最長排隊中位數 | 機器時間（Linux／Windows／macOS） |
|---|---|---|---|---|---|---|
| CI | 8（46） | 7（26） | 5.2 分（4.8 分） | 8.6 分（7.6 分） | 0.1 分（0.1 分） | 71／6／0 分（328／82／0 分） |
| 桌面端建置 | 7（32） | 7（28） | 0.2 分（0.2 分） | 6.4 分（5.8 分） | 0.1 分（0.1 分） | 1／11／23 分（5／37／47 分） |
| 伺服器分發包 | 8（36） | 7（33） | 0.2 分（0.3 分） | 2.7 分（2.8 分） | 0.1 分（0.1 分） | 16／0／0 分（70／0／0 分） |
| 一鍵安裝腳本 | 11（40） | 11（38） | 32.1 分（0.2 分） | 33.5 分（30.6 分） | 0.1 分（0.1 分） | 220／289／292 分（223／289／291 分） |
| 每晚完整測試 | 8（8） | 8（7） | 73.5 分（70.2 分） | 75.7 分（78.5 分） | 0.1 分（0.1 分） | 504／462／600 分（506／464／572 分） |
| 發布 | 1（1） | 1（1） | 8.3 分（7.8 分） | 8.3 分（7.8 分） | 0.1 分（0.1 分） | 6／6／11 分（5／6／11 分） |

## 每天的機器時間（分鐘，洛杉磯日期，最近 14 天）

| 日期 | 運行次數 | Linux | Windows | macOS | 合計 |
|---|---|---|---|---|---|
| 2026-11-25 | 1 | 28 | 39 | 44 | 111 |
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
| 2026-11-13 | 53 | 233 | 157 | 120 | 509 |
| 2026-11-12 | 12 | 117 | 97 | 104 | 318 |

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

最近一次：2026-11-24 19:33 America/Los_Angeles（PST，UTC−08:00），合計 1759 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 186.9（186.9） | 16 | `apps/server/tests/test_portal.py` |
| 119.0（119.0） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 118.1（115.4） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 109.0（122.4） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 100.5（129.7） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 91.2（91.2） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 90.4（90.5） | 18 | `apps/cli/tests/test_serve.py` |
| 80.1（80.1） | 9 | `apps/server/tests/test_production_flow.py` |
| 78.3（85.6） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 69.9（73.5） | 5 | `apps/server/tests/test_remote_worker_flow.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-2.xml

最近一次：2026-11-24 19:33 America/Los_Angeles（PST，UTC−08:00），合計 1218 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 167.8（167.8） | 16 | `apps/server/tests/test_portal.py` |
| 111.4（111.9） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 109.7（109.7） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 86.3（94.6） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 84.9（69.2） | 9 | `apps/server/tests/test_production_flow.py` |
| 84.6（92.2） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 82.6（94.6） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 73.8（79.1） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 73.0（73.0） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 52.8（53.3） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-3.xml

最近一次：2026-11-24 19:33 America/Los_Angeles（PST，UTC−08:00），合計 1310 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 169.1（193.0） | 16 | `apps/server/tests/test_portal.py` |
| 126.4（122.7） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 109.3（118.6） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 105.5（100.4） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 97.9（77.5） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 94.5（91.2） | 9 | `apps/server/tests/test_production_flow.py` |
| 93.5（91.1） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 89.2（89.2） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 77.9（82.5） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 51.5（51.5） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.12/pass-1.xml

最近一次：2026-11-24 19:33 America/Los_Angeles（PST，UTC−08:00），合計 1070 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 101.1（112.9） | 16 | `apps/server/tests/test_portal.py` |
| 85.4（90.5） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 68.5（74.0） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 58.9（68.5） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 54.8（62.3） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 49.6（57.5） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 43.5（48.8） | 9 | `apps/server/tests/test_production_flow.py` |
| 42.1（49.5） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 37.8（44.8） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 35.6（40.5） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-1.xml

最近一次：2026-11-24 19:33 America/Los_Angeles（PST，UTC−08:00），合計 1187 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 112.3（112.3） | 16 | `apps/server/tests/test_portal.py` |
| 89.8（89.8） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 74.2（74.2） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 66.5（66.5） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 59.7（59.7） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 55.8（55.8） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 47.8（47.8） | 9 | `apps/server/tests/test_production_flow.py` |
| 44.7（45.5） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 43.5（47.1） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 40.0（40.0） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-2.xml

最近一次：2026-11-24 19:33 America/Los_Angeles（PST，UTC−08:00），合計 826 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 109.5（109.5） | 16 | `apps/server/tests/test_portal.py` |
| 90.1（90.1） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 74.2（74.2） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 66.7（66.7） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 61.4（61.4） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 55.9（55.9） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 47.5（47.5） | 9 | `apps/server/tests/test_production_flow.py` |
| 46.9（46.9） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 39.7（39.7） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 34.6（34.6） | 4 | `apps/server/tests/test_replay_flow.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-3.xml

最近一次：2026-11-24 19:33 America/Los_Angeles（PST，UTC−08:00），合計 827 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 109.6（109.6） | 16 | `apps/server/tests/test_portal.py` |
| 89.8（89.8） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 74.1（74.1） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 66.5（66.5） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 60.8（60.8） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 55.7（55.7） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 48.5（48.5） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 47.7（47.7） | 9 | `apps/server/tests/test_production_flow.py` |
| 39.6（39.6） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 34.7（35.4） | 4 | `apps/server/tests/test_replay_flow.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-1.xml

最近一次：2026-11-24 19:33 America/Los_Angeles（PST，UTC−08:00），合計 1606 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 132.7（136.5） | 16 | `apps\server\tests\test_portal.py` |
| 101.0（101.0） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 97.6（110.2） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 94.5（97.8） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 80.8（56.3） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 77.5（78.2） | 23 | `packages\rpa_runner\tests\test_debug.py` |
| 72.4（78.8） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 66.5（69.0） | 9 | `apps\server\tests\test_production_flow.py` |
| 61.0（64.0） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |
| 55.0（62.7） | 5 | `apps\server\tests\test_remote_worker_flow.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-2.xml

最近一次：2026-11-24 19:33 America/Los_Angeles（PST，UTC−08:00），合計 1028 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 128.2（131.5） | 16 | `apps\server\tests\test_portal.py` |
| 97.5（99.9） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 95.1（96.4） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 87.7（103.6） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 75.4（77.0） | 23 | `packages\rpa_runner\tests\test_debug.py` |
| 70.0（71.3） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 64.7（65.7） | 9 | `apps\server\tests\test_production_flow.py` |
| 56.6（59.5） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 48.9（51.5） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 45.7（47.2） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-3.xml

最近一次：2026-11-24 19:33 America/Los_Angeles（PST，UTC−08:00），合計 1050 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 130.1（135.9） | 16 | `apps\server\tests\test_portal.py` |
| 97.7（98.2） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 94.7（94.7） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 93.2（98.3） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 75.0（75.0） | 23 | `packages\rpa_runner\tests\test_debug.py` |
| 74.2（76.1） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 71.3（69.9） | 9 | `apps\server\tests\test_production_flow.py` |
| 59.5（60.7） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 47.7（51.4） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 46.5（46.6） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |

## 最近 40 次運行

| 開始（洛杉磯） | 流程 | 觸發 | 分支 | 結果 | 耗時 | 最長排隊 | 運行 |
|---|---|---|---|---|---|---|---|
| 11-25 19:10 | 一鍵安裝腳本 | 排程 | main | success | 34.9 分 | 0.1 分 | [#45747189446](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45747189446/attempts/1) |
| 11-24 19:46 | 一鍵安裝腳本 | 排程 | main | success | 31.1 分 | 0.1 分 | [#45542224877](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45542224877/attempts/1) |
| 11-24 19:33 | 每晚完整測試 | 排程 | main | success | 72.8 分 | 0.1 分 | [#45540827218](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45540827218/attempts/1) |
| 11-23 20:59 | 一鍵安裝腳本 | 排程 | main | success | 32.5 分 | 0.1 分 | [#45330171052](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45330171052/attempts/1) |
| 11-23 20:48 | 每晚完整測試 | 排程 | main | success | 73.9 分 | 0.1 分 | [#45328949232](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45328949232/attempts/1) |
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

