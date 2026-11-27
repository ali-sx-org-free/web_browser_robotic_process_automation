# CI 運行耗時紀錄

更新：2026-11-26 19:50 America/Los_Angeles（PST，UTC−08:00）。共 360 次運行。

每次 CI、桌面端建置、一鍵安裝腳本、每晚完整測試、發布結束後，由 `.github/workflows/ci-metrics.yml` 追加到 `data/`；本頁由 `tools/ci_metrics.py report` 產生，不要手改。耗時＝第一個工作建立到最後一個工作結束（含排隊）；機器時間＝各工作實際執行的時間總和。
規則與背景見 main 的 `docs/develop/ci.html`。

## 各流程：近 7 天（前 7 天）

| 流程 | 次數 | 通過 | 耗時中位數 | 耗時 P90 | 最長排隊中位數 | 機器時間（Linux／Windows／macOS） |
|---|---|---|---|---|---|---|
| CI | 11（43） | 9（24） | 5.2 分（4.8 分） | 8.6 分（7.6 分） | 0.1 分（0.1 分） | 95／17／0 分（304／78／0 分） |
| 桌面端建置 | 9（29） | 9（25） | 0.3 分（0.2 分） | 6.4 分（5.8 分） | 0.1 分（0.1 分） | 1／14／23 分（4／37／47 分） |
| 伺服器分發包 | 11（34） | 10（31） | 0.2 分（0.3 分） | 2.8 分（2.8 分） | 0.1 分（0.1 分） | 21／0／0 分（70／0／0 分） |
| 一鍵安裝腳本 | 12（38） | 12（37） | 31.6 分（0.2 分） | 33.0 分（31.0 分） | 0.1 分（0.1 分） | 221／293／289 分（230／297／296 分） |
| 每晚完整測試 | 12（8） | 10（7） | 71.1 分（73.3 分） | 74.5 分（78.5 分） | 0.1 分（0.1 分） | 669／595／599 分（511／474／589 分） |
| 發布 | 1（1） | 1（1） | 8.3 分（7.8 分） | 8.3 分（7.8 分） | 0.1 分（0.1 分） | 6／6／11 分（5／6／11 分） |

## 每天的機器時間（分鐘，洛杉磯日期，最近 14 天）

| 日期 | 運行次數 | Linux | Windows | macOS | 合計 |
|---|---|---|---|---|---|
| 2026-11-26 | 1 | 33 | 44 | 40 | 117 |
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

最近一次：2026-11-25 18:52 America/Los_Angeles（PST，UTC−08:00），合計 1816 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 177.4（186.9） | 16 | `apps/server/tests/test_portal.py` |
| 134.7（122.4） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 123.0（122.0） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 121.7（121.7） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 105.8（111.1） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 101.6（85.6） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 97.9（91.2） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 90.8（90.7） | 18 | `apps/cli/tests/test_serve.py` |
| 67.6（80.1） | 9 | `apps/server/tests/test_production_flow.py` |
| 63.1（55.6） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-2.xml

最近一次：2026-11-25 18:52 America/Los_Angeles（PST，UTC−08:00），合計 1357 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 176.0（167.8） | 16 | `apps/server/tests/test_portal.py` |
| 127.3（114.9） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 123.0（109.7） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 122.2（94.6） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 101.2（94.6） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 96.0（92.2） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 86.1（79.1） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 78.2（71.5） | 9 | `apps/server/tests/test_production_flow.py` |
| 73.3（73.3） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 61.3（53.3） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-3.xml

最近一次：2026-11-25 18:52 America/Los_Angeles（PST，UTC−08:00），合計 1176 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 158.0（169.1） | 16 | `apps/server/tests/test_portal.py` |
| 106.7（122.7） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 105.4（109.3） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 96.5（96.5） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 86.9（86.9） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 84.1（91.1） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 84.0（81.8） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 68.5（88.4） | 9 | `apps/server/tests/test_production_flow.py` |
| 66.5（82.5） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 50.6（51.5） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.12/pass-1.xml

最近一次：2026-11-25 21:57 America/Los_Angeles（PST，UTC−08:00），合計 2102 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 97.2（107.8） | 16 | `apps/server/tests/test_portal.py` |
| 97.2（107.8） | 16 | `apps/server/tests/test_portal.py` |
| 85.4（87.7） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 85.4（87.7） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 64.2（70.6） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 64.2（70.6） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 57.3（63.4） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 57.3（63.4） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 54.8（58.3） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 54.8（58.3） | 23 | `packages/rpa_runner/tests/test_debug.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-1.xml

最近一次：2026-11-25 21:57 America/Los_Angeles（PST，UTC−08:00），合計 2583 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 117.8（119.3） | 16 | `apps/server/tests/test_portal.py` |
| 117.8（119.3） | 16 | `apps/server/tests/test_portal.py` |
| 93.1（93.1） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 93.1（93.1） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 79.5（80.0） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 79.5（80.0） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 74.6（76.7） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 74.6（76.7） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 64.6（65.4） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 64.6（65.4） | 23 | `packages/rpa_runner/tests/test_debug.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-2.xml

最近一次：2026-11-25 21:57 America/Los_Angeles（PST，UTC−08:00），合計 1745 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 115.1（117.9） | 16 | `apps/server/tests/test_portal.py` |
| 115.1（117.9） | 16 | `apps/server/tests/test_portal.py` |
| 92.1（93.2） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 92.1（93.2） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 77.6（79.3） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 77.6（79.3） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 70.4（73.3） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 70.4（73.3） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 62.2（63.4） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 62.2（63.4） | 23 | `packages/rpa_runner/tests/test_debug.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-3.xml

最近一次：2026-11-25 21:57 America/Los_Angeles（PST，UTC−08:00），合計 1750 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 115.7（115.7） | 16 | `apps/server/tests/test_portal.py` |
| 115.7（115.7） | 16 | `apps/server/tests/test_portal.py` |
| 91.2（91.4） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 91.2（91.4） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 78.0（78.0） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 78.0（78.0） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 70.2（71.2） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 70.2（71.2） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 63.8（64.2） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 63.8（64.2） | 23 | `packages/rpa_runner/tests/test_debug.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-1.xml

最近一次：2026-11-25 21:57 America/Los_Angeles（PST，UTC−08:00），合計 5059 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 136.5（134.0） | 16 | `apps\server\tests\test_portal.py` |
| 134.0（134.0） | 16 | `apps\server\tests\test_portal.py` |
| 134.0（134.0） | 16 | `apps\server\tests\test_portal.py` |
| 104.4（104.4） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 104.4（104.4） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 102.1（104.4） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 101.9（101.0） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 99.4（101.0） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 99.4（101.0） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 94.0（94.0） | 6 | `apps\server\tests\test_workflow_flow.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-2.xml

最近一次：2026-11-25 21:57 America/Los_Angeles（PST，UTC−08:00），合計 3249 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 138.5（128.2） | 16 | `apps\server\tests\test_portal.py` |
| 127.9（128.2） | 16 | `apps\server\tests\test_portal.py` |
| 127.9（128.2） | 16 | `apps\server\tests\test_portal.py` |
| 113.4（100.2） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 100.2（100.2） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 100.2（100.2） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 99.7（99.7） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 99.7（99.7） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 98.8（99.7） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 95.8（95.1） | 6 | `apps\server\tests\test_workflow_flow.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-3.xml

最近一次：2026-11-25 21:57 America/Los_Angeles（PST，UTC−08:00），合計 3299 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 137.7（135.9） | 16 | `apps\server\tests\test_portal.py` |
| 137.7（135.9） | 16 | `apps\server\tests\test_portal.py` |
| 134.6（135.9） | 16 | `apps\server\tests\test_portal.py` |
| 109.2（107.2） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 107.6（107.2） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 107.6（107.2） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 101.1（99.2） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 99.2（99.2） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 99.2（99.2） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 95.6（95.1） | 6 | `apps\server\tests\test_workflow_flow.py` |

## 最近 40 次運行

| 開始（洛杉磯） | 流程 | 觸發 | 分支 | 結果 | 耗時 | 最長排隊 | 運行 |
|---|---|---|---|---|---|---|---|
| 11-26 19:17 | 一鍵安裝腳本 | 排程 | main | success | 32.7 分 | 0.1 分 | [#45933324664](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/45933324664/attempts/1) |
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
| 11-20 06:19 | 桌面端建置 | PR | m14/expected-revision | success | 0.2 分 | 0.1 分 | [#44752382641](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44752382641/attempts/1) |
| 11-20 06:19 | CI | PR | m14/expected-revision | success | 5.2 分 | 0.1 分 | [#44752382681](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44752382681/attempts/1) |
| 11-20 06:08 | 發布 | 推送 | v0.10.1 | success | 8.3 分 | 0.1 分 | [#44750615230](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44750615230/attempts/1) |
| 11-20 06:08 | 伺服器分發包 | 推送 | main | success | 0.1 分 | 0.1 分 | [#44750575305](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44750575305/attempts/1) |

