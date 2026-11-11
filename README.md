# CI 運行耗時紀錄

更新：2026-11-10 16:56 America/Los_Angeles（PST，UTC−08:00）。共 91 次運行。

每次 CI、桌面端建置、一鍵安裝腳本、每晚完整測試、發布結束後，由 `.github/workflows/ci-metrics.yml` 追加到 `data/`；本頁由 `tools/ci_metrics.py report` 產生，不要手改。耗時＝第一個工作建立到最後一個工作結束（含排隊）；機器時間＝各工作實際執行的時間總和。
規則與背景見 main 的 `docs/develop/ci.html`。

## 各流程：近 7 天（前 7 天）

| 流程 | 次數 | 通過 | 耗時中位數 | 耗時 P90 | 最長排隊中位數 | 機器時間（Linux／Windows／macOS） |
|---|---|---|---|---|---|---|
| CI | 26（0） | 20（0） | 4.7 分（0.0 分） | 8.2 分（0.0 分） | 0.1 分（0.0 分） | 209／31／0 分（0／0／0 分） |
| 桌面端建置 | 17（0） | 16（0） | 0.2 分（0.0 分） | 6.7 分（0.0 分） | 0.1 分（0.0 分） | 2／34／36 分（0／0／0 分） |
| 伺服器分發包 | 22（0） | 22（0） | 0.2 分（0.0 分） | 2.6 分（0.0 分） | 0.1 分（0.0 分） | 30／0／0 分（0／0／0 分） |
| 一鍵安裝腳本 | 21（0） | 19（0） | 0.2 分（0.0 分） | 3.1 分（0.0 分） | 0.1 分（0.0 分） | 34／39／37 分（0／0／0 分） |
| 每晚完整測試 | 2（0） | 1（0） | 43.7 分（0.0 分） | 64.9 分（0.0 分） | 0.1 分（0.0 分） | 60／77／76 分（0／0／0 分） |
| 發布 | 3（0） | 3（0） | 8.0 分（0.0 分） | 8.2 分（0.0 分） | 0.1 分（0.0 分） | 16／16／34 分（0／0／0 分） |

## 每天的機器時間（分鐘，洛杉磯日期，最近 14 天）

| 日期 | 運行次數 | Linux | Windows | macOS | 合計 |
|---|---|---|---|---|---|
| 2026-11-10 | 54 | 164 | 79 | 47 | 290 |
| 2026-11-09 | 37 | 186 | 119 | 138 | 442 |

## 最慢的測試檔案（每份報告最近一次，括號是近 7 次的中位數）

### CI · pytest-report-3.12/pytest-report.xml

最近一次：2026-11-10 16:37 America/Los_Angeles（PST，UTC−08:00），合計 390 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 31.0（31.0） | 30 | `apps/server/tests/test_production_api.py` |
| 26.9（26.9） | 29 | `apps/server/tests/test_api.py` |
| 23.8（24.4） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 20.1（20.1） | 18 | `apps/cli/tests/test_serve.py` |
| 18.5（19.6） | 11 | `apps/server/tests/test_gitsync.py` |
| 17.6（17.9） | 14 | `apps/server/tests/test_workflow_api.py` |
| 15.7（16.6） | 13 | `apps/server/tests/test_replay.py` |
| 15.5（16.9） | 20 | `apps/server/tests/test_recorder_api.py` |
| 14.3（14.3） | 17 | `apps/worker/tests/test_recorder.py` |
| 14.2（14.2） | 10 | `apps/server/tests/test_videos.py` |

### CI · pytest-report-3.13/pytest-report.xml

最近一次：2026-11-10 16:37 America/Los_Angeles（PST，UTC−08:00），合計 552 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 80.0（99.7） | 12 | `apps/server/tests/test_portal.py` |
| 39.4（45.7） | 4 | `apps/server/tests/test_replay_flow.py` |
| 30.2（41.6） | 3 | `apps/server/tests/test_workflow_flow.py` |
| 25.2（31.1） | 10 | `packages/rpa_runner/tests/test_debug.py` |
| 23.2（29.0） | 5 | `apps/server/tests/test_production_flow.py` |
| 21.7（29.9） | 3 | `apps/server/tests/test_remote_worker_flow.py` |
| 19.6（19.9） | 18 | `apps/cli/tests/test_serve.py` |
| 17.6（21.7） | 15 | `apps/server/tests/test_replay.py` |
| 15.7（28.0） | 30 | `apps/server/tests/test_production_api.py` |
| 14.1（13.9） | 17 | `apps/worker/tests/test_recorder.py` |

### CI · pytest-report-windows/pytest-report.xml

最近一次：2026-11-10 16:37 America/Los_Angeles（PST，UTC−08:00），合計 906 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 212.0（224.9） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 209.6（209.6） | 26 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 147.5（122.5） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 90.4（89.1） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 66.1（61.4） | 17 | `packages\rpa_runner\tests\test_upload.py` |
| 56.4（103.1） | 10 | `packages\rpa_runner\tests\test_frames.py` |
| 54.1（45.4） | 8 | `packages\rpa_runner\tests\test_tabs.py` |
| 35.4（35.6） | 2 | `packages\rpa_runner\tests\test_download_browser.py` |
| 22.5（23.7） | 1 | `packages\rpa_runner\tests\test_profiles.py` |
| 5.5（4.6） | 2 | `tests\smoke\test_browser.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-1.xml

最近一次：2026-11-09 13:03 America/Los_Angeles（PST，UTC−08:00），合計 1556 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 179.6（179.6） | 15 | `apps/server/tests/test_portal.py` |
| 132.3（132.3） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 125.0（125.0） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 118.1（118.1） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 111.7（111.7） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 90.6（90.6） | 18 | `apps/cli/tests/test_serve.py` |
| 83.8（83.8） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 80.9（80.9） | 9 | `apps/server/tests/test_production_flow.py` |
| 58.0（58.0） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 44.9（44.9） | 4 | `apps/server/tests/test_replay_flow.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-2.xml

最近一次：2026-11-09 13:03 America/Los_Angeles（PST，UTC−08:00），合計 1059 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 163.8（163.8） | 15 | `apps/server/tests/test_portal.py` |
| 117.8（117.8） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 110.9（110.9） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 109.7（109.7） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 107.4（107.4） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 76.0（76.0） | 9 | `apps/server/tests/test_production_flow.py` |
| 60.0（60.0） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 51.9（51.9） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 43.5（43.5） | 4 | `apps/server/tests/test_replay_flow.py` |
| 31.3（31.3） | 10 | `packages/rpa_runner/tests/test_frames.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-3.xml

最近一次：2026-11-09 13:03 America/Los_Angeles（PST，UTC−08:00），合計 1172 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 179.7（179.7） | 15 | `apps/server/tests/test_portal.py` |
| 134.3（134.3） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 133.9（133.9） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 119.6（119.6） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 119.5（119.5） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 78.7（78.7） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 72.1（72.1） | 9 | `apps/server/tests/test_production_flow.py` |
| 63.0（63.0） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 43.5（43.5） | 4 | `apps/server/tests/test_replay_flow.py` |
| 33.1（33.1） | 3 | `apps/server/tests/test_flow.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.12/pass-1.xml

最近一次：2026-11-09 13:03 America/Los_Angeles（PST，UTC−08:00），合計 1123 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 117.9（117.9） | 15 | `apps/server/tests/test_portal.py` |
| 95.5（95.5） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 84.6（84.6） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 79.2（79.2） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 71.2（71.2） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 56.3（56.3） | 9 | `apps/server/tests/test_production_flow.py` |
| 52.2（52.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 45.2（45.2） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 36.2（36.2） | 4 | `apps/server/tests/test_replay_flow.py` |
| 22.0（22.0） | 4 | `apps/server/tests/test_recorder_flow.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-1.xml

最近一次：2026-11-09 13:03 America/Los_Angeles（PST，UTC−08:00），合計 955 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 105.3（105.3） | 15 | `apps/server/tests/test_portal.py` |
| 88.7（88.7） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 72.1（72.1） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 65.5（65.5） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 62.7（62.7） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 45.9（45.9） | 9 | `apps/server/tests/test_production_flow.py` |
| 43.2（43.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 38.6（38.6） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 34.8（34.8） | 4 | `apps/server/tests/test_replay_flow.py` |
| 19.8（19.8） | 18 | `apps/cli/tests/test_serve.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-2.xml

最近一次：2026-11-09 13:03 America/Los_Angeles（PST，UTC−08:00），合計 681 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 104.8（104.8） | 15 | `apps/server/tests/test_portal.py` |
| 88.8（88.8） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 70.4（70.4） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 64.5（64.5） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 52.9（52.9） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 44.8（44.8） | 9 | `apps/server/tests/test_production_flow.py` |
| 43.2（43.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 38.9（38.9） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 34.3（34.3） | 4 | `apps/server/tests/test_replay_flow.py` |
| 18.0（18.0） | 4 | `apps/server/tests/test_recorder_flow.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-3.xml

最近一次：2026-11-09 13:03 America/Los_Angeles（PST，UTC−08:00），合計 680 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 105.8（105.8） | 15 | `apps/server/tests/test_portal.py` |
| 88.4（88.4） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 70.6（70.6） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 64.9（64.9） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 51.5（51.5） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 44.5（44.5） | 9 | `apps/server/tests/test_production_flow.py` |
| 43.2（43.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 39.5（39.5） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 34.6（34.6） | 4 | `apps/server/tests/test_replay_flow.py` |
| 17.8（17.8） | 4 | `apps/server/tests/test_recorder_flow.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-1.xml

最近一次：2026-11-10 07:43 America/Los_Angeles（PST，UTC−08:00），合計 1275 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 125.6（128.8） | 15 | `apps\server\tests\test_portal.py` |
| 107.6（104.9） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 101.3（107.8） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 95.2（98.2） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 77.4（81.2） | 19 | `packages\rpa_runner\tests\test_debug.py` |
| 63.5（65.2） | 9 | `apps\server\tests\test_production_flow.py` |
| 54.6（56.2） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 49.1（52.1） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 37.7（37.7） | 4 | `apps\server\tests\test_replay_flow.py` |
| 27.0（29.1） | 11 | `apps\server\tests\test_gitsync.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-2.xml

最近一次：2026-11-09 13:03 America/Los_Angeles（PST，UTC−08:00），合計 924 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 128.1（128.1） | 15 | `apps\server\tests\test_portal.py` |
| 102.1（102.1） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 100.9（100.9） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 99.3（99.3） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 69.1（69.1） | 9 | `apps\server\tests\test_production_flow.py` |
| 69.0（69.0） | 19 | `packages\rpa_runner\tests\test_debug.py` |
| 61.2（61.2） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 52.3（52.3） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 38.1（38.1） | 4 | `apps\server\tests\test_replay_flow.py` |
| 29.0（29.0） | 17 | `packages\rpa_runner\tests\test_upload.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-3.xml

最近一次：2026-11-09 13:03 America/Los_Angeles（PST，UTC−08:00），合計 924 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 129.5（129.5） | 15 | `apps\server\tests\test_portal.py` |
| 103.9（103.9） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 100.5（100.5） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 99.4（99.4） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 70.4（70.4） | 9 | `apps\server\tests\test_production_flow.py` |
| 69.2（69.2） | 19 | `packages\rpa_runner\tests\test_debug.py` |
| 58.2（58.2） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 53.5（53.5） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 38.3（38.3） | 4 | `apps\server\tests\test_replay_flow.py` |
| 27.3（27.3） | 10 | `packages\rpa_runner\tests\test_frames.py` |

## 最近 40 次運行

| 開始（洛杉磯） | 流程 | 觸發 | 分支 | 結果 | 耗時 | 最長排隊 | 運行 |
|---|---|---|---|---|---|---|---|
| 11-10 16:53 | 一鍵安裝腳本 | PR | feat/m7-flow-control | success | 0.1 分 | 0.1 分 | [#42934854946](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42934854946/attempts/1) |
| 11-10 16:53 | 伺服器分發包 | PR | feat/m7-flow-control | success | 2.6 分 | 0.1 分 | [#42934854780](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42934854780/attempts/1) |
| 11-10 16:37 | 伺服器分發包 | PR | docs/m6-status | success | 0.1 分 | 0.0 分 | [#42932825305](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42932825305/attempts/1) |
| 11-10 16:37 | 一鍵安裝腳本 | PR | docs/m6-status | success | 0.2 分 | 0.0 分 | [#42932825248](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42932825248/attempts/1) |
| 11-10 16:37 | CI | PR | docs/m6-status | success | 3.3 分 | 0.1 分 | [#42932825256](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42932825256/attempts/1) |
| 11-10 16:37 | 伺服器分發包 | PR | feat/m7-flow-control | success | 2.3 分 | 0.1 分 | [#42932818566](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42932818566/attempts/1) |
| 11-10 16:37 | CI | PR | feat/m7-flow-control | failure | 5.2 分 | 0.1 分 | [#42932818567](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42932818567/attempts/1) |
| 11-10 16:37 | 桌面端建置 | PR | feat/m7-flow-control | success | 6.7 分 | 0.1 分 | [#42932818437](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42932818437/attempts/1) |
| 11-10 16:13 | 發布 | 推送 | v0.9.1 | success | 7.7 分 | 0.1 分 | [#42929671624](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42929671624/attempts/1) |
| 11-10 16:12 | 伺服器分發包 | 推送 | main | success | 0.2 分 | 0.1 分 | [#42929515357](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42929515357/attempts/1) |
| 11-10 16:12 | 一鍵安裝腳本 | 推送 | main | success | 0.2 分 | 0.1 分 | [#42929515310](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42929515310/attempts/1) |
| 11-10 16:12 | CI | 推送 | main | failure | 9.1 分 | 0.1 分 | [#42929515342](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42929515342/attempts/1) |
| 11-10 16:07 | 伺服器分發包 | PR | chore/release-0.9.1 | success | 0.1 分 | 0.1 分 | [#42928899814](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42928899814/attempts/1) |
| 11-10 16:07 | 一鍵安裝腳本 | PR | chore/release-0.9.1 | success | 0.2 分 | 0.1 分 | [#42928899887](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42928899887/attempts/1) |
| 11-10 16:07 | CI | PR | chore/release-0.9.1 | success | 2.3 分 | 0.1 分 | [#42928899965](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42928899965/attempts/1) |
| 11-10 16:02 | 一鍵安裝腳本 | PR | chore/release-0.9.1 | success | 0.1 分 | 0.0 分 | [#42928193031](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42928193031/attempts/1) |
| 11-10 16:02 | 伺服器分發包 | PR | chore/release-0.9.1 | success | 0.2 分 | 0.0 分 | [#42928193182](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42928193182/attempts/1) |
| 11-10 16:02 | CI | PR | chore/release-0.9.1 | success | 4.7 分 | 0.1 分 | [#42928193050](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42928193050/attempts/1) |
| 11-10 15:58 | 發布 | 推送 | v0.9.0 | success | 8.2 分 | 0.1 分 | [#42786155487 第 2 次](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42786155487/attempts/2) |
| 11-10 15:56 | 桌面端建置 | 推送 | main | success | 0.1 分 | 0.1 分 | [#42927345690](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42927345690/attempts/1) |
| 11-10 15:56 | 伺服器分發包 | 推送 | main | success | 0.2 分 | 0.1 分 | [#42927345609](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42927345609/attempts/1) |
| 11-10 15:56 | CI | 推送 | main | success | 8.2 分 | 0.1 分 | [#42927345766](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42927345766/attempts/1) |
| 11-10 07:47 | 一鍵安裝腳本 | PR | fix/json-scene-sections | success | 0.2 分 | 0.1 分 | [#42847985514](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42847985514/attempts/1) |
| 11-10 07:47 | 伺服器分發包 | PR | fix/json-scene-sections | success | 2.8 分 | 0.1 分 | [#42847985630](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42847985630/attempts/1) |
| 11-10 07:47 | 桌面端建置 | PR | fix/json-scene-sections | success | 3.0 分 | 0.1 分 | [#42847985540](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42847985540/attempts/1) |
| 11-10 07:47 | CI | PR | fix/json-scene-sections | success | 5.3 分 | 0.1 分 | [#42847985615](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42847985615/attempts/1) |
| 11-10 07:44 | 桌面端建置 | 推送 | main | success | 0.2 分 | 0.1 分 | [#42847532709](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42847532709/attempts/1) |
| 11-10 07:44 | 一鍵安裝腳本 | 推送 | main | success | 0.2 分 | 0.1 分 | [#42847532714](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42847532714/attempts/1) |
| 11-10 07:44 | CI | 推送 | main | success | 7.8 分 | 0.1 分 | [#42847532856](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42847532856/attempts/1) |
| 11-10 07:43 | 每晚完整測試 | 手動 | main | success | 22.5 分 | 0.1 分 | [#42847296159](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42847296159/attempts/1) |
| 11-10 07:27 | 伺服器分發包 | PR | feat/login-locator-guide | success | 0.2 分 | 0.1 分 | [#42844572816](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42844572816/attempts/1) |
| 11-10 07:27 | 一鍵安裝腳本 | PR | feat/login-locator-guide | success | 0.2 分 | 0.1 分 | [#42844572993](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42844572993/attempts/1) |
| 11-10 07:27 | CI | PR | feat/login-locator-guide | success | 2.5 分 | 0.1 分 | [#42844572800](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42844572800/attempts/1) |
| 11-10 07:20 | 桌面端建置 | PR | feat/login-locator-guide | success | 6.2 分 | 0.1 分 | [#42843257654](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42843257654/attempts/1) |
| 11-10 07:20 | CI | PR | feat/login-locator-guide | success | 5.3 分 | 0.1 分 | [#42843257444](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42843257444/attempts/1) |
| 11-10 07:20 | 伺服器分發包 | PR | feat/login-locator-guide | success | 2.6 分 | 0.1 分 | [#42843257347](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42843257347/attempts/1) |
| 11-10 07:19 | 一鍵安裝腳本 | PR | feat/login-locator-guide | success | 0.3 分 | 0.1 分 | [#42843145781](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42843145781/attempts/1) |
| 11-10 07:19 | 桌面端建置 | PR | feat/login-locator-guide | cancelled | 1.0 分 | 0.1 分 | [#42843145836](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42843145836/attempts/1) |
| 11-10 07:18 | 伺服器分發包 | PR | fix/json-scene-sections | success | 0.1 分 | 0.1 分 | [#42842909226](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42842909226/attempts/1) |
| 11-10 07:18 | 一鍵安裝腳本 | PR | fix/json-scene-sections | success | 0.2 分 | 0.0 分 | [#42842909244](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42842909244/attempts/1) |

