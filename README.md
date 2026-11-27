# CI 運行耗時紀錄

更新：2026-11-26 22:57 America/Los_Angeles（PST，UTC−08:00）。共 364 次運行。

每次 CI、桌面端建置、一鍵安裝腳本、每晚完整測試、發布結束後，由 `.github/workflows/ci-metrics.yml` 追加到 `data/`；本頁由 `tools/ci_metrics.py report` 產生，不要手改。耗時＝第一個工作建立到最後一個工作結束（含排隊）；機器時間＝各工作實際執行的時間總和。
規則與背景見 main 的 `docs/develop/ci.html`。

## 各流程：近 7 天（前 7 天）

| 流程 | 次數 | 通過 | 耗時中位數 | 耗時 P90 | 最長排隊中位數 | 機器時間（Linux／Windows／macOS） |
|---|---|---|---|---|---|---|
| CI | 11（43） | 9（24） | 5.2 分（4.8 分） | 8.6 分（7.6 分） | 0.1 分（0.1 分） | 95／17／0 分（304／78／0 分） |
| 桌面端建置 | 10（29） | 9（25） | 0.3 分（0.2 分） | 6.4 分（5.8 分） | 0.1 分（0.1 分） | 1／15／24 分（4／37／47 分） |
| 伺服器分發包 | 13（34） | 11（31） | 0.2 分（0.3 分） | 2.8 分（2.8 分） | 0.1 分（0.1 分） | 27／0／0 分（70／0／0 分） |
| 一鍵安裝腳本 | 12（38） | 12（37） | 31.6 分（0.2 分） | 33.0 分（31.0 分） | 0.1 分（0.1 分） | 221／293／289 分（230／297／296 分） |
| 每晚完整測試 | 13（8） | 11（7） | 72.8 分（73.3 分） | 76.3 分（78.5 分） | 0.1 分（0.1 分） | 746／671／681 分（511／474／589 分） |
| 發布 | 1（1） | 1（1） | 8.3 分（7.8 分） | 8.3 分（7.8 分） | 0.1 分（0.1 分） | 6／6／11 分（5／6／11 分） |

## 每天的機器時間（分鐘，洛杉磯日期，最近 14 天）

| 日期 | 運行次數 | Linux | Windows | macOS | 合計 |
|---|---|---|---|---|---|
| 2026-11-26 | 5 | 116 | 120 | 123 | 359 |
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

最近一次：2026-11-25 23:03 America/Los_Angeles（PST，UTC−08:00），合計 406 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 26.5（28.2） | 30 | `apps/server/tests/test_production_api.py` |
| 22.8（24.8） | 29 | `apps/server/tests/test_api.py` |
| 20.6（23.2） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 19.5（20.4） | 18 | `apps/cli/tests/test_serve.py` |
| 18.8（23.8） | 21 | `apps/server/tests/test_workflow_api.py` |
| 15.7（17.3） | 11 | `apps/server/tests/test_gitsync.py` |
| 14.9（16.9） | 20 | `apps/server/tests/test_recorder_api.py` |
| 14.5（14.5） | 15 | `apps/worker/tests/test_gateway.py` |
| 13.8（13.8） | 17 | `apps/worker/tests/test_recorder.py` |
| 13.1（15.0） | 13 | `apps/server/tests/test_replay.py` |

### CI · pytest-report-3.13/pytest-report.xml

最近一次：2026-11-25 23:03 America/Los_Angeles（PST，UTC−08:00），合計 484 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 32.7（32.2） | 30 | `apps/server/tests/test_production_api.py` |
| 27.1（27.1） | 29 | `apps/server/tests/test_api.py` |
| 26.2（24.8） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 24.8（24.8） | 21 | `apps/server/tests/test_workflow_api.py` |
| 20.1（20.1） | 11 | `apps/server/tests/test_gitsync.py` |
| 19.8（19.8） | 18 | `apps/cli/tests/test_serve.py` |
| 19.6（19.1） | 20 | `apps/server/tests/test_recorder_api.py` |
| 16.6（23.6） | 13 | `apps/server/tests/test_replay.py` |
| 16.0（16.0） | 8 | `apps/server/tests/test_batches_api.py` |
| 14.6（14.6） | 15 | `apps/worker/tests/test_gateway.py` |

### CI · pytest-report-windows/pytest-report.xml

最近一次：2026-11-25 20:48 America/Los_Angeles（PST，UTC−08:00），合計 1064 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 219.1（254.8） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 180.6（194.4） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |
| 173.6（201.6） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 124.9（158.6） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 99.6（113.0） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 72.9（72.9） | 17 | `packages\rpa_runner\tests\test_upload.py` |
| 61.4（47.1） | 8 | `packages\rpa_runner\tests\test_tabs.py` |
| 58.0（64.9） | 10 | `packages\rpa_runner\tests\test_frames.py` |
| 37.6（40.0） | 2 | `packages\rpa_runner\tests\test_download_browser.py` |
| 25.0（29.0） | 1 | `packages\rpa_runner\tests\test_profiles.py` |

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
| 11-26 22:54 | 伺服器分發包 | 推送 | main | success | 2.7 分 | 0.1 分 | [#45954892210](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45954892210/attempts/1) |
| 11-26 22:54 | 伺服器分發包 | 推送 | main | cancelled | 0.6 分 | 0.1 分 | [#45954857136](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45954857136/attempts/1) |
| 11-26 22:54 | 桌面端建置 | 推送 | main | cancelled | 0.6 分 | 0.1 分 | [#45954857011](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45954857011/attempts/1) |
| 11-26 19:17 | 一鍵安裝腳本 | 排程 | main | success | 32.7 分 | 0.1 分 | [#45933324664](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45933324664/attempts/1) |
| 11-26 18:51 | 每晚完整測試 | 排程 | main | success | 76.3 分 | 0.1 分 | [#45930809920](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45930809920/attempts/1) |
| 11-25 23:03 | 每晚完整測試 | PR | claude/project-thread-nniq4z | success | 0.1 分 | 0.1 分 | [#45772533245](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45772533245/attempts/1) |
| 11-25 23:03 | 伺服器分發包 | PR | claude/project-thread-nniq4z | success | 0.2 分 | 0.1 分 | [#45772533258](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45772533258/attempts/1) |
| 11-25 23:03 | 桌面端建置 | PR | claude/project-thread-nniq4z | success | 0.3 分 | 0.1 分 | [#45772533238](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45772533238/attempts/1) |
| 11-25 23:03 | CI | PR | claude/project-thread-nniq4z | success | 2.8 分 | 0.1 分 | [#45772533307](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45772533307/attempts/1) |
| 11-25 21:57 | 每晚完整測試 | PR | claude/project-thread-nniq4z | success | 65.5 分 | 0.1 分 | [#45757505720 第 2 次](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45757505720/attempts/2) |
| 11-25 20:48 | 每晚完整測試 | PR | claude/project-thread-nniq4z | failure | 67.0 分 | 0.0 分 | [#45757505720](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45757505720/attempts/1) |
| 11-25 20:48 | 伺服器分發包 | PR | claude/project-thread-nniq4z | success | 0.2 分 | 0.0 分 | [#45757505843](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45757505843/attempts/1) |
| 11-25 20:48 | CI | PR | claude/project-thread-nniq4z | success | 5.7 分 | 0.0 分 | [#45757505754](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45757505754/attempts/1) |
| 11-25 20:39 | 一鍵安裝腳本 | PR | claude/project-thread-nniq4z | success | 2.4 分 | 0.0 分 | [#45756601690](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45756601690/attempts/1) |
| 11-25 20:39 | 伺服器分發包 | PR | claude/project-thread-nniq4z | success | 2.8 分 | 0.1 分 | [#45756601702](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45756601702/attempts/1) |
| 11-25 20:39 | 桌面端建置 | PR | claude/project-thread-nniq4z | success | 3.4 分 | 0.0 分 | [#45756601744](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45756601744/attempts/1) |
| 11-25 20:39 | CI | PR | claude/project-thread-nniq4z | failure | 7.9 分 | 0.1 分 | [#45756601684](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45756601684/attempts/1) |
| 11-25 20:39 | 每晚完整測試 | PR | claude/project-thread-nniq4z | cancelled | 9.0 分 | 0.1 分 | [#45756601741](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45756601741/attempts/1) |
| 11-25 19:10 | 一鍵安裝腳本 | 排程 | main | success | 34.9 分 | 0.1 分 | [#45747189446](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45747189446/attempts/1) |
| 11-25 18:52 | 每晚完整測試 | 排程 | main | success | 74.0 分 | 0.1 分 | [#45745284960](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45745284960/attempts/1) |
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

