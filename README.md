# CI 運行耗時紀錄

更新：2026-11-12 18:35 America/Los_Angeles（PST，UTC−08:00）。共 145 次運行。

每次 CI、桌面端建置、一鍵安裝腳本、每晚完整測試、發布結束後，由 `.github/workflows/ci-metrics.yml` 追加到 `data/`；本頁由 `tools/ci_metrics.py report` 產生，不要手改。耗時＝第一個工作建立到最後一個工作結束（含排隊）；機器時間＝各工作實際執行的時間總和。
規則與背景見 main 的 `docs/develop/ci.html`。

## 各流程：近 7 天（前 7 天）

| 流程 | 次數 | 通過 | 耗時中位數 | 耗時 P90 | 最長排隊中位數 | 機器時間（Linux／Windows／macOS） |
|---|---|---|---|---|---|---|
| CI | 41（0） | 31（0） | 4.7 分（0.0 分） | 8.7 分（0.0 分） | 0.1 分（0.0 分） | 322／50／0 分（0／0／0 分） |
| 桌面端建置 | 28（0） | 27（0） | 0.2 分（0.0 分） | 6.3 分（0.0 分） | 0.1 分（0.0 分） | 3／49／42 分（0／0／0 分） |
| 伺服器分發包 | 32（0） | 31（0） | 0.2 分（0.0 分） | 2.7 分（0.0 分） | 0.1 分（0.0 分） | 55／0／0 分（0／0／0 分） |
| 一鍵安裝腳本 | 36（0） | 33（0） | 0.2 分（0.0 分） | 26.0 分（0.0 分） | 0.1 分（0.0 分） | 115／146／146 分（0／0／0 分） |
| 每晚完整測試 | 5（0） | 3（0） | 58.9 分（0.0 分） | 64.9 分（0.0 分） | 0.1 分（0.0 分） | 255／246／268 分（0／0／0 分） |
| 發布 | 3（0） | 3（0） | 8.0 分（0.0 分） | 8.2 分（0.0 分） | 0.1 分（0.0 分） | 16／16／34 分（0／0／0 分） |

## 每天的機器時間（分鐘，洛杉磯日期，最近 14 天）

| 日期 | 運行次數 | Linux | Windows | macOS | 合計 |
|---|---|---|---|---|---|
| 2026-11-12 | 6 | 105 | 92 | 104 | 301 |
| 2026-11-11 | 41 | 210 | 120 | 96 | 426 |
| 2026-11-10 | 61 | 265 | 177 | 153 | 595 |
| 2026-11-09 | 37 | 186 | 119 | 138 | 442 |

## 最慢的測試檔案（每份報告最近一次，括號是近 7 次的中位數）

### CI · pytest-report-3.12/pytest-report.xml

最近一次：2026-11-12 16:01 America/Los_Angeles（PST，UTC−08:00），合計 1726 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 192.3（191.4） | 16 | `apps/server/tests/test_portal.py` |
| 135.6（132.1） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 126.7（119.7） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 124.1（122.2） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 98.5（96.0） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 95.6（93.0） | 9 | `apps/server/tests/test_production_flow.py` |
| 83.3（82.9） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 77.0（71.7） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 49.5（46.9） | 4 | `apps/server/tests/test_replay_flow.py` |
| 33.0（16.9） | 15 | `apps/server/tests/test_replay.py` |

### CI · pytest-report-3.13/pytest-report.xml

最近一次：2026-11-12 16:01 America/Los_Angeles（PST，UTC−08:00），合計 605 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 86.3（99.0） | 13 | `apps/server/tests/test_portal.py` |
| 41.3（43.0） | 4 | `apps/server/tests/test_replay_flow.py` |
| 33.3（37.6） | 3 | `apps/server/tests/test_workflow_flow.py` |
| 26.3（29.8） | 10 | `packages/rpa_runner/tests/test_debug.py` |
| 24.8（28.1） | 5 | `apps/server/tests/test_production_flow.py` |
| 20.3（26.9） | 3 | `apps/server/tests/test_remote_worker_flow.py` |
| 19.8（25.9） | 30 | `apps/server/tests/test_production_api.py` |
| 19.7（20.2） | 18 | `apps/cli/tests/test_serve.py` |
| 17.8（15.4） | 15 | `apps/server/tests/test_replay.py` |
| 16.7（21.1） | 29 | `apps/server/tests/test_api.py` |

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

最近一次：2026-11-12 17:06 America/Los_Angeles（PST，UTC−08:00），合計 1379 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 163.4（166.2） | 16 | `apps/server/tests/test_portal.py` |
| 121.2（126.8） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 110.3（117.7） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 104.9（109.1） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 90.0（89.9） | 18 | `apps/cli/tests/test_serve.py` |
| 82.4（97.1） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 78.8（71.5） | 9 | `apps/server/tests/test_production_flow.py` |
| 77.4（67.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 45.4（51.7） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 43.1（43.2） | 4 | `apps/server/tests/test_replay_flow.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-2.xml

最近一次：2026-11-12 17:06 America/Los_Angeles（PST，UTC−08:00），合計 1020 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 168.9（159.9） | 16 | `apps/server/tests/test_portal.py` |
| 112.4（107.3） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 110.1（107.9） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 109.1（109.0） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 84.2（97.0） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 64.3（62.1） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 63.1（69.5） | 9 | `apps/server/tests/test_production_flow.py` |
| 51.0（51.5） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 40.2（41.5） | 4 | `apps/server/tests/test_replay_flow.py` |
| 27.1（27.4） | 17 | `packages/rpa_runner/tests/test_upload.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-3.xml

最近一次：2026-11-12 17:06 America/Los_Angeles（PST，UTC−08:00），合計 995 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 142.4（150.4） | 16 | `apps/server/tests/test_portal.py` |
| 117.5（110.5） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 109.6（113.8） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 101.3（103.3） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 77.7（74.9） | 9 | `apps/server/tests/test_production_flow.py` |
| 77.4（75.9） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 73.2（80.5） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 50.6（49.3） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 44.3（43.2） | 4 | `apps/server/tests/test_replay_flow.py` |
| 26.0（25.6） | 4 | `apps/server/tests/test_recorder_flow.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.12/pass-1.xml

最近一次：2026-11-12 17:06 America/Los_Angeles（PST，UTC−08:00），合計 943 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 106.3（114.3） | 16 | `apps/server/tests/test_portal.py` |
| 87.9（93.0） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 65.2（79.3） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 59.8（73.7） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 56.7（66.8） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 46.2（49.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 43.1（52.1） | 9 | `apps/server/tests/test_production_flow.py` |
| 36.8（42.9） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 34.7（35.5） | 4 | `apps/server/tests/test_replay_flow.py` |
| 19.8（20.1） | 18 | `apps/cli/tests/test_serve.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-1.xml

最近一次：2026-11-12 17:06 America/Los_Angeles（PST，UTC−08:00），合計 1137 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 121.3（117.8） | 16 | `apps/server/tests/test_portal.py` |
| 96.9（95.2） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 84.5（83.7） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 82.2（79.8） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 74.5（69.4） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 56.7（55.6） | 9 | `apps/server/tests/test_production_flow.py` |
| 48.4（48.6） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 45.9（44.5） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 36.5（36.0） | 4 | `apps/server/tests/test_replay_flow.py` |
| 23.0（22.8） | 30 | `apps/server/tests/test_production_api.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-2.xml

最近一次：2026-11-12 17:06 America/Los_Angeles（PST，UTC−08:00），合計 809 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 120.2（116.2） | 16 | `apps/server/tests/test_portal.py` |
| 95.7（95.2） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 84.8（83.1） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 79.1（78.4） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 61.2（60.5） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 56.0（55.2） | 9 | `apps/server/tests/test_production_flow.py` |
| 47.2（47.8） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 45.0（44.6） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 37.0（36.5） | 4 | `apps/server/tests/test_replay_flow.py` |
| 21.3（21.5） | 4 | `apps/server/tests/test_recorder_flow.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-3.xml

最近一次：2026-11-12 17:06 America/Los_Angeles（PST，UTC−08:00），合計 814 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 120.9（117.0） | 16 | `apps/server/tests/test_portal.py` |
| 95.9（95.1） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 84.6（82.6） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 78.9（78.3） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 61.1（60.8） | 19 | `packages/rpa_runner/tests/test_debug.py` |
| 56.3（55.1） | 9 | `apps/server/tests/test_production_flow.py` |
| 50.0（49.5） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 44.8（44.4） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 37.0（36.5） | 4 | `apps/server/tests/test_replay_flow.py` |
| 21.5（21.3） | 4 | `apps/server/tests/test_recorder_flow.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-1.xml

最近一次：2026-11-12 17:06 America/Los_Angeles（PST，UTC−08:00），合計 1454 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 136.8（132.1） | 16 | `apps\server\tests\test_portal.py` |
| 118.6（110.8） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 102.2（107.6） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 101.2（101.1） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 84.5（84.9） | 19 | `packages\rpa_runner\tests\test_debug.py` |
| 77.3（67.0） | 9 | `apps\server\tests\test_production_flow.py` |
| 62.2（60.3） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 52.3（52.3） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 36.8（37.7） | 4 | `apps\server\tests\test_replay_flow.py` |
| 32.2（27.2） | 30 | `apps\server\tests\test_production_api.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-2.xml

最近一次：2026-11-12 17:06 America/Los_Angeles（PST，UTC−08:00），合計 989 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 142.5（134.6） | 16 | `apps\server\tests\test_portal.py` |
| 104.2（100.4） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 99.9（101.0） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 99.4（100.2） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 72.5（70.1） | 9 | `apps\server\tests\test_production_flow.py` |
| 72.3（63.1） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 72.3（70.7） | 19 | `packages\rpa_runner\tests\test_debug.py` |
| 55.5（53.9） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 38.9（38.2） | 4 | `apps\server\tests\test_replay_flow.py` |
| 29.3（26.9） | 10 | `packages\rpa_runner\tests\test_frames.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-3.xml

最近一次：2026-11-12 17:06 America/Los_Angeles（PST，UTC−08:00），合計 975 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 130.9（130.2） | 16 | `apps\server\tests\test_portal.py` |
| 109.5（103.6） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 100.6（100.0） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 100.3（100.4） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 70.6（70.2） | 19 | `packages\rpa_runner\tests\test_debug.py` |
| 68.3（69.2） | 9 | `apps\server\tests\test_production_flow.py` |
| 57.9（58.0） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 56.9（53.6） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 39.3（38.6） | 4 | `apps\server\tests\test_replay_flow.py` |
| 28.9（26.6） | 10 | `packages\rpa_runner\tests\test_frames.py` |

## 最近 40 次運行

| 開始（洛杉磯） | 流程 | 觸發 | 分支 | 結果 | 耗時 | 最長排隊 | 運行 |
|---|---|---|---|---|---|---|---|
| 11-12 18:35 | 伺服器分發包 | PR | claude/project-thread-0k55i9 | success | 0.1 分 | 0.0 分 | [#43353251265](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43353251265/attempts/1) |
| 11-12 17:29 | 一鍵安裝腳本 | 排程 | main | failure | 28.5 分 | 0.1 分 | [#43345289668](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43345289668/attempts/1) |
| 11-12 17:06 | 每晚完整測試 | 排程 | main | success | 58.5 分 | 0.1 分 | [#43342282371](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43342282371/attempts/1) |
| 11-12 16:01 | 一鍵安裝腳本 | 推送 | main | success | 0.1 分 | 0.1 分 | [#43333669594](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43333669594/attempts/1) |
| 11-12 16:01 | 桌面端建置 | 推送 | main | success | 0.2 分 | 0.1 分 | [#43333669650](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43333669650/attempts/1) |
| 11-12 16:01 | CI | 推送 | main | failure | 8.8 分 | 0.1 分 | [#43333669974](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/43333669974/attempts/1) |
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

