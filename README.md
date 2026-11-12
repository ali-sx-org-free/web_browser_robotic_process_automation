# CI 運行耗時紀錄

更新：2026-11-11 17:20 America/Los_Angeles（PST，UTC−08:00）。共 123 次運行。

每次 CI、桌面端建置、一鍵安裝腳本、每晚完整測試、發布結束後，由 `.github/workflows/ci-metrics.yml` 追加到 `data/`；本頁由 `tools/ci_metrics.py report` 產生，不要手改。耗時＝第一個工作建立到最後一個工作結束（含排隊）；機器時間＝各工作實際執行的時間總和。
規則與背景見 main 的 `docs/develop/ci.html`。

## 各流程：近 7 天（前 7 天）

| 流程 | 次數 | 通過 | 耗時中位數 | 耗時 P90 | 最長排隊中位數 | 機器時間（Linux／Windows／macOS） |
|---|---|---|---|---|---|---|
| CI | 35（0） | 27（0） | 4.7 分（0.0 分） | 8.7 分（0.0 分） | 0.1 分（0.0 分） | 274／41／0 分（0／0／0 分） |
| 桌面端建置 | 25（0） | 24（0） | 0.2 分（0.0 分） | 6.7 分（0.0 分） | 0.1 分（0.0 分） | 3／43／42 分（0／0／0 分） |
| 伺服器分發包 | 28（0） | 27（0） | 0.2 分（0.0 分） | 2.7 分（0.0 分） | 0.1 分（0.0 分） | 50／0／0 分（0／0／0 分） |
| 一鍵安裝腳本 | 29（0） | 27（0） | 0.2 分（0.0 分） | 3.1 分（0.0 分） | 0.1 分（0.0 分） | 61／76／74 分（0／0／0 分） |
| 每晚完整測試 | 3（0） | 1（0） | 61.2 分（0.0 分） | 64.9 分（0.0 分） | 0.1 分（0.0 分） | 124／129／147 分（0／0／0 分） |
| 發布 | 3（0） | 3（0） | 8.0 分（0.0 分） | 8.2 分（0.0 分） | 0.1 分（0.0 分） | 16／16／34 分（0／0／0 分） |

## 每天的機器時間（分鐘，洛杉磯日期，最近 14 天）

| 日期 | 運行次數 | Linux | Windows | macOS | 合計 |
|---|---|---|---|---|---|
| 2026-11-11 | 25 | 77 | 11 | 6 | 93 |
| 2026-11-10 | 61 | 265 | 177 | 153 | 595 |
| 2026-11-09 | 37 | 186 | 119 | 138 | 442 |

## 最慢的測試檔案（每份報告最近一次，括號是近 7 次的中位數）

### CI · pytest-report-3.12/pytest-report.xml

最近一次：2026-11-11 17:13 America/Los_Angeles（PST，UTC−08:00），合計 402 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 30.1（30.5） | 30 | `apps/server/tests/test_production_api.py` |
| 26.2（26.0） | 29 | `apps/server/tests/test_api.py` |
| 23.4（23.4） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 20.9（20.5） | 18 | `apps/cli/tests/test_serve.py` |
| 19.3（19.2） | 11 | `apps/server/tests/test_gitsync.py` |
| 18.4（18.7） | 15 | `apps/server/tests/test_workflow_api.py` |
| 16.9（16.4） | 20 | `apps/server/tests/test_recorder_api.py` |
| 16.9（16.9） | 13 | `apps/server/tests/test_replay.py` |
| 14.3（14.3） | 17 | `apps/worker/tests/test_recorder.py` |
| 13.7（14.0） | 10 | `apps/server/tests/test_videos.py` |

### CI · pytest-report-3.13/pytest-report.xml

最近一次：2026-11-11 17:13 America/Los_Angeles（PST，UTC−08:00），合計 752 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 111.8（100.2） | 13 | `apps/server/tests/test_portal.py` |
| 45.2（43.5） | 4 | `apps/server/tests/test_replay_flow.py` |
| 44.6（38.2） | 3 | `apps/server/tests/test_workflow_flow.py` |
| 32.1（29.9） | 10 | `packages/rpa_runner/tests/test_debug.py` |
| 31.4（27.9） | 5 | `apps/server/tests/test_production_flow.py` |
| 31.4（29.5） | 3 | `apps/server/tests/test_remote_worker_flow.py` |
| 25.6（25.6） | 30 | `apps/server/tests/test_production_api.py` |
| 22.0（17.9） | 15 | `apps/server/tests/test_replay.py` |
| 20.7（19.8） | 18 | `apps/cli/tests/test_serve.py` |
| 20.5（20.5） | 29 | `apps/server/tests/test_api.py` |

### CI · pytest-report-windows/pytest-report.xml

最近一次：2026-11-11 17:13 America/Los_Angeles（PST，UTC−08:00），合計 844 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 280.8（224.9） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 139.3（130.7） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 116.2（103.1） | 10 | `packages\rpa_runner\tests\test_frames.py` |
| 98.6（94.0） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 67.1（63.5） | 17 | `packages\rpa_runner\tests\test_upload.py` |
| 50.2（46.2） | 8 | `packages\rpa_runner\tests\test_tabs.py` |
| 39.9（24.1） | 1 | `packages\rpa_runner\tests\test_profiles.py` |
| 38.9（37.6） | 2 | `packages\rpa_runner\tests\test_download_browser.py` |
| 5.3（3.9） | 1 | `apps\desktop\tests\test_selftest.py` |
| 4.5（4.7） | 2 | `tests\smoke\test_browser.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-1.xml

最近一次：2026-11-10 16:40 America/Los_Angeles（PST，UTC−08:00），合計 1510 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 168.9（174.2） | 15 | `apps/server/tests/test_portal.py` |
| 137.5（134.9） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 129.6（120.7） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 127.6（126.3） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 113.2（115.7） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 89.8（90.2） | 18 | `apps/cli/tests/test_serve.py` |
| 64.3（72.6） | 9 | `apps/server/tests/test_production_flow.py` |
| 58.7（58.4） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 57.0（70.4） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 43.4（44.1） | 4 | `apps/server/tests/test_replay_flow.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-2.xml

最近一次：2026-11-10 16:40 America/Los_Angeles（PST，UTC−08:00），合計 1054 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 156.1（159.9） | 15 | `apps/server/tests/test_portal.py` |
| 110.4（110.1） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 108.9（113.3） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 107.3（107.3） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 105.7（108.3） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 76.3（76.2） | 9 | `apps/server/tests/test_production_flow.py` |
| 67.8（63.9） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 53.7（52.8） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 42.5（43.0） | 4 | `apps/server/tests/test_replay_flow.py` |
| 32.0（29.9） | 17 | `packages/rpa_runner/tests/test_upload.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-3.xml

最近一次：2026-11-10 16:40 America/Los_Angeles（PST，UTC−08:00），合計 1024 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 158.4（169.1） | 15 | `apps/server/tests/test_portal.py` |
| 117.9（125.9） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 105.3（112.4） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 103.6（111.6） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 87.8（111.1） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 83.3（77.7） | 9 | `apps/server/tests/test_production_flow.py` |
| 74.4（76.6） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 48.0（55.5） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 43.0（43.2） | 4 | `apps/server/tests/test_replay_flow.py` |
| 25.3（25.7） | 4 | `apps/server/tests/test_recorder_flow.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.12/pass-1.xml

最近一次：2026-11-10 16:40 America/Los_Angeles（PST，UTC−08:00），合計 1020 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 110.8（114.3） | 15 | `apps/server/tests/test_portal.py` |
| 90.5（93.0） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 74.4（79.5） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 68.5（73.8） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 63.5（67.3） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 48.0（52.1） | 9 | `apps/server/tests/test_production_flow.py` |
| 43.4（47.8） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 40.8（43.0） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 34.8（35.5） | 4 | `apps/server/tests/test_replay_flow.py` |
| 20.9（20.8） | 30 | `apps/server/tests/test_production_api.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-1.xml

最近一次：2026-11-10 16:40 America/Los_Angeles（PST，UTC−08:00），合計 1096 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 114.4（109.8） | 15 | `apps/server/tests/test_portal.py` |
| 94.4（91.6） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 83.0（77.5） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 77.5（71.5） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 69.7（66.2） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 54.7（50.3） | 9 | `apps/server/tests/test_production_flow.py` |
| 48.9（46.0） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 44.3（41.5） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 36.1（35.5） | 4 | `apps/server/tests/test_replay_flow.py` |
| 22.5（19.1） | 30 | `apps/server/tests/test_production_api.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-2.xml

最近一次：2026-11-10 16:40 America/Los_Angeles（PST，UTC−08:00），合計 791 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 113.7（109.2） | 15 | `apps/server/tests/test_portal.py` |
| 94.8（91.8） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 81.7（76.1） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 77.7（71.1） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 60.3（56.6） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 54.4（49.6） | 9 | `apps/server/tests/test_production_flow.py` |
| 48.4（45.8） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 44.2（41.5） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 36.1（35.2） | 4 | `apps/server/tests/test_replay_flow.py` |
| 21.6（19.8） | 4 | `apps/server/tests/test_recorder_flow.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-3.xml

最近一次：2026-11-10 16:40 America/Los_Angeles（PST，UTC−08:00），合計 791 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 113.0（109.4） | 15 | `apps/server/tests/test_portal.py` |
| 94.9（91.7） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 82.1（76.3） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 77.7（71.3） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 60.4（56.0） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 54.4（49.5） | 9 | `apps/server/tests/test_production_flow.py` |
| 48.9（46.0） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 44.2（41.9） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 36.2（35.4） | 4 | `apps/server/tests/test_replay_flow.py` |
| 21.5（19.6） | 4 | `apps/server/tests/test_recorder_flow.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-1.xml

最近一次：2026-11-10 16:40 America/Los_Angeles（PST，UTC−08:00），合計 1284 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 121.3（125.6） | 15 | `apps\server\tests\test_portal.py` |
| 113.2（107.6） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 91.4（84.9） | 19 | `packages\rpa_runner\tests\test_debug.py` |
| 90.2（101.3） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 89.6（95.2） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 60.5（63.5） | 9 | `apps\server\tests\test_production_flow.py` |
| 60.3（57.8） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 49.6（49.6） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 38.1（37.7） | 4 | `apps\server\tests\test_replay_flow.py` |
| 28.1（28.1） | 11 | `apps\server\tests\test_gitsync.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-2.xml

最近一次：2026-11-10 16:40 America/Los_Angeles（PST，UTC−08:00），合計 880 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 122.9（125.5） | 15 | `apps\server\tests\test_portal.py` |
| 97.0（99.0） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 90.3（94.8） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 88.9（95.5） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 65.2（67.2） | 9 | `apps\server\tests\test_production_flow.py` |
| 64.0（66.5） | 19 | `packages\rpa_runner\tests\test_debug.py` |
| 57.8（59.5） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 51.7（52.0） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 37.4（37.8） | 4 | `apps\server\tests\test_replay_flow.py` |
| 24.2（25.6） | 10 | `packages\rpa_runner\tests\test_frames.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-3.xml

最近一次：2026-11-10 16:40 America/Los_Angeles（PST，UTC−08:00），合計 896 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 121.9（125.7） | 15 | `apps\server\tests\test_portal.py` |
| 96.9（98.7） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 92.0（95.7） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 91.9（97.9） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 69.9（69.6） | 19 | `packages\rpa_runner\tests\test_debug.py` |
| 66.8（68.6） | 9 | `apps\server\tests\test_production_flow.py` |
| 53.8（56.0） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 52.3（52.9） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 37.9（38.1） | 4 | `apps\server\tests\test_replay_flow.py` |
| 26.2（26.6） | 17 | `packages\rpa_runner\tests\test_upload.py` |

## 最近 40 次運行

| 開始（洛杉磯） | 流程 | 觸發 | 分支 | 結果 | 耗時 | 最長排隊 | 運行 |
|---|---|---|---|---|---|---|---|
| 11-11 17:13 | 一鍵安裝腳本 | PR | claude/project-thread-0k55i9 | success | 0.1 分 | 0.0 分 | [#43133049806](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43133049806/attempts/1) |
| 11-11 17:13 | 伺服器分發包 | PR | claude/project-thread-0k55i9 | success | 2.3 分 | 0.1 分 | [#43133049874](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43133049874/attempts/1) |
| 11-11 17:13 | CI | PR | claude/project-thread-0k55i9 | success | 5.0 分 | 0.1 分 | [#43133049805](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43133049805/attempts/1) |
| 11-11 17:13 | 桌面端建置 | PR | claude/project-thread-0k55i9 | success | 6.3 分 | 0.1 分 | [#43133049744](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43133049744/attempts/1) |
| 11-11 17:11 | 一鍵安裝腳本 | PR | feat/m7-flow-control | success | 0.3 分 | 0.0 分 | [#43132787670](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43132787670/attempts/1) |
| 11-11 17:11 | 桌面端建置 | PR | feat/m7-flow-control | success | 0.1 分 | 0.1 分 | [#43132787607](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43132787607/attempts/1) |
| 11-11 17:11 | 伺服器分發包 | PR | feat/m7-flow-control | success | 2.7 分 | 0.1 分 | [#43132787650](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43132787650/attempts/1) |
| 11-11 17:11 | CI | PR | feat/m7-flow-control | success | 3.4 分 | 0.1 分 | [#43132787608](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43132787608/attempts/1) |
| 11-11 16:50 | 桌面端建置 | 推送 | main | success | 0.1 分 | 0.0 分 | [#43130204067](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43130204067/attempts/1) |
| 11-11 16:50 | 一鍵安裝腳本 | 推送 | main | success | 0.2 分 | 0.0 分 | [#43130203986](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43130203986/attempts/1) |
| 11-11 16:50 | CI | 推送 | main | failure | 8.7 分 | 0.0 分 | [#43130203981](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43130203981/attempts/1) |
| 11-11 16:39 | 桌面端建置 | 推送 | main | success | 0.1 分 | 0.0 分 | [#43128889452](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43128889452/attempts/1) |
| 11-11 16:39 | 一鍵安裝腳本 | 推送 | main | success | 0.1 分 | 0.0 分 | [#43128889600](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43128889600/attempts/1) |
| 11-11 16:39 | CI | 推送 | main | success | 9.1 分 | 0.1 分 | [#43128889495](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43128889495/attempts/1) |
| 11-11 03:54 | 一鍵安裝腳本 | PR | fix/scene-dag-visual-order | success | 0.2 分 | 0.0 分 | [#43015871314](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43015871314/attempts/1) |
| 11-11 03:54 | 桌面端建置 | PR | fix/scene-dag-visual-order | success | 0.2 分 | 0.1 分 | [#43015871296](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43015871296/attempts/1) |
| 11-11 03:54 | 伺服器分發包 | PR | fix/scene-dag-visual-order | success | 2.7 分 | 0.1 分 | [#43015871222](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43015871222/attempts/1) |
| 11-11 03:54 | CI | PR | fix/scene-dag-visual-order | success | 4.7 分 | 0.1 分 | [#43015871260](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43015871260/attempts/1) |
| 11-11 02:17 | CI | PR | fix/scene-dag-visual-order | success | 3.0 分 | 0.1 分 | [#43002361457](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43002361457/attempts/1) |
| 11-11 02:17 | 伺服器分發包 | PR | fix/scene-dag-visual-order | success | 2.5 分 | 0.1 分 | [#43002361211](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43002361211/attempts/1) |
| 11-11 02:17 | 桌面端建置 | PR | fix/scene-dag-visual-order | success | 0.1 分 | 0.0 分 | [#43002361250](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43002361250/attempts/1) |
| 11-11 02:16 | 桌面端建置 | PR | fix/scene-dag-visual-order | success | 0.1 分 | 0.1 分 | [#43002254488](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43002254488/attempts/1) |
| 11-11 02:16 | 一鍵安裝腳本 | PR | fix/scene-dag-visual-order | success | 0.2 分 | 0.1 分 | [#43002254097](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43002254097/attempts/1) |
| 11-11 02:16 | 伺服器分發包 | PR | fix/scene-dag-visual-order | cancelled | 1.0 分 | 0.1 分 | [#43002254421](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43002254421/attempts/1) |
| 11-11 02:16 | CI | PR | fix/scene-dag-visual-order | cancelled | 1.1 分 | 0.1 分 | [#43002254221](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43002254221/attempts/1) |
| 11-10 17:04 | 一鍵安裝腳本 | PR | feat/m7-flow-control | success | 0.2 分 | 0.0 分 | [#42936176004](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42936176004/attempts/1) |
| 11-10 17:04 | 伺服器分發包 | PR | feat/m7-flow-control | success | 0.1 分 | 0.1 分 | [#42936175352](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42936175352/attempts/1) |
| 11-10 17:04 | CI | PR | feat/m7-flow-control | success | 2.3 分 | 0.1 分 | [#42936175487](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42936175487/attempts/1) |
| 11-10 16:55 | 一鍵安裝腳本 | 排程 | main | success | 28.4 分 | 0.1 分 | [#42935067113](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42935067113/attempts/1) |
| 11-10 16:53 | 一鍵安裝腳本 | PR | feat/m7-flow-control | success | 0.1 分 | 0.1 分 | [#42934854946](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42934854946/attempts/1) |
| 11-10 16:53 | 伺服器分發包 | PR | feat/m7-flow-control | success | 2.6 分 | 0.1 分 | [#42934854780](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42934854780/attempts/1) |
| 11-10 16:53 | 桌面端建置 | PR | feat/m7-flow-control | success | 3.0 分 | 0.1 分 | [#42934854829](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42934854829/attempts/1) |
| 11-10 16:53 | CI | PR | feat/m7-flow-control | success | 5.1 分 | 0.1 分 | [#42934854837](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42934854837/attempts/1) |
| 11-10 16:40 | 每晚完整測試 | 排程 | main | failure | 61.2 分 | 0.1 分 | [#42933251106](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42933251106/attempts/1) |
| 11-10 16:37 | 伺服器分發包 | PR | docs/m6-status | success | 0.1 分 | 0.0 分 | [#42932825305](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42932825305/attempts/1) |
| 11-10 16:37 | 一鍵安裝腳本 | PR | docs/m6-status | success | 0.2 分 | 0.0 分 | [#42932825248](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42932825248/attempts/1) |
| 11-10 16:37 | CI | PR | docs/m6-status | success | 3.3 分 | 0.1 分 | [#42932825256](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42932825256/attempts/1) |
| 11-10 16:37 | 伺服器分發包 | PR | feat/m7-flow-control | success | 2.3 分 | 0.1 分 | [#42932818566](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42932818566/attempts/1) |
| 11-10 16:37 | CI | PR | feat/m7-flow-control | failure | 5.2 分 | 0.1 分 | [#42932818567](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42932818567/attempts/1) |
| 11-10 16:37 | 桌面端建置 | PR | feat/m7-flow-control | success | 6.7 分 | 0.1 分 | [#42932818437](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42932818437/attempts/1) |

