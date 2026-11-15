# CI 運行耗時紀錄

更新：2026-11-14 22:50 America/Los_Angeles（PST，UTC−08:00）。共 265 次運行。

每次 CI、桌面端建置、一鍵安裝腳本、每晚完整測試、發布結束後，由 `.github/workflows/ci-metrics.yml` 追加到 `data/`；本頁由 `tools/ci_metrics.py report` 產生，不要手改。耗時＝第一個工作建立到最後一個工作結束（含排隊）；機器時間＝各工作實際執行的時間總和。
規則與背景見 main 的 `docs/develop/ci.html`。

## 各流程：近 7 天（前 7 天）

| 流程 | 次數 | 通過 | 耗時中位數 | 耗時 P90 | 最長排隊中位數 | 機器時間（Linux／Windows／macOS） |
|---|---|---|---|---|---|---|
| CI | 77（0） | 50（0） | 4.7 分（0.0 分） | 8.1 分（0.0 分） | 0.1 分（0.0 分） | 554／132／0 分（0／0／0 分） |
| 桌面端建置 | 54（0） | 49（0） | 0.2 分（0.0 分） | 6.3 分（0.0 分） | 0.1 分（0.0 分） | 7／86／89 分（0／0／0 分） |
| 伺服器分發包 | 61（0） | 57（0） | 0.2 分（0.0 分） | 2.7 分（0.0 分） | 0.1 分（0.0 分） | 114／0／0 分（0／0／0 分） |
| 一鍵安裝腳本 | 62（0） | 58（0） | 0.2 分（0.0 分） | 5.1 分（0.0 分） | 0.1 分（0.0 分） | 181／226／229 分（0／0／0 分） |
| 每晚完整測試 | 8（0） | 6（0） | 60.0 分（0.0 分） | 64.9 分（0.0 分） | 0.1 分（0.0 分） | 396／380／429 分（0／0／0 分） |
| 發布 | 3（0） | 3（0） | 8.0 分（0.0 分） | 8.2 分（0.0 分） | 0.1 分（0.0 分） | 16／16／34 分（0／0／0 分） |

## 每天的機器時間（分鐘，洛杉磯日期，最近 14 天）

| 日期 | 運行次數 | Linux | Windows | macOS | 合計 |
|---|---|---|---|---|---|
| 2026-11-14 | 61 | 257 | 172 | 171 | 600 |
| 2026-11-13 | 53 | 233 | 157 | 120 | 509 |
| 2026-11-12 | 12 | 117 | 97 | 104 | 318 |
| 2026-11-11 | 41 | 210 | 120 | 96 | 426 |
| 2026-11-10 | 61 | 265 | 177 | 153 | 595 |
| 2026-11-09 | 37 | 186 | 119 | 138 | 442 |

## 最慢的測試檔案（每份報告最近一次，括號是近 7 次的中位數）

### CI · pytest-report-3.12/pytest-report.xml

最近一次：2026-11-14 21:32 America/Los_Angeles（PST，UTC−08:00），合計 390 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 24.0（27.5） | 30 | `apps/server/tests/test_production_api.py` |
| 21.4（23.0） | 29 | `apps/server/tests/test_api.py` |
| 20.0（20.0） | 18 | `apps/cli/tests/test_serve.py` |
| 19.8（21.8） | 21 | `apps/server/tests/test_workflow_api.py` |
| 19.3（22.3） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 16.1（16.1） | 11 | `apps/server/tests/test_gitsync.py` |
| 14.6（14.7） | 13 | `apps/server/tests/test_replay.py` |
| 14.5（14.5） | 15 | `apps/worker/tests/test_gateway.py` |
| 14.3（15.1） | 20 | `apps/server/tests/test_recorder_api.py` |
| 14.1（14.2） | 17 | `apps/worker/tests/test_recorder.py` |

### CI · pytest-report-3.13/pytest-report.xml

最近一次：2026-11-14 21:32 America/Los_Angeles（PST，UTC−08:00），合計 738 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 93.7（90.6） | 13 | `apps/server/tests/test_portal.py` |
| 41.2（40.6） | 4 | `apps/server/tests/test_replay_flow.py` |
| 38.6（38.6） | 3 | `apps/server/tests/test_workflow_flow.py` |
| 33.7（33.7） | 12 | `packages/rpa_runner/tests/test_debug.py` |
| 27.4（25.6） | 5 | `apps/server/tests/test_production_flow.py` |
| 26.4（26.4） | 3 | `apps/server/tests/test_remote_worker_flow.py` |
| 24.2（22.7） | 30 | `apps/server/tests/test_production_api.py` |
| 21.2（20.1） | 21 | `apps/server/tests/test_workflow_api.py` |
| 20.0（19.4） | 29 | `apps/server/tests/test_api.py` |
| 19.8（19.7） | 18 | `apps/cli/tests/test_serve.py` |

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

最近一次：2026-11-14 15:56 America/Los_Angeles（PST，UTC−08:00），合計 1611 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 152.4（166.2） | 16 | `apps/server/tests/test_portal.py` |
| 120.4（120.4） | 16 | `packages/rpa_runner/tests/test_call_browser.py` |
| 112.4（112.8） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 109.3（110.5） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 108.0（122.5） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 95.4（109.5） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 90.8（89.9） | 18 | `apps/cli/tests/test_serve.py` |
| 78.0（78.0） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 69.8（74.3） | 9 | `apps/server/tests/test_production_flow.py` |
| 56.0（66.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-2.xml

最近一次：2026-11-14 15:56 America/Los_Angeles（PST，UTC−08:00），合計 1293 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 182.1（159.9） | 16 | `apps/server/tests/test_portal.py` |
| 120.5（107.3） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 116.4（108.4） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 106.1（102.7） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 93.6（93.6） | 16 | `packages/rpa_runner/tests/test_call_browser.py` |
| 93.3（109.0） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 82.4（82.4） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 73.8（68.5） | 9 | `apps/server/tests/test_production_flow.py` |
| 72.7（62.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 59.9（52.1） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-3.xml

最近一次：2026-11-14 15:56 America/Los_Angeles（PST，UTC−08:00），合計 1182 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 169.7（152.4） | 16 | `apps/server/tests/test_portal.py` |
| 103.6（109.1） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 96.1（110.7） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 93.6（90.2） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 92.0（100.8） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 88.0（88.0） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 84.9（74.9） | 9 | `apps/server/tests/test_production_flow.py` |
| 80.8（80.8） | 16 | `packages/rpa_runner/tests/test_call_browser.py` |
| 72.0（75.5） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 46.4（49.0） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.12/pass-1.xml

最近一次：2026-11-14 15:56 America/Los_Angeles（PST，UTC−08:00），合計 1044 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 100.1（114.3） | 16 | `apps/server/tests/test_portal.py` |
| 87.6（93.0） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 67.9（79.3） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 60.1（73.7） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 55.8（66.8） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 51.4（51.4） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 42.6（52.1） | 9 | `apps/server/tests/test_production_flow.py` |
| 41.9（49.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 37.1（42.9） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 36.5（36.5） | 16 | `packages/rpa_runner/tests/test_call_browser.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-1.xml

最近一次：2026-11-14 15:56 America/Los_Angeles（PST，UTC−08:00），合計 1346 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 134.1（120.2） | 16 | `apps/server/tests/test_portal.py` |
| 96.9（95.2） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 89.2（83.7） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 84.1（79.8） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 70.8（69.4） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 66.1（66.1） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 61.4（55.6） | 9 | `apps/server/tests/test_production_flow.py` |
| 51.2（48.6） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 48.7（48.7） | 16 | `packages/rpa_runner/tests/test_call_browser.py` |
| 45.5（44.5） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-2.xml

最近一次：2026-11-14 15:56 America/Los_Angeles（PST，UTC−08:00），合計 969 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 125.4（117.9） | 16 | `apps/server/tests/test_portal.py` |
| 97.1（95.2） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 85.6（83.1） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 84.6（78.4） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 70.6（60.5） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 66.9（66.9） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 59.3（55.2） | 9 | `apps/server/tests/test_production_flow.py` |
| 57.8（47.8） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 45.7（44.6） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 36.7（36.7） | 4 | `apps/server/tests/test_replay_flow.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-3.xml

最近一次：2026-11-14 15:56 America/Los_Angeles（PST，UTC−08:00），合計 942 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 121.5（119.3） | 16 | `apps/server/tests/test_portal.py` |
| 96.5（95.1） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 84.5（82.6） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 79.5（78.3） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 68.6（60.8） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 63.7（63.7） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 58.5（49.5） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 57.3（55.1） | 9 | `apps/server/tests/test_production_flow.py` |
| 45.2（44.4） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 36.5（36.5） | 4 | `apps/server/tests/test_replay_flow.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-1.xml

最近一次：2026-11-14 15:56 America/Los_Angeles（PST，UTC−08:00），合計 1660 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 145.1（136.8） | 16 | `apps\server\tests\test_portal.py` |
| 111.5（111.5） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 105.8（101.2） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 105.8（107.6） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 85.7（85.7） | 23 | `packages\rpa_runner\tests\test_debug.py` |
| 81.2（81.2） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 76.6（74.6） | 9 | `apps\server\tests\test_production_flow.py` |
| 63.1（62.2） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 59.4（59.4） | 16 | `packages\rpa_runner\tests\test_call_browser.py` |
| 57.3（55.1） | 20 | `packages\rpa_runner\tests\test_run.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-2.xml

最近一次：2026-11-14 15:56 America/Los_Angeles（PST，UTC−08:00），合計 1146 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 140.5（140.8） | 16 | `apps\server\tests\test_portal.py` |
| 105.9（104.0） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 104.7（102.7） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 103.9（102.8） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 83.6（72.5） | 23 | `packages\rpa_runner\tests\test_debug.py` |
| 77.3（77.3） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 73.9（71.8） | 9 | `apps\server\tests\test_production_flow.py` |
| 62.9（62.0） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 56.3（55.9） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 42.7（42.7） | 16 | `packages\rpa_runner\tests\test_call_browser.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-3.xml

最近一次：2026-11-14 15:56 America/Los_Angeles（PST，UTC−08:00），合計 1162 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 141.4（134.2） | 16 | `apps\server\tests\test_portal.py` |
| 107.7（105.8） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 106.8（101.3） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 103.9（102.2） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 90.2（71.4） | 23 | `packages\rpa_runner\tests\test_debug.py` |
| 81.0（81.0） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 72.1（70.3） | 9 | `apps\server\tests\test_production_flow.py` |
| 59.5（58.9） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 56.0（54.8） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 44.1（44.1） | 16 | `packages\rpa_runner\tests\test_call_browser.py` |

## 最近 40 次運行

| 開始（洛杉磯） | 流程 | 觸發 | 分支 | 結果 | 耗時 | 最長排隊 | 運行 |
|---|---|---|---|---|---|---|---|
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
| 11-14 17:07 | 桌面端建置 | PR | feat/m8-multi-user | success | 0.2 分 | 0.1 分 | [#43661574210](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43661574210/attempts/1) |
| 11-14 17:07 | 伺服器分發包 | PR | feat/m8-multi-user | success | 0.2 分 | 0.1 分 | [#43661574077](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43661574077/attempts/1) |
| 11-14 17:07 | CI | PR | feat/m8-multi-user | cancelled | 0.7 分 | 0.1 分 | [#43661574106](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43661574106/attempts/1) |
| 11-14 16:58 | 一鍵安裝腳本 | PR | feat/m8-multi-user | success | 0.2 分 | 0.1 分 | [#43660822285](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43660822285/attempts/1) |
| 11-14 16:58 | 伺服器分發包 | PR | feat/m8-multi-user | success | 2.8 分 | 0.1 分 | [#43660822222](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43660822222/attempts/1) |
| 11-14 16:58 | CI | PR | feat/m8-multi-user | failure | 5.4 分 | 0.1 分 | [#43660822221](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43660822221/attempts/1) |
| 11-14 16:58 | 桌面端建置 | PR | feat/m8-multi-user | success | 7.8 分 | 0.1 分 | [#43660822252](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43660822252/attempts/1) |
| 11-14 16:44 | 伺服器分發包 | PR | feat/m8-multi-user | failure | 2.2 分 | 0.1 分 | [#43659703574](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43659703574/attempts/1) |
| 11-14 16:44 | 一鍵安裝腳本 | PR | feat/m8-multi-user | success | 3.2 分 | 0.1 分 | [#43659703582](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43659703582/attempts/1) |
| 11-14 16:44 | CI | PR | feat/m8-multi-user | failure | 6.8 分 | 0.1 分 | [#43659703620](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43659703620/attempts/1) |
| 11-14 16:44 | 桌面端建置 | PR | feat/m8-multi-user | failure | 7.9 分 | 1.2 分 | [#43659703768](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43659703768/attempts/1) |
| 11-14 16:40 | 伺服器分發包 | PR | feat/m8-multi-user | failure | 0.4 分 | 0.1 分 | [#43659334108](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43659334108/attempts/1) |
| 11-14 16:40 | 桌面端建置 | PR | feat/m8-multi-user | failure | 0.6 分 | 0.1 分 | [#43659334101](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43659334101/attempts/1) |
| 11-14 16:40 | 一鍵安裝腳本 | PR | feat/m8-multi-user | failure | 3.4 分 | 0.1 分 | [#43659334137](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43659334137/attempts/1) |
| 11-14 16:21 | 一鍵安裝腳本 | 排程 | main | success | 30.6 分 | 0.1 分 | [#43657766073](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43657766073/attempts/1) |
| 11-14 16:17 | CI | PR | feat/m7-wrapup | success | 6.7 分 | 0.0 分 | [#43608969497 第 2 次](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43608969497/attempts/2) |
| 11-14 15:56 | 每晚完整測試 | 排程 | main | success | 69.5 分 | 0.1 分 | [#43655676514](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43655676514/attempts/1) |

