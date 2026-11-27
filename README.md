# CI 運行耗時紀錄

更新：2026-11-27 00:29 America/Los_Angeles（PST，UTC−08:00）。共 394 次運行。

每次 CI、桌面端建置、一鍵安裝腳本、每晚完整測試、發布結束後，由 `.github/workflows/ci-metrics.yml` 追加到 `data/`；本頁由 `tools/ci_metrics.py report` 產生，不要手改。耗時＝第一個工作建立到最後一個工作結束（含排隊）；機器時間＝各工作實際執行的時間總和。
規則與背景見 main 的 `docs/develop/ci.html`。

## 各流程：近 7 天（前 7 天）

| 流程 | 次數 | 通過 | 耗時中位數 | 耗時 P90 | 最長排隊中位數 | 機器時間（Linux／Windows／macOS） |
|---|---|---|---|---|---|---|
| CI | 19（43） | 13（24） | 5.7 分（4.8 分） | 9.1 分（7.6 分） | 0.1 分（0.1 分） | 177／40／0 分（304／78／0 分） |
| 桌面端建置 | 18（29） | 17（25） | 0.3 分（0.2 分） | 6.4 分（5.8 分） | 0.1 分（0.1 分） | 3／27／36 分（4／37／47 分） |
| 伺服器分發包 | 20（34） | 18（31） | 1.5 分（0.3 分） | 2.9 分（2.8 分） | 0.1 分（0.1 分） | 52／0／0 分（70／0／0 分） |
| 一鍵安裝腳本 | 19（38） | 19（37） | 2.4 分（0.2 分） | 32.7 分（31.0 分） | 0.1 分（0.1 分） | 229／298／293 分（230／297／296 分） |
| 每晚完整測試 | 13（8） | 11（7） | 72.8 分（73.3 分） | 76.3 分（78.5 分） | 0.1 分（0.1 分） | 746／671／681 分（511／474／589 分） |
| 發布 | 1（1） | 1（1） | 8.3 分（7.8 分） | 8.3 分（7.8 分） | 0.1 分（0.1 分） | 6／6／11 分（5／6／11 分） |

## 每天的機器時間（分鐘，洛杉磯日期，最近 14 天）

| 日期 | 運行次數 | Linux | Windows | macOS | 合計 |
|---|---|---|---|---|---|
| 2026-11-27 | 12 | 41 | 0 | 0 | 41 |
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
| 2026-11-13 | 53 | 233 | 157 | 120 | 509 |

## 最慢的測試檔案（每份報告最近一次，括號是近 7 次的中位數）

### CI · pytest-report-3.12/pytest-report.xml

最近一次：2026-11-27 00:18 America/Los_Angeles（PST，UTC−08:00），合計 1526 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 147.3（174.9） | 16 | `apps/server/tests/test_portal.py` |
| 103.6（116.9） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 100.6（126.9） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 88.5（107.1） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 82.2（108.8） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 78.0（99.3） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 67.5（81.7） | 9 | `apps/server/tests/test_production_flow.py` |
| 59.4（77.9） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 50.7（65.3） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 48.2（65.9） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |

### CI · pytest-report-3.13/pytest-report.xml

最近一次：2026-11-27 00:18 America/Los_Angeles（PST，UTC−08:00），合計 818 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 93.2（93.7） | 13 | `apps/server/tests/test_portal.py` |
| 43.4（43.2） | 4 | `apps/server/tests/test_replay_flow.py` |
| 42.1（40.9） | 3 | `apps/server/tests/test_workflow_flow.py` |
| 35.4（32.9） | 30 | `apps/server/tests/test_production_api.py` |
| 32.2（32.4） | 12 | `packages/rpa_runner/tests/test_debug.py` |
| 30.9（26.9） | 29 | `apps/server/tests/test_api.py` |
| 28.6（29.1） | 3 | `apps/server/tests/test_remote_worker_flow.py` |
| 27.7（27.1） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 25.6（25.6） | 5 | `apps/server/tests/test_production_flow.py` |
| 24.2（26.0） | 21 | `apps/server/tests/test_workflow_api.py` |

### CI · pytest-report-windows/pytest-report.xml

最近一次：2026-11-26 23:50 America/Los_Angeles（PST，UTC−08:00），合計 1087 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 234.8（231.8） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 194.9（185.0） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 186.3（166.1） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |
| 129.6（135.6） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 98.7（99.6） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 62.4（69.8） | 17 | `packages\rpa_runner\tests\test_upload.py` |
| 55.0（55.0） | 10 | `packages\rpa_runner\tests\test_frames.py` |
| 51.1（51.1） | 8 | `packages\rpa_runner\tests\test_tabs.py` |
| 36.1（36.1） | 2 | `packages\rpa_runner\tests\test_download_browser.py` |
| 26.6（25.0） | 1 | `packages\rpa_runner\tests\test_profiles.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-1.xml

最近一次：2026-11-26 18:51 America/Los_Angeles（PST，UTC−08:00），合計 1755 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 179.5（186.9） | 16 | `apps/server/tests/test_portal.py` |
| 133.3（133.3） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 119.0（118.1） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 113.0（122.0） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 93.9（93.9） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 92.2（92.2） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 92.0（121.7） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 90.9（90.7） | 18 | `apps/cli/tests/test_serve.py` |
| 81.6（80.1） | 9 | `apps/server/tests/test_production_flow.py` |
| 69.7（69.9） | 5 | `apps/server/tests/test_remote_worker_flow.py` |

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
| 11-27 00:29 | 桌面端建置 | PR | release/v0.10.2 | success | 0.2 分 | 0.0 分 | [#45966078479](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45966078479/attempts/1) |
| 11-27 00:18 | CI | 推送 | main | success | 8.0 分 | 0.1 分 | [#45964598026](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45964598026/attempts/1) |
| 11-27 00:18 | 一鍵安裝腳本 | 推送 | main | success | 0.2 分 | 0.1 分 | [#45964597930](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45964597930/attempts/1) |
| 11-27 00:18 | 桌面端建置 | 推送 | main | success | 0.3 分 | 0.1 分 | [#45964598061](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45964598061/attempts/1) |
| 11-27 00:18 | 伺服器分發包 | 推送 | main | success | 2.5 分 | 0.1 分 | [#45964598075](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45964598075/attempts/1) |
| 11-27 00:15 | 桌面端建置 | PR | claude/project-thread-35fd52 | success | 0.1 分 | 0.0 分 | [#45964314244](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45964314244/attempts/1) |
| 11-27 00:15 | 一鍵安裝腳本 | PR | claude/project-thread-35fd52 | success | 0.2 分 | 0.1 分 | [#45964314259](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45964314259/attempts/1) |
| 11-27 00:15 | 伺服器分發包 | PR | claude/project-thread-35fd52 | success | 2.9 分 | 0.1 分 | [#45964314211](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45964314211/attempts/1) |
| 11-27 00:15 | CI | PR | claude/project-thread-35fd52 | success | 3.9 分 | 0.1 分 | [#45964314250](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45964314250/attempts/1) |
| 11-27 00:12 | 伺服器分發包 | 推送 | main | success | 0.1 分 | 0.0 分 | [#45963955279](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45963955279/attempts/1) |
| 11-27 00:12 | 桌面端建置 | 推送 | main | success | 0.2 分 | 0.1 分 | [#45963955131](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45963955131/attempts/1) |
| 11-27 00:12 | CI | 推送 | main | cancelled | 5.4 分 | 0.1 分 | [#45963955108](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45963955108/attempts/1) |
| 11-26 23:57 | 一鍵安裝腳本 | PR | claude/project-thread-35fd52 | success | 0.2 分 | 0.0 分 | [#45962082925](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45962082925/attempts/1) |
| 11-26 23:57 | 伺服器分發包 | PR | claude/project-thread-35fd52 | success | 0.3 分 | 0.1 分 | [#45962082964](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45962082964/attempts/1) |
| 11-26 23:57 | CI | PR | claude/project-thread-35fd52 | success | 3.0 分 | 0.1 分 | [#45962082933](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45962082933/attempts/1) |
| 11-26 23:50 | 一鍵安裝腳本 | PR | claude/project-thread-35fd52 | success | 0.1 分 | 0.0 分 | [#45961229714](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45961229714/attempts/1) |
| 11-26 23:50 | 伺服器分發包 | PR | claude/project-thread-35fd52 | success | 2.9 分 | 0.1 分 | [#45961229700](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45961229700/attempts/1) |
| 11-26 23:50 | 桌面端建置 | PR | claude/project-thread-35fd52 | success | 3.1 分 | 0.1 分 | [#45961229705](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45961229705/attempts/1) |
| 11-26 23:50 | CI | PR | claude/project-thread-35fd52 | success | 6.2 分 | 0.1 分 | [#45961229694](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45961229694/attempts/1) |
| 11-26 23:26 | 一鍵安裝腳本 | PR | claude/project-thread-g6e2z3 | success | 0.2 分 | 0.1 分 | [#45958490157](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45958490157/attempts/1) |
| 11-26 23:26 | 桌面端建置 | PR | claude/project-thread-g6e2z3 | success | 0.2 分 | 0.1 分 | [#45958490133](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45958490133/attempts/1) |
| 11-26 23:26 | 伺服器分發包 | PR | claude/project-thread-g6e2z3 | success | 2.7 分 | 0.1 分 | [#45958490116](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45958490116/attempts/1) |
| 11-26 23:26 | CI | PR | claude/project-thread-g6e2z3 | failure | 6.1 分 | 0.1 分 | [#45958490072](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45958490072/attempts/1) |
| 11-26 23:20 | 伺服器分發包 | 推送 | main | success | 2.4 分 | 0.1 分 | [#45957732345](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45957732345/attempts/1) |
| 11-26 23:20 | 一鍵安裝腳本 | 推送 | main | success | 2.5 分 | 0.1 分 | [#45957732045](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45957732045/attempts/1) |
| 11-26 23:20 | 桌面端建置 | 推送 | main | success | 2.8 分 | 0.1 分 | [#45957732162](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45957732162/attempts/1) |
| 11-26 23:20 | CI | 推送 | main | failure | 9.1 分 | 0.1 分 | [#45957732303](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45957732303/attempts/1) |
| 11-26 22:54 | 桌面端建置 | 推送 | main | success | 7.1 分 | 0.1 分 | [#45954892180](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45954892180/attempts/1) |
| 11-26 22:54 | 一鍵安裝腳本 | 推送 | main | success | 3.7 分 | 0.1 分 | [#45954892159](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45954892159/attempts/1) |
| 11-26 22:54 | 伺服器分發包 | 推送 | main | success | 2.7 分 | 0.1 分 | [#45954892210](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45954892210/attempts/1) |
| 11-26 22:54 | CI | 推送 | main | failure | 10.6 分 | 0.1 分 | [#45954892364](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45954892364/attempts/1) |
| 11-26 22:54 | 伺服器分發包 | 推送 | main | cancelled | 0.6 分 | 0.1 分 | [#45954857136](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45954857136/attempts/1) |
| 11-26 22:54 | 桌面端建置 | 推送 | main | cancelled | 0.6 分 | 0.1 分 | [#45954857011](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45954857011/attempts/1) |
| 11-26 19:17 | 一鍵安裝腳本 | 排程 | main | success | 32.7 分 | 0.1 分 | [#45933324664](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45933324664/attempts/1) |
| 11-26 18:51 | 每晚完整測試 | 排程 | main | success | 76.3 分 | 0.1 分 | [#45930809920](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45930809920/attempts/1) |
| 11-25 23:03 | 每晚完整測試 | PR | claude/project-thread-nniq4z | success | 0.1 分 | 0.1 分 | [#45772533245](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45772533245/attempts/1) |
| 11-25 23:03 | 伺服器分發包 | PR | claude/project-thread-nniq4z | success | 0.2 分 | 0.1 分 | [#45772533258](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45772533258/attempts/1) |
| 11-25 23:03 | 桌面端建置 | PR | claude/project-thread-nniq4z | success | 0.3 分 | 0.1 分 | [#45772533238](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45772533238/attempts/1) |
| 11-25 23:03 | CI | PR | claude/project-thread-nniq4z | success | 2.8 分 | 0.1 分 | [#45772533307](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45772533307/attempts/1) |
| 11-25 21:57 | 每晚完整測試 | PR | claude/project-thread-nniq4z | success | 65.5 分 | 0.1 分 | [#45757505720 第 2 次](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45757505720/attempts/2) |

