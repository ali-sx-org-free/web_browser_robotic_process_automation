# CI 運行耗時紀錄

更新：2026-11-15 17:10 America/Los_Angeles（PST，UTC−08:00）。共 282 次運行。

每次 CI、桌面端建置、一鍵安裝腳本、每晚完整測試、發布結束後，由 `.github/workflows/ci-metrics.yml` 追加到 `data/`；本頁由 `tools/ci_metrics.py report` 產生，不要手改。耗時＝第一個工作建立到最後一個工作結束（含排隊）；機器時間＝各工作實際執行的時間總和。
規則與背景見 main 的 `docs/develop/ci.html`。

## 各流程：近 7 天（前 7 天）

| 流程 | 次數 | 通過 | 耗時中位數 | 耗時 P90 | 最長排隊中位數 | 機器時間（Linux／Windows／macOS） |
|---|---|---|---|---|---|---|
| CI | 82（0） | 53（0） | 4.7 分（0.0 分） | 8.1 分（0.0 分） | 0.1 分（0.0 分） | 594／132／0 分（0／0／0 分） |
| 桌面端建置 | 56（0） | 51（0） | 0.2 分（0.0 分） | 6.3 分（0.0 分） | 0.1 分（0.0 分） | 7／86／89 分（0／0／0 分） |
| 伺服器分發包 | 65（0） | 61（0） | 0.2 分（0.0 分） | 2.8 分（0.0 分） | 0.1 分（0.0 分） | 124／0／0 分（0／0／0 分） |
| 一鍵安裝腳本 | 67（0） | 63（0） | 0.2 分（0.0 分） | 5.1 分（0.0 分） | 0.1 分（0.0 分） | 210／271／271 分（0／0／0 分） |
| 每晚完整測試 | 9（0） | 6（0） | 61.2 分（0.0 分） | 69.5 分（0.0 分） | 0.1 分（0.0 分） | 466／449／511 分（0／0／0 分） |
| 發布 | 3（0） | 3（0） | 8.0 分（0.0 分） | 8.2 分（0.0 分） | 0.1 分（0.0 分） | 16／16／34 分（0／0／0 分） |

## 每天的機器時間（分鐘，洛杉磯日期，最近 14 天）

| 日期 | 運行次數 | Linux | Windows | macOS | 合計 |
|---|---|---|---|---|---|
| 2026-11-15 | 2 | 98 | 113 | 123 | 335 |
| 2026-11-14 | 76 | 310 | 172 | 171 | 652 |
| 2026-11-13 | 53 | 233 | 157 | 120 | 509 |
| 2026-11-12 | 12 | 117 | 97 | 104 | 318 |
| 2026-11-11 | 41 | 210 | 120 | 96 | 426 |
| 2026-11-10 | 61 | 265 | 177 | 153 | 595 |
| 2026-11-09 | 37 | 186 | 119 | 138 | 442 |

## 最慢的測試檔案（每份報告最近一次，括號是近 7 次的中位數）

### CI · pytest-report-3.12/pytest-report.xml

最近一次：2026-11-14 23:30 America/Los_Angeles（PST，UTC−08:00），合計 549 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 39.8（27.6） | 30 | `apps/server/tests/test_production_api.py` |
| 33.1（23.0） | 29 | `apps/server/tests/test_api.py` |
| 30.7（22.1） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 29.8（25.1） | 21 | `apps/server/tests/test_workflow_api.py` |
| 23.1（19.2） | 11 | `apps/server/tests/test_gitsync.py` |
| 20.2（20.1） | 18 | `apps/cli/tests/test_serve.py` |
| 20.2（18.8） | 20 | `apps/server/tests/test_recorder_api.py` |
| 19.8（17.4） | 13 | `apps/server/tests/test_replay.py` |
| 17.6（14.0） | 8 | `apps/server/tests/test_batches_api.py` |
| 16.5（12.5） | 10 | `apps/server/tests/test_videos.py` |

### CI · pytest-report-3.13/pytest-report.xml

最近一次：2026-11-14 23:30 America/Los_Angeles（PST，UTC−08:00），合計 355 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 20.7（22.8） | 30 | `apps/server/tests/test_production_api.py` |
| 19.7（19.7） | 18 | `apps/cli/tests/test_serve.py` |
| 17.7（19.6） | 21 | `apps/server/tests/test_workflow_api.py` |
| 17.3（20.0） | 29 | `apps/server/tests/test_api.py` |
| 15.5（19.2） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 14.6（14.6） | 11 | `apps/server/tests/test_gitsync.py` |
| 13.9（13.9） | 17 | `apps/worker/tests/test_recorder.py` |
| 13.5（14.5） | 15 | `apps/worker/tests/test_gateway.py` |
| 13.2（13.7） | 20 | `apps/server/tests/test_recorder_api.py` |
| 10.8（12.5） | 8 | `apps/server/tests/test_batches_api.py` |

### CI · pytest-report-windows/pytest-report.xml

最近一次：2026-11-14 16:58 America/Los_Angeles（PST，UTC−08:00），合計 990 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 215.1（254.8） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 168.5（194.4） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |
| 153.7（215.1） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 129.5（158.6） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 85.8（117.4） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 64.9（75.1） | 10 | `packages\rpa_runner\tests\test_frames.py` |
| 58.0（73.3） | 17 | `packages\rpa_runner\tests\test_upload.py` |
| 47.0（47.1） | 8 | `packages\rpa_runner\tests\test_tabs.py` |
| 33.9（40.0） | 2 | `packages\rpa_runner\tests\test_download_browser.py` |
| 22.9（30.8） | 1 | `packages\rpa_runner\tests\test_profiles.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-1.xml

最近一次：2026-11-15 15:58 America/Los_Angeles（PST，UTC−08:00），合計 1702 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 171.1（168.9） | 16 | `apps/server/tests/test_portal.py` |
| 120.7（120.6） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 115.9（110.3） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 112.5（112.5） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 110.5（121.2） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 94.5（109.3） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 89.6（89.8） | 18 | `apps/cli/tests/test_serve.py` |
| 78.1（78.0） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 73.5（73.5） | 9 | `apps/server/tests/test_production_flow.py` |
| 62.6（62.6） | 5 | `apps/server/tests/test_remote_worker_flow.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-2.xml

最近一次：2026-11-15 15:58 America/Los_Angeles（PST，UTC−08:00），合計 1255 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 166.9（163.8） | 16 | `apps/server/tests/test_portal.py` |
| 121.7（107.4） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 116.5（110.1） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 101.7（101.7） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 96.0（94.8） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 86.1（84.2） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 85.9（108.9） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 70.3（70.3） | 9 | `apps/server/tests/test_production_flow.py` |
| 69.5（64.3） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 49.4（51.9） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-3.xml

最近一次：2026-11-15 15:58 America/Los_Angeles（PST，UTC−08:00），合計 1162 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 171.7（158.4） | 16 | `apps/server/tests/test_portal.py` |
| 110.4（110.4） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 108.6（108.6） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 91.8（91.8） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 75.7（75.7） | 9 | `apps/server/tests/test_production_flow.py` |
| 75.5（78.2） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 68.7（100.2） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 67.2（74.4） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 64.3（76.2） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 54.9（50.0） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.12/pass-1.xml

最近一次：2026-11-15 15:58 America/Los_Angeles（PST，UTC−08:00），合計 1246 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 117.5（117.5） | 16 | `apps/server/tests/test_portal.py` |
| 90.1（90.5） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 79.9（79.9） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 70.1（70.1） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 61.7（63.5） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 56.7（54.0） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 55.2（55.2） | 9 | `apps/server/tests/test_production_flow.py` |
| 51.7（44.1） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 43.6（46.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 41.0（41.0） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-1.xml

最近一次：2026-11-15 15:58 America/Los_Angeles（PST，UTC−08:00），合計 1176 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 110.8（119.1） | 16 | `apps/server/tests/test_portal.py` |
| 89.6（94.4） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 73.1（83.0） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 69.0（77.5） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 58.6（69.1） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 55.1（60.6） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 49.8（48.9） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 46.8（54.7） | 9 | `apps/server/tests/test_production_flow.py` |
| 45.2（47.0） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 39.2（44.3） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-2.xml

最近一次：2026-11-15 15:58 America/Los_Angeles（PST，UTC−08:00），合計 816 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 109.3（117.0） | 16 | `apps/server/tests/test_portal.py` |
| 89.5（94.8） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 73.0（81.7） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 67.2（77.7） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 58.2（60.3） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 55.3（61.1） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 46.6（54.5） | 9 | `apps/server/tests/test_production_flow.py` |
| 46.1（47.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 39.3（44.2） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 35.1（36.6） | 4 | `apps/server/tests/test_replay_flow.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-3.xml

最近一次：2026-11-15 15:58 America/Los_Angeles（PST，UTC−08:00），合計 815 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 109.9（117.8） | 16 | `apps/server/tests/test_portal.py` |
| 89.5（94.9） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 74.2（82.1） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 66.6（77.7） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 59.3（60.4） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 55.2（59.5） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 46.8（54.4） | 9 | `apps/server/tests/test_production_flow.py` |
| 43.7（48.9） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 39.2（44.2） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 34.4（36.5） | 4 | `apps/server/tests/test_replay_flow.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-1.xml

最近一次：2026-11-15 15:58 America/Los_Angeles（PST，UTC−08:00），合計 1711 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 147.9（143.7） | 16 | `apps\server\tests\test_portal.py` |
| 108.0（110.8） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 106.1（102.8） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 105.0（107.6） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 90.8（86.1） | 23 | `packages\rpa_runner\tests\test_debug.py` |
| 78.8（80.0） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 74.5（74.6） | 9 | `apps\server\tests\test_production_flow.py` |
| 67.3（63.3） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |
| 61.6（62.2） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 60.8（56.8） | 20 | `packages\rpa_runner\tests\test_run.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-2.xml

最近一次：2026-11-15 15:58 America/Los_Angeles（PST，UTC−08:00），合計 1158 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 142.4（141.1） | 16 | `apps\server\tests\test_portal.py` |
| 106.0（103.9） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 104.6（104.6） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 104.0（104.0） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 82.7（72.7） | 23 | `packages\rpa_runner\tests\test_debug.py` |
| 79.9（78.6） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 74.6（72.5） | 9 | `apps\server\tests\test_production_flow.py` |
| 62.4（62.4） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 57.0（56.3） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 53.0（47.9） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-3.xml

最近一次：2026-11-15 15:58 America/Los_Angeles（PST，UTC−08:00），合計 1162 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 142.6（137.4） | 16 | `apps\server\tests\test_portal.py` |
| 107.2（103.8） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 107.2（102.0） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 104.6（104.6） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 83.3（72.2） | 23 | `packages\rpa_runner\tests\test_debug.py` |
| 77.7（79.3） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 76.5（70.4） | 9 | `apps\server\tests\test_production_flow.py` |
| 60.7（59.5） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 56.1（55.9） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 53.6（48.9） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |

## 最近 40 次運行

| 開始（洛杉磯） | 流程 | 觸發 | 分支 | 結果 | 耗時 | 最長排隊 | 運行 |
|---|---|---|---|---|---|---|---|
| 11-15 16:24 | 一鍵安裝腳本 | 排程 | main | success | 32.8 分 | 0.1 分 | [#43780148561](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43780148561/attempts/1) |
| 11-15 15:58 | 每晚完整測試 | 排程 | main | failure | 71.0 分 | 0.8 分 | [#43777652055](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43777652055/attempts/1) |
| 11-14 23:30 | 一鍵安裝腳本 | PR | feat/m8-1-credential-grants | success | 0.2 分 | 0.0 分 | [#43690272048](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43690272048/attempts/1) |
| 11-14 23:30 | 伺服器分發包 | PR | feat/m8-1-credential-grants | success | 0.2 分 | 0.1 分 | [#43690272057](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43690272057/attempts/1) |
| 11-14 23:30 | CI | PR | feat/m8-1-credential-grants | success | 3.0 分 | 0.0 分 | [#43690272077](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43690272077/attempts/1) |
| 11-14 23:26 | 伺服器分發包 | PR | feat/m8-1-credential-grants | success | 0.1 分 | 0.0 分 | [#43689919563](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43689919563/attempts/1) |
| 11-14 23:26 | 一鍵安裝腳本 | PR | feat/m8-1-credential-grants | success | 0.2 分 | 0.1 分 | [#43689919568](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43689919568/attempts/1) |
| 11-14 23:26 | CI | PR | feat/m8-1-credential-grants | success | 4.2 分 | 0.1 分 | [#43689919578](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43689919578/attempts/1) |
| 11-14 23:19 | 桌面端建置 | PR | feat/m8-1-credential-grants | success | 0.2 分 | 0.1 分 | [#43689425178](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43689425178/attempts/1) |
| 11-14 23:19 | 一鍵安裝腳本 | PR | feat/m8-1-credential-grants | success | 0.2 分 | 0.1 分 | [#43689425199](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43689425199/attempts/1) |
| 11-14 23:19 | 伺服器分發包 | PR | feat/m8-1-credential-grants | success | 2.5 分 | 0.1 分 | [#43689425209](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43689425209/attempts/1) |
| 11-14 23:19 | CI | PR | feat/m8-1-credential-grants | failure | 4.5 分 | 0.1 分 | [#43689425181](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43689425181/attempts/1) |
| 11-14 23:13 | 桌面端建置 | PR | feat/m8-1-credential-grants | success | 0.1 分 | 0.0 分 | [#43688984565](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43688984565/attempts/1) |
| 11-14 23:13 | 一鍵安裝腳本 | PR | feat/m8-1-credential-grants | success | 0.2 分 | 0.1 分 | [#43688984603](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43688984603/attempts/1) |
| 11-14 23:13 | 伺服器分發包 | PR | feat/m8-1-credential-grants | success | 3.8 分 | 0.1 分 | [#43688984561](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43688984561/attempts/1) |
| 11-14 23:13 | CI | PR | feat/m8-1-credential-grants | failure | 4.9 分 | 0.1 分 | [#43688984654](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43688984654/attempts/1) |
| 11-14 22:50 | CI | 推送 | main | success | 8.0 分 | 0.1 分 | [#43687234319](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43687234319/attempts/1) |
| 11-14 22:49 | 一鍵安裝腳本 | 推送 | main | success | 0.1 分 | 0.0 分 | [#43687212774](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43687212774/attempts/1) |
| 11-14 22:49 | 桌面端建置 | 推送 | main | success | 0.2 分 | 0.0 分 | [#43687212823](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43687212823/attempts/1) |
| 11-14 22:49 | CI | 推送 | main | cancelled | 0.5 分 | 0.1 分 | [#43687212750](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43687212750/attempts/1) |
| 11-14 21:32 | 一鍵安裝腳本 | PR | feat/m8-multi-user | success | 0.3 分 | 0.0 分 | [#43681502475](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43681502475/attempts/1) |
| 11-14 21:32 | 桌面端建置 | PR | feat/m8-multi-user | success | 0.3 分 | 0.1 分 | [#43681502486](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43681502486/attempts/1) |
| 11-14 21:32 | 伺服器分發包 | PR | feat/m8-multi-user | success | 2.4 分 | 0.1 分 | [#43681502483](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43681502483/attempts/1) |
| 11-14 21:32 | CI | PR | feat/m8-multi-user | success | 4.4 分 | 0.0 分 | [#43681502491](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43681502491/attempts/1) |
| 11-14 18:52 | 一鍵安裝腳本 | PR | feat/m8-multi-user | success | 0.2 分 | 0.1 分 | [#43669814595](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43669814595/attempts/1) |
| 11-14 18:52 | 桌面端建置 | PR | feat/m8-multi-user | success | 0.2 分 | 0.1 分 | [#43669814583](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43669814583/attempts/1) |
| 11-14 18:52 | 伺服器分發包 | PR | feat/m8-multi-user | success | 2.4 分 | 0.1 分 | [#43669814633](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43669814633/attempts/1) |
| 11-14 18:52 | CI | PR | feat/m8-multi-user | failure | 3.8 分 | 0.1 分 | [#43669814613](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43669814613/attempts/1) |
| 11-14 18:39 | 伺服器分發包 | PR | feat/m8-multi-user | success | 0.2 分 | 0.0 分 | [#43668804703](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43668804703/attempts/1) |
| 11-14 18:39 | 桌面端建置 | PR | feat/m8-multi-user | success | 0.2 分 | 0.1 分 | [#43668804759](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43668804759/attempts/1) |
| 11-14 18:39 | CI | PR | feat/m8-multi-user | failure | 2.4 分 | 0.1 分 | [#43668804720](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43668804720/attempts/1) |
| 11-14 18:34 | 一鍵安裝腳本 | 推送 | main | success | 0.2 分 | 0.0 分 | [#43668406940](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43668406940/attempts/1) |
| 11-14 18:34 | 伺服器分發包 | 推送 | main | success | 0.2 分 | 0.1 分 | [#43668406876](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43668406876/attempts/1) |
| 11-14 18:34 | CI | 推送 | main | success | 2.2 分 | 0.1 分 | [#43668406963](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43668406963/attempts/1) |
| 11-14 17:13 | 伺服器分發包 | PR | feat/m8-multi-user | success | 0.2 分 | 0.1 分 | [#43662055056](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43662055056/attempts/1) |
| 11-14 17:13 | 一鍵安裝腳本 | PR | feat/m8-multi-user | success | 0.2 分 | 0.1 分 | [#43662055517](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43662055517/attempts/1) |
| 11-14 17:13 | CI | PR | feat/m8-multi-user | success | 2.7 分 | 0.1 分 | [#43662055051](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43662055051/attempts/1) |
| 11-14 17:08 | CI | PR | feat/m8-multi-user | success | 4.5 分 | 0.1 分 | [#43661611580](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43661611580/attempts/1) |
| 11-14 17:08 | 伺服器分發包 | PR | feat/m8-multi-user | success | 0.1 分 | 0.1 分 | [#43661613391](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43661613391/attempts/1) |
| 11-14 17:08 | CI | PR | feat/m7-wrapup | success | 2.8 分 | 0.0 分 | [#43661609732](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43661609732/attempts/1) |

