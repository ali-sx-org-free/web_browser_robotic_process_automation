# CI 運行耗時紀錄

更新：2026-11-12 16:01 America/Los_Angeles（PST，UTC−08:00）。共 140 次運行。

每次 CI、桌面端建置、一鍵安裝腳本、每晚完整測試、發布結束後，由 `.github/workflows/ci-metrics.yml` 追加到 `data/`；本頁由 `tools/ci_metrics.py report` 產生，不要手改。耗時＝第一個工作建立到最後一個工作結束（含排隊）；機器時間＝各工作實際執行的時間總和。
規則與背景見 main 的 `docs/develop/ci.html`。

## 各流程：近 7 天（前 7 天）

| 流程 | 次數 | 通過 | 耗時中位數 | 耗時 P90 | 最長排隊中位數 | 機器時間（Linux／Windows／macOS） |
|---|---|---|---|---|---|---|
| CI | 40（0） | 31（0） | 4.7 分（0.0 分） | 8.7 分（0.0 分） | 0.1 分（0.0 分） | 309／50／0 分（0／0／0 分） |
| 桌面端建置 | 27（0） | 26（0） | 0.2 分（0.0 分） | 6.3 分（0.0 分） | 0.1 分（0.0 分） | 3／49／42 分（0／0／0 分） |
| 伺服器分發包 | 31（0） | 30（0） | 0.2 分（0.0 分） | 2.7 分（0.0 分） | 0.1 分（0.0 分） | 55／0／0 分（0／0／0 分） |
| 一鍵安裝腳本 | 35（0） | 33（0） | 0.2 分（0.0 分） | 5.1 分（0.0 分） | 0.1 分（0.0 分） | 87／112／108 分（0／0／0 分） |
| 每晚完整測試 | 4（0） | 2（0） | 60.0 分（0.0 分） | 64.9 分（0.0 分） | 0.1 分（0.0 分） | 191／188／202 分（0／0／0 分） |
| 發布 | 3（0） | 3（0） | 8.0 分（0.0 分） | 8.2 分（0.0 分） | 0.1 分（0.0 分） | 16／16／34 分（0／0／0 分） |

## 每天的機器時間（分鐘，洛杉磯日期，最近 14 天）

| 日期 | 運行次數 | Linux | Windows | macOS | 合計 |
|---|---|---|---|---|---|
| 2026-11-12 | 1 | 0 | 0 | 0 | 0 |
| 2026-11-11 | 41 | 210 | 120 | 96 | 426 |
| 2026-11-10 | 61 | 265 | 177 | 153 | 595 |
| 2026-11-09 | 37 | 186 | 119 | 138 | 442 |

## 最慢的測試檔案（每份報告最近一次，括號是近 7 次的中位數）

### CI · pytest-report-3.12/pytest-report.xml

最近一次：2026-11-11 17:47 America/Los_Angeles（PST，UTC−08:00），合計 401 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 31.1（30.1） | 30 | `apps/server/tests/test_production_api.py` |
| 26.5（26.2） | 29 | `apps/server/tests/test_api.py` |
| 23.7（23.7） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 20.5（20.2） | 18 | `apps/cli/tests/test_serve.py` |
| 19.7（19.7） | 15 | `apps/server/tests/test_workflow_api.py` |
| 19.4（18.8） | 11 | `apps/server/tests/test_gitsync.py` |
| 16.9（16.7） | 13 | `apps/server/tests/test_replay.py` |
| 15.3（16.9） | 20 | `apps/server/tests/test_recorder_api.py` |
| 14.3（14.3） | 17 | `apps/worker/tests/test_recorder.py` |
| 13.9（13.7） | 10 | `apps/server/tests/test_videos.py` |

### CI · pytest-report-3.13/pytest-report.xml

最近一次：2026-11-11 17:47 America/Los_Angeles（PST，UTC−08:00），合計 356 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 25.9（25.9） | 30 | `apps/server/tests/test_production_api.py` |
| 21.1（21.1） | 29 | `apps/server/tests/test_api.py` |
| 20.3（20.3） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 19.8（20.2） | 18 | `apps/cli/tests/test_serve.py` |
| 16.0（16.2） | 11 | `apps/server/tests/test_gitsync.py` |
| 15.4（14.9） | 13 | `apps/server/tests/test_replay.py` |
| 15.2（16.5） | 15 | `apps/server/tests/test_workflow_api.py` |
| 14.7（13.9） | 20 | `apps/server/tests/test_recorder_api.py` |
| 13.9（13.9） | 17 | `apps/worker/tests/test_recorder.py` |
| 13.1（13.1） | 14 | `apps/worker/tests/test_gateway.py` |

### CI · pytest-report-windows/pytest-report.xml

最近一次：2026-11-11 17:39 America/Los_Angeles（PST，UTC−08:00），合計 836 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 194.4（222.7） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 184.9（197.2） | 26 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 134.6（134.6） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 86.0（89.1） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 64.9（64.8） | 17 | `packages\rpa_runner\tests\test_upload.py` |
| 55.9（83.7） | 10 | `packages\rpa_runner\tests\test_frames.py` |
| 48.5（46.2） | 8 | `packages\rpa_runner\tests\test_tabs.py` |
| 32.5（37.6） | 2 | `packages\rpa_runner\tests\test_download_browser.py` |
| 20.8（23.7） | 1 | `packages\rpa_runner\tests\test_profiles.py` |
| 6.3（4.9） | 2 | `tests\smoke\test_browser.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-1.xml

最近一次：2026-11-11 17:54 America/Los_Angeles（PST，UTC−08:00），合計 1137 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 132.6（168.9） | 16 | `apps/server/tests/test_portal.py` |
| 100.7（132.3） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 97.4（113.2） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 89.8（89.8） | 18 | `apps/cli/tests/test_serve.py` |
| 80.8（125.0） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 69.7（111.7） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 50.0（64.3） | 9 | `apps/server/tests/test_production_flow.py` |
| 46.1（57.0） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 40.5（58.0） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 38.4（43.4） | 4 | `apps/server/tests/test_replay_flow.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-2.xml

最近一次：2026-11-11 17:54 America/Los_Angeles（PST，UTC−08:00），合計 807 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 129.4（156.1） | 16 | `apps/server/tests/test_portal.py` |
| 94.6（105.7） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 89.6（108.9） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 83.4（107.3） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 65.1（109.7） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 50.5（76.0） | 9 | `apps/server/tests/test_production_flow.py` |
| 47.6（60.0） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 40.4（42.5） | 4 | `apps/server/tests/test_replay_flow.py` |
| 39.4（51.9） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 21.1（22.7） | 4 | `apps/server/tests/test_recorder_flow.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-3.xml

最近一次：2026-11-11 17:54 America/Los_Angeles（PST，UTC−08:00），合計 796 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 131.3（158.4） | 16 | `apps/server/tests/test_portal.py` |
| 93.9（103.6） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 89.8（105.3） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 77.1（117.9） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 66.3（87.8） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 47.6（74.4） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 46.8（72.1） | 9 | `apps/server/tests/test_production_flow.py` |
| 41.7（48.0） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 38.0（43.0） | 4 | `apps/server/tests/test_replay_flow.py` |
| 19.3（21.8） | 8 | `packages/rpa_runner/tests/test_tabs.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.12/pass-1.xml

最近一次：2026-11-11 17:54 America/Los_Angeles（PST，UTC−08:00），合計 1153 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 122.7（117.9） | 16 | `apps/server/tests/test_portal.py` |
| 95.9（95.5） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 84.2（84.2） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 78.9（78.9） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 70.0（70.0） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 57.5（56.3） | 9 | `apps/server/tests/test_production_flow.py` |
| 52.3（52.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 45.0（45.0） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 37.3（36.2） | 4 | `apps/server/tests/test_replay_flow.py` |
| 25.2（20.9） | 30 | `apps/server/tests/test_production_api.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-1.xml

最近一次：2026-11-11 17:54 America/Los_Angeles（PST，UTC−08:00），合計 1152 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 128.2（114.4） | 16 | `apps/server/tests/test_portal.py` |
| 96.0（94.4） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 84.4（83.0） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 82.6（77.5） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 69.1（69.1） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 56.5（54.7） | 9 | `apps/server/tests/test_production_flow.py` |
| 51.5（48.9） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 44.6（44.3） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 35.8（35.8） | 4 | `apps/server/tests/test_replay_flow.py` |
| 24.5（22.5） | 30 | `apps/server/tests/test_production_api.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-2.xml

最近一次：2026-11-11 17:54 America/Los_Angeles（PST，UTC−08:00），合計 817 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 118.8（113.7） | 16 | `apps/server/tests/test_portal.py` |
| 95.5（94.8） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 84.4（81.7） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 79.9（77.7） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 60.8（60.3） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 56.7（54.4） | 9 | `apps/server/tests/test_production_flow.py` |
| 52.6（48.4） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 45.6（44.2） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 37.2（36.1） | 4 | `apps/server/tests/test_replay_flow.py` |
| 21.9（21.6） | 4 | `apps/server/tests/test_recorder_flow.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-3.xml

最近一次：2026-11-11 17:54 America/Los_Angeles（PST，UTC−08:00），合計 813 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 121.5（113.0） | 16 | `apps/server/tests/test_portal.py` |
| 95.3（94.9） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 83.1（82.1） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 80.4（77.7） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 61.2（60.4） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 55.8（54.4） | 9 | `apps/server/tests/test_production_flow.py` |
| 51.5（48.9） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 44.6（44.2） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 36.9（36.2） | 4 | `apps/server/tests/test_replay_flow.py` |
| 21.2（20.4） | 17 | `packages/rpa_runner/tests/test_upload.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-1.xml

最近一次：2026-11-11 17:54 America/Los_Angeles（PST，UTC−08:00），合計 1468 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 143.7（128.8） | 16 | `apps\server\tests\test_portal.py` |
| 117.0（110.4） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 110.8（106.0） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 102.8（98.2） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 86.1（85.5） | 19 | `packages\rpa_runner\tests\test_debug.py` |
| 74.6（65.2） | 9 | `apps\server\tests\test_production_flow.py` |
| 66.2（59.0） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 57.0（52.4） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 39.4（37.9） | 4 | `apps\server\tests\test_replay_flow.py` |
| 32.6（25.5） | 30 | `apps\server\tests\test_production_api.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-2.xml

最近一次：2026-11-11 17:54 America/Los_Angeles（PST，UTC−08:00），合計 997 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 141.1（128.1） | 16 | `apps\server\tests\test_portal.py` |
| 108.1（102.1） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 104.5（100.9） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 101.6（99.3） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 72.7（69.0） | 19 | `packages\rpa_runner\tests\test_debug.py` |
| 71.1（69.1） | 9 | `apps\server\tests\test_production_flow.py` |
| 65.0（61.2） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 56.8（52.3） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 38.3（38.1） | 4 | `apps\server\tests\test_replay_flow.py` |
| 28.1（28.1） | 17 | `packages\rpa_runner\tests\test_upload.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-3.xml

最近一次：2026-11-11 17:54 America/Los_Angeles（PST，UTC−08:00），合計 974 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 137.4（129.5） | 16 | `apps\server\tests\test_portal.py` |
| 103.8（100.5） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 103.3（103.3） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 102.0（99.4） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 72.2（69.9） | 19 | `packages\rpa_runner\tests\test_debug.py` |
| 70.2（70.2） | 9 | `apps\server\tests\test_production_flow.py` |
| 63.1（58.2） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 53.8（53.5） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 39.0（38.3） | 4 | `apps\server\tests\test_replay_flow.py` |
| 27.2（27.1） | 17 | `packages\rpa_runner\tests\test_upload.py` |

## 最近 40 次運行

| 開始（洛杉磯） | 流程 | 觸發 | 分支 | 結果 | 耗時 | 最長排隊 | 運行 |
|---|---|---|---|---|---|---|---|
| 11-12 16:01 | 一鍵安裝腳本 | 推送 | main | success | 0.1 分 | 0.1 分 | [#43333669594](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43333669594/attempts/1) |
| 11-11 18:01 | 一鍵安裝腳本 | 排程 | main | success | 27.2 分 | 0.1 分 | [#43138471298](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43138471298/attempts/1) |
| 11-11 17:54 | 每晚完整測試 | 排程 | main | success | 58.9 分 | 0.1 分 | [#43137742533](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43137742533/attempts/1) |
| 11-11 17:47 | 伺服器分發包 | PR | feat/m7-flow-control | success | 0.1 分 | 0.0 分 | [#43136880539](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43136880539/attempts/1) |
| 11-11 17:47 | 一鍵安裝腳本 | PR | feat/m7-flow-control | success | 0.2 分 | 0.0 分 | [#43136880437](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43136880437/attempts/1) |
| 11-11 17:47 | CI | PR | feat/m7-flow-control | success | 2.3 分 | 0.1 分 | [#43136880591](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43136880591/attempts/1) |
| 11-11 17:46 | 伺服器分發包 | PR | feat/composite-flow | success | 0.1 分 | 0.1 分 | [#43136842877](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43136842877/attempts/1) |
| 11-11 17:46 | 一鍵安裝腳本 | PR | feat/composite-flow | success | 0.2 分 | 0.1 分 | [#43136842900](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43136842900/attempts/1) |
| 11-11 17:46 | CI | PR | feat/composite-flow | success | 2.5 分 | 0.1 分 | [#43136843000](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43136843000/attempts/1) |
| 11-11 17:39 | 一鍵安裝腳本 | PR | feat/composite-flow | success | 0.1 分 | 0.1 分 | [#43135963416](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43135963416/attempts/1) |
| 11-11 17:39 | 伺服器分發包 | PR | feat/composite-flow | success | 2.6 分 | 0.1 分 | [#43135963382](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43135963382/attempts/1) |
| 11-11 17:39 | CI | PR | feat/composite-flow | success | 4.8 分 | 0.1 分 | [#43135963332](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43135963332/attempts/1) |
| 11-11 17:39 | 桌面端建置 | PR | feat/composite-flow | success | 6.2 分 | 0.1 分 | [#43135963470](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43135963470/attempts/1) |
| 11-11 17:26 | CI | 手動 | feat/composite-flow | failure | 9.2 分 | 0.1 分 | [#43134475815](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43134475815/attempts/1) |
| 11-11 17:21 | 一鍵安裝腳本 | PR | claude/project-thread-0k55i9 | success | 0.2 分 | 0.1 分 | [#43133920041](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43133920041/attempts/1) |
| 11-11 17:21 | 桌面端建置 | PR | claude/project-thread-0k55i9 | success | 0.2 分 | 0.1 分 | [#43133920169](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43133920169/attempts/1) |
| 11-11 17:21 | CI | PR | claude/project-thread-0k55i9 | success | 2.1 分 | 0.1 分 | [#43133919993](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43133919993/attempts/1) |
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

