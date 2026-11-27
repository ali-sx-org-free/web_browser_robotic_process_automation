# CI 運行耗時紀錄

更新：2026-11-27 03:18 America/Los_Angeles（PST，UTC−08:00）。共 420 次運行。

每次 CI、桌面端建置、一鍵安裝腳本、每晚完整測試、發布結束後，由 `.github/workflows/ci-metrics.yml` 追加到 `data/`；本頁由 `tools/ci_metrics.py report` 產生，不要手改。耗時＝第一個工作建立到最後一個工作結束（含排隊）；機器時間＝各工作實際執行的時間總和。
規則與背景見 main 的 `docs/develop/ci.html`。

## 各流程：近 7 天（前 7 天）

| 流程 | 次數 | 通過 | 耗時中位數 | 耗時 P90 | 最長排隊中位數 | 機器時間（Linux／Windows／macOS） |
|---|---|---|---|---|---|---|
| CI | 27（43） | 21（24） | 5.4 分（4.8 分） | 10.4 分（7.6 分） | 0.1 分（0.1 分） | 256／45／0 分（304／78／0 分） |
| 桌面端建置 | 23（29） | 22（25） | 0.2 分（0.2 分） | 6.4 分（5.8 分） | 0.1 分（0.1 分） | 3／27／36 分（4／37／47 分） |
| 伺服器分發包 | 28（34） | 26（31） | 0.3 分（0.3 分） | 2.8 分（2.8 分） | 0.1 分（0.1 分） | 62／0／0 分（70／0／0 分） |
| 一鍵安裝腳本 | 23（38） | 23（37） | 0.3 分（0.2 分） | 32.7 分（31.0 分） | 0.1 分（0.1 分） | 230／298／293 分（230／297／296 分） |
| 每晚完整測試 | 13（8） | 11（7） | 72.8 分（73.3 分） | 76.3 分（78.5 分） | 0.1 分（0.1 分） | 746／671／681 分（511／474／589 分） |
| 發布 | 2（1） | 2（1） | 7.7 分（7.8 分） | 8.3 分（7.8 分） | 0.1 分（0.1 分） | 11／11／22 分（5／6／11 分） |

## 每天的機器時間（分鐘，洛杉磯日期，最近 14 天）

| 日期 | 運行次數 | Linux | Windows | macOS | 合計 |
|---|---|---|---|---|---|
| 2026-11-27 | 38 | 136 | 10 | 11 | 157 |
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

最近一次：2026-11-27 02:56 America/Los_Angeles（PST，UTC−08:00），合計 510 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 34.9（33.4） | 30 | `apps/server/tests/test_production_api.py` |
| 29.5（28.9） | 29 | `apps/server/tests/test_api.py` |
| 27.8（27.0） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 26.2（26.0） | 21 | `apps/server/tests/test_workflow_api.py` |
| 21.9（21.8） | 12 | `apps/server/tests/test_gitsync.py` |
| 19.9（19.9） | 18 | `apps/cli/tests/test_serve.py` |
| 19.7（19.3） | 20 | `apps/server/tests/test_recorder_api.py` |
| 18.0（18.0） | 13 | `apps/server/tests/test_replay.py` |
| 16.0（15.7） | 8 | `apps/server/tests/test_batches_api.py` |
| 14.7（14.7） | 6 | `apps/server/tests/test_multi_user.py` |

### CI · pytest-report-3.13/pytest-report.xml

最近一次：2026-11-27 02:56 America/Los_Angeles（PST，UTC−08:00），合計 433 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 26.6（24.5） | 30 | `apps/server/tests/test_production_api.py` |
| 23.0（21.4） | 29 | `apps/server/tests/test_api.py` |
| 21.3（21.3） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 21.1（21.1） | 21 | `apps/server/tests/test_workflow_api.py` |
| 20.3（19.9） | 18 | `apps/cli/tests/test_serve.py` |
| 19.7（19.7） | 12 | `apps/server/tests/test_gitsync.py` |
| 17.0（16.2） | 20 | `apps/server/tests/test_recorder_api.py` |
| 14.7（20.1） | 13 | `apps/server/tests/test_replay.py` |
| 14.6（14.5） | 15 | `apps/worker/tests/test_gateway.py` |
| 14.0（13.9） | 17 | `apps/worker/tests/test_recorder.py` |

### CI · pytest-report-windows/pytest-report.xml

最近一次：2026-11-27 00:28 America/Los_Angeles（PST，UTC−08:00），合計 944 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 204.9（219.1） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 150.5（184.9） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 142.8（159.2） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |
| 119.5（129.6） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 98.6（98.7） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 57.4（51.1） | 8 | `packages\rpa_runner\tests\test_tabs.py` |
| 54.7（62.4） | 17 | `packages\rpa_runner\tests\test_upload.py` |
| 51.2（53.4） | 10 | `packages\rpa_runner\tests\test_frames.py` |
| 29.7（34.3） | 2 | `packages\rpa_runner\tests\test_download_browser.py` |
| 25.0（25.0） | 1 | `packages\rpa_runner\tests\test_profiles.py` |

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
| 11-27 03:18 | 桌面端建置 | PR | claude/project-thread-70yx5u | success | 0.2 分 | 0.1 分 | [#45989343546](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45989343546/attempts/1) |
| 11-27 03:18 | 伺服器分發包 | PR | claude/project-thread-70yx5u | success | 0.2 分 | 0.1 分 | [#45989339433](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45989339433/attempts/1) |
| 11-27 02:56 | 桌面端建置 | 推送 | main | success | 0.1 分 | 0.0 分 | [#45986339944](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45986339944/attempts/1) |
| 11-27 02:56 | 伺服器分發包 | 推送 | main | success | 0.2 分 | 0.0 分 | [#45986338807](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45986338807/attempts/1) |
| 11-27 02:56 | CI | 推送 | main | success | 2.8 分 | 0.1 分 | [#45986338756](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45986338756/attempts/1) |
| 11-27 02:33 | 桌面端建置 | PR | claude/project-thread-g6e2z3 | success | 0.1 分 | 0.0 分 | [#45983160939](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45983160939/attempts/1) |
| 11-27 02:33 | 伺服器分發包 | PR | claude/project-thread-g6e2z3 | success | 0.2 分 | 0.0 分 | [#45983161209](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45983161209/attempts/1) |
| 11-27 02:33 | CI | PR | claude/project-thread-g6e2z3 | success | 3.7 分 | 0.1 分 | [#45983161125](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45983161125/attempts/1) |
| 11-27 02:03 | 發布 | 推送 | v0.11.0 | success | 7.0 分 | 0.1 分 | [#45978887706](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45978887706/attempts/1) |
| 11-27 02:00 | 伺服器分發包 | 推送 | main | success | 0.1 分 | 0.0 分 | [#45978374290](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45978374290/attempts/1) |
| 11-27 02:00 | 桌面端建置 | 推送 | main | success | 0.2 分 | 0.1 分 | [#45978374320](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45978374320/attempts/1) |
| 11-27 02:00 | CI | 推送 | main | success | 10.4 分 | 0.1 分 | [#45978374205](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45978374205/attempts/1) |
| 11-27 01:35 | 伺服器分發包 | PR | claude/project-thread-g6e2z3 | success | 0.1 分 | 0.0 分 | [#45975026290](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45975026290/attempts/1) |
| 11-27 01:35 | 一鍵安裝腳本 | PR | claude/project-thread-g6e2z3 | success | 0.2 分 | 0.1 分 | [#45975026320](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45975026320/attempts/1) |
| 11-27 01:35 | CI | PR | claude/project-thread-g6e2z3 | success | 2.4 分 | 0.1 分 | [#45975026345](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45975026345/attempts/1) |
| 11-27 01:28 | 一鍵安裝腳本 | PR | claude/project-thread-g6e2z3 | success | 0.1 分 | 0.0 分 | [#45974044566](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45974044566/attempts/1) |
| 11-27 01:28 | 伺服器分發包 | PR | claude/project-thread-g6e2z3 | success | 0.2 分 | 0.1 分 | [#45974044825](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45974044825/attempts/1) |
| 11-27 01:28 | CI | PR | claude/project-thread-g6e2z3 | success | 4.8 分 | 0.1 分 | [#45974044602](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45974044602/attempts/1) |
| 11-27 01:28 | 伺服器分發包 | 手動 | claude/project-thread-g6e2z3 | success | 2.7 分 | 0.1 分 | [#45973997810](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45973997810/attempts/1) |
| 11-27 00:36 | 桌面端建置 | 推送 | main | success | 0.2 分 | 0.1 分 | [#45966968954](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45966968954/attempts/1) |
| 11-27 00:36 | 一鍵安裝腳本 | 推送 | main | success | 0.2 分 | 0.1 分 | [#45966968783](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45966968783/attempts/1) |
| 11-27 00:36 | CI | 推送 | main | success | 8.0 分 | 0.1 分 | [#45966968689](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45966968689/attempts/1) |
| 11-27 00:29 | 桌面端建置 | PR | release/v0.10.2 | success | 0.2 分 | 0.0 分 | [#45966078479](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45966078479/attempts/1) |
| 11-27 00:29 | 一鍵安裝腳本 | PR | release/v0.10.2 | success | 0.3 分 | 0.0 分 | [#45966078311](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45966078311/attempts/1) |
| 11-27 00:29 | CI | PR | release/v0.10.2 | success | 5.1 分 | 0.1 分 | [#45966078435](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45966078435/attempts/1) |
| 11-27 00:28 | CI | 手動 | release/v0.10.2 | success | 11.4 分 | 0.0 分 | [#45965976585](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45965976585/attempts/1) |
| 11-27 00:28 | 伺服器分發包 | 手動 | release/v0.10.2 | success | 2.7 分 | 0.1 分 | [#45965972102](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45965972102/attempts/1) |
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

