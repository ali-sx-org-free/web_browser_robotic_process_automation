# CI 運行耗時紀錄

更新：2026-11-14 16:58 America/Los_Angeles（PST，UTC−08:00）。共 235 次運行。

每次 CI、桌面端建置、一鍵安裝腳本、每晚完整測試、發布結束後，由 `.github/workflows/ci-metrics.yml` 追加到 `data/`；本頁由 `tools/ci_metrics.py report` 產生，不要手改。耗時＝第一個工作建立到最後一個工作結束（含排隊）；機器時間＝各工作實際執行的時間總和。
規則與背景見 main 的 `docs/develop/ci.html`。

## 各流程：近 7 天（前 7 天）

| 流程 | 次數 | 通過 | 耗時中位數 | 耗時 P90 | 最長排隊中位數 | 機器時間（Linux／Windows／macOS） |
|---|---|---|---|---|---|---|
| CI | 67（0） | 45（0） | 4.8 分（0.0 分） | 8.2 分（0.0 分） | 0.1 分（0.0 分） | 503／127／0 分（0／0／0 分） |
| 桌面端建置 | 48（0） | 43（0） | 0.2 分（0.0 分） | 6.3 分（0.0 分） | 0.1 分（0.0 分） | 6／80／77 分（0／0／0 分） |
| 伺服器分發包 | 53（0） | 49（0） | 0.2 分（0.0 分） | 2.7 分（0.0 分） | 0.1 分（0.0 分） | 99／0／0 分（0／0／0 分） |
| 一鍵安裝腳本 | 57（0） | 53（0） | 0.2 分（0.0 分） | 5.1 分（0.0 分） | 0.1 分（0.0 分） | 181／226／229 分（0／0／0 分） |
| 每晚完整測試 | 7（0） | 5（0） | 58.9 分（0.0 分） | 61.5 分（0.0 分） | 0.1 分（0.0 分） | 322／312／350 分（0／0／0 分） |
| 發布 | 3（0） | 3（0） | 8.0 分（0.0 分） | 8.2 分（0.0 分） | 0.1 分（0.0 分） | 16／16／34 分（0／0／0 分） |

## 每天的機器時間（分鐘，洛杉磯日期，最近 14 天）

| 日期 | 運行次數 | Linux | Windows | macOS | 合計 |
|---|---|---|---|---|---|
| 2026-11-14 | 31 | 116 | 93 | 80 | 289 |
| 2026-11-13 | 53 | 233 | 157 | 120 | 509 |
| 2026-11-12 | 12 | 117 | 97 | 104 | 318 |
| 2026-11-11 | 41 | 210 | 120 | 96 | 426 |
| 2026-11-10 | 61 | 265 | 177 | 153 | 595 |
| 2026-11-09 | 37 | 186 | 119 | 138 | 442 |

## 最慢的測試檔案（每份報告最近一次，括號是近 7 次的中位數）

### CI · pytest-report-3.12/pytest-report.xml

最近一次：2026-11-14 16:44 America/Los_Angeles（PST，UTC−08:00），合計 401 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 26.0（28.6） | 30 | `apps/server/tests/test_production_api.py` |
| 22.4（24.0） | 29 | `apps/server/tests/test_api.py` |
| 20.9（25.6） | 21 | `apps/server/tests/test_workflow_api.py` |
| 20.1（23.6） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 20.0（20.1） | 18 | `apps/cli/tests/test_serve.py` |
| 15.7（18.5） | 13 | `apps/server/tests/test_replay.py` |
| 15.5（18.9） | 11 | `apps/server/tests/test_gitsync.py` |
| 14.8（19.8） | 20 | `apps/server/tests/test_recorder_api.py` |
| 14.2（14.4） | 17 | `apps/worker/tests/test_recorder.py` |
| 13.5（13.6） | 14 | `apps/worker/tests/test_gateway.py` |

### CI · pytest-report-3.13/pytest-report.xml

最近一次：2026-11-14 16:44 America/Los_Angeles（PST，UTC−08:00），合計 723 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 97.4（111.4） | 13 | `apps/server/tests/test_portal.py` |
| 42.8（46.3） | 4 | `apps/server/tests/test_replay_flow.py` |
| 38.9（43.0） | 3 | `apps/server/tests/test_workflow_flow.py` |
| 32.2（37.2） | 12 | `packages/rpa_runner/tests/test_debug.py` |
| 25.3（32.5） | 5 | `apps/server/tests/test_production_flow.py` |
| 24.2（33.0） | 3 | `apps/server/tests/test_remote_worker_flow.py` |
| 22.5（31.5） | 30 | `apps/server/tests/test_production_api.py` |
| 20.9（24.0） | 21 | `apps/server/tests/test_workflow_api.py` |
| 20.2（27.0） | 29 | `apps/server/tests/test_api.py` |
| 19.9（20.4） | 18 | `apps/cli/tests/test_serve.py` |

### CI · pytest-report-windows/pytest-report.xml

最近一次：2026-11-14 16:44 America/Los_Angeles（PST，UTC−08:00），合計 1323 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 352.6（254.8） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 217.7（217.6） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 200.0（194.4） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |
| 131.5（158.6） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 119.5（117.4） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 112.3（75.1） | 10 | `packages\rpa_runner\tests\test_frames.py` |
| 54.5（75.9） | 17 | `packages\rpa_runner\tests\test_upload.py` |
| 46.4（47.2） | 8 | `packages\rpa_runner\tests\test_tabs.py` |
| 44.0（40.0） | 2 | `packages\rpa_runner\tests\test_download_browser.py` |
| 32.5（30.8） | 1 | `packages\rpa_runner\tests\test_profiles.py` |

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
| 11-14 16:58 | 一鍵安裝腳本 | PR | feat/m8-multi-user | success | 0.2 分 | 0.1 分 | [#43660822285](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43660822285/attempts/1) |
| 11-14 16:44 | 伺服器分發包 | PR | feat/m8-multi-user | failure | 2.2 分 | 0.1 分 | [#43659703574](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43659703574/attempts/1) |
| 11-14 16:44 | 一鍵安裝腳本 | PR | feat/m8-multi-user | success | 3.2 分 | 0.1 分 | [#43659703582](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43659703582/attempts/1) |
| 11-14 16:44 | CI | PR | feat/m8-multi-user | failure | 6.8 分 | 0.1 分 | [#43659703620](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43659703620/attempts/1) |
| 11-14 16:44 | 桌面端建置 | PR | feat/m8-multi-user | failure | 7.9 分 | 1.2 分 | [#43659703768](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43659703768/attempts/1) |
| 11-14 16:40 | 伺服器分發包 | PR | feat/m8-multi-user | failure | 0.4 分 | 0.1 分 | [#43659334108](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43659334108/attempts/1) |
| 11-14 16:40 | 桌面端建置 | PR | feat/m8-multi-user | failure | 0.6 分 | 0.1 分 | [#43659334101](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43659334101/attempts/1) |
| 11-14 16:40 | 一鍵安裝腳本 | PR | feat/m8-multi-user | failure | 3.4 分 | 0.1 分 | [#43659334137](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43659334137/attempts/1) |
| 11-14 16:21 | 一鍵安裝腳本 | 排程 | main | success | 30.6 分 | 0.1 分 | [#43657766073](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43657766073/attempts/1) |
| 11-14 16:17 | CI | PR | feat/m7-wrapup | success | 6.7 分 | 0.0 分 | [#43608969497 第 2 次](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43608969497/attempts/2) |
| 11-14 15:18 | 每晚完整測試 | 排程 | main | success | 7.1 分 | 0.1 分 | [#43652588563](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43652588563/attempts/1) |
| 11-14 07:13 | 伺服器分發包 | PR | feat/m7-wrapup | success | 2.8 分 | 0.1 分 | [#43608969499](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43608969499/attempts/1) |
| 11-14 07:13 | CI | PR | feat/m7-wrapup | failure | 6.7 分 | 0.1 分 | [#43608969497](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43608969497/attempts/1) |
| 11-14 07:13 | 桌面端建置 | PR | feat/m7-wrapup | success | 5.8 分 | 0.1 分 | [#43608969487](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43608969487/attempts/1) |
| 11-14 07:12 | 一鍵安裝腳本 | PR | feat/m7-wrapup | success | 0.1 分 | 0.0 分 | [#43608969532](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43608969532/attempts/1) |
| 11-14 07:11 | CI | PR | feat/m7-wrapup | cancelled | 2.1 分 | 0.1 分 | [#43608788100](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43608788100/attempts/1) |
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

