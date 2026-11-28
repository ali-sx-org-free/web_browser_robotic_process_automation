# CI 運行耗時紀錄

更新：2026-11-28 00:47 America/Los_Angeles（PST，UTC−08:00）。共 486 次運行。

每次 CI、桌面端建置、一鍵安裝腳本、每晚完整測試、發布結束後，由 `.github/workflows/ci-metrics.yml` 追加到 `data/`；本頁由 `tools/ci_metrics.py report` 產生，不要手改。耗時＝第一個工作建立到最後一個工作結束（含排隊）；機器時間＝各工作實際執行的時間總和。
規則與背景見 main 的 `docs/develop/ci.html`。

## 各流程：近 7 天（前 7 天）

| 流程 | 次數 | 通過 | 耗時中位數 | 耗時 P90 | 最長排隊中位數 | 機器時間（Linux／Windows／macOS） |
|---|---|---|---|---|---|---|
| CI | 39（34） | 27（21） | 5.4 分（4.6 分） | 9.1 分（8.6 分） | 0.1 分（0.1 分） | 329／62／0 分（260／32／0 分） |
| 桌面端建置 | 28（24） | 26（20） | 0.2 分（0.2 分） | 6.7 分（6.4 分） | 0.1 分（0.1 分） | 4／41／39 分（3／29／47 分） |
| 伺服器分發包 | 35（27） | 34（24） | 0.3 分（0.2 分） | 2.8 分（2.8 分） | 0.1 分（0.1 分） | 81／0／0 分（51／0／0 分） |
| 一鍵安裝腳本 | 38（31） | 36（30） | 0.2 分（0.2 分） | 32.7 分（32.8 分） | 0.1 分（0.1 分） | 257／340／345 分（235／304／298 分） |
| 每晚完整測試 | 14（8） | 12（7） | 73.0 分（73.3 分） | 80.4 分（78.5 分） | 0.1 分（0.1 分） | 751／673／724 分（515／473／598 分） |
| 發布 | 2（2） | 2（2） | 7.6 分（8.1 分） | 8.2 分（8.3 分） | 0.1 分（0.1 分） | 11／10／22 分（11／11／23 分） |

## 每天的機器時間（分鐘，洛杉磯日期，最近 14 天）

| 日期 | 運行次數 | Linux | Windows | macOS | 合計 |
|---|---|---|---|---|---|
| 2026-11-28 | 8 | 15 | 13 | 0 | 28 |
| 2026-11-27 | 96 | 428 | 186 | 251 | 865 |
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

## 最慢的測試檔案（每份報告最近一次，括號是近 7 次的中位數）

### CI · pytest-report-3.12/pytest-report.xml

最近一次：2026-11-28 00:38 America/Los_Angeles（PST，UTC−08:00），合計 417 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 24.6（30.4） | 30 | `apps/server/tests/test_production_api.py` |
| 21.8（23.9） | 21 | `apps/server/tests/test_workflow_api.py` |
| 20.3（23.6） | 29 | `apps/server/tests/test_api.py` |
| 20.3（20.5） | 18 | `apps/cli/tests/test_serve.py` |
| 19.4（22.1） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 16.6（19.7） | 20 | `apps/server/tests/test_recorder_api.py` |
| 16.2（20.4） | 12 | `apps/server/tests/test_gitsync.py` |
| 15.0（14.6） | 15 | `apps/worker/tests/test_gateway.py` |
| 13.8（13.8） | 17 | `apps/worker/tests/test_recorder.py` |
| 12.6（18.6） | 13 | `apps/server/tests/test_replay.py` |

### CI · pytest-report-3.13/pytest-report.xml

最近一次：2026-11-28 00:38 America/Los_Angeles（PST，UTC−08:00），合計 857 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 96.1（112.8） | 13 | `apps/server/tests/test_portal.py` |
| 44.0（49.8） | 3 | `apps/server/tests/test_workflow_flow.py` |
| 42.2（46.9） | 4 | `apps/server/tests/test_replay_flow.py` |
| 32.1（33.5） | 30 | `apps/server/tests/test_production_api.py` |
| 30.7（36.2） | 12 | `packages/rpa_runner/tests/test_debug.py` |
| 26.8（29.0） | 29 | `apps/server/tests/test_api.py` |
| 26.6（31.1） | 3 | `apps/server/tests/test_remote_worker_flow.py` |
| 26.1（30.9） | 5 | `apps/server/tests/test_production_flow.py` |
| 23.7（28.6） | 21 | `apps/server/tests/test_workflow_api.py` |
| 22.3（26.4） | 22 | `apps/server/tests/test_remote_worker_api.py` |

### CI · pytest-report-windows/pytest-report.xml

最近一次：2026-11-28 00:38 America/Los_Angeles（PST，UTC−08:00），合計 964 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 184.3（227.6） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 166.8（136.8） | 21 | `packages\rpa_runner\tests\test_video_browser.py` |
| 163.9（184.9） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 144.3（159.2） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |
| 81.8（98.6） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 58.3（62.4） | 17 | `packages\rpa_runner\tests\test_upload.py` |
| 50.4（51.5） | 10 | `packages\rpa_runner\tests\test_frames.py` |
| 47.4（56.0） | 8 | `packages\rpa_runner\tests\test_tabs.py` |
| 33.9（33.9） | 2 | `packages\rpa_runner\tests\test_download_browser.py` |
| 20.4（25.0） | 1 | `packages\rpa_runner\tests\test_profiles.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-1.xml

最近一次：2026-11-27 18:42 America/Los_Angeles（PST，UTC−08:00），合計 2164 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 220.8（186.9） | 16 | `apps/server/tests/test_portal.py` |
| 140.4（118.1） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 133.3（119.0） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 131.9（131.9） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 118.4（118.4） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 118.2（92.2） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 115.4（93.9） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 100.8（81.6） | 9 | `apps/server/tests/test_production_flow.py` |
| 92.2（69.9） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 90.3（90.7） | 18 | `apps/cli/tests/test_serve.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-2.xml

最近一次：2026-11-27 18:42 America/Los_Angeles（PST，UTC−08:00），合計 1256 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 147.7（167.8） | 16 | `apps/server/tests/test_portal.py` |
| 125.8（102.2） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 117.4（110.0） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 108.4（92.2） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 102.5（81.4） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 99.4（114.9） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 78.4（94.6） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 61.1（78.2） | 9 | `apps/server/tests/test_production_flow.py` |
| 59.3（79.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 51.5（53.5） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-3.xml

最近一次：2026-11-27 18:42 America/Los_Angeles（PST，UTC−08:00），合計 1311 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 173.7（169.1） | 16 | `apps/server/tests/test_portal.py` |
| 128.8（126.4） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 120.2（110.6） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 98.5（91.1） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 91.3（96.5） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 89.5（88.4） | 9 | `apps/server/tests/test_production_flow.py` |
| 86.4（89.2） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 78.8（81.3） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 78.3（81.8） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 59.7（52.5） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.12/pass-1.xml

最近一次：2026-11-27 18:42 America/Los_Angeles（PST，UTC−08:00），合計 1199 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 113.1（107.8） | 16 | `apps/server/tests/test_portal.py` |
| 89.4（87.7） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 72.8（70.6） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 65.5（62.2） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 59.9（58.3） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 58.2（54.8） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 47.5（47.1） | 9 | `apps/server/tests/test_production_flow.py` |
| 46.5（42.9） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 43.9（43.9） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 38.6（37.8） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-1.xml

最近一次：2026-11-27 18:42 America/Los_Angeles（PST，UTC−08:00），合計 1312 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 121.2（121.5） | 16 | `apps/server/tests/test_portal.py` |
| 94.5（94.3） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 83.0（82.7） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 74.9（75.6） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 66.1（66.3） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 64.6（62.7） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 53.9（55.0） | 9 | `apps/server/tests/test_production_flow.py` |
| 48.6（48.4） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 47.3（49.3） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 43.3（43.3） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-2.xml

最近一次：2026-11-27 18:42 America/Los_Angeles（PST，UTC−08:00），合計 924 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 120.5（120.2） | 16 | `apps/server/tests/test_portal.py` |
| 95.4（94.8） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 82.1（82.2） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 76.9（75.9） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 66.9（66.6） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 64.6（62.0） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 54.4（54.8） | 9 | `apps/server/tests/test_production_flow.py` |
| 47.2（53.0） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 43.5（43.1） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 37.8（37.7） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-3.xml

最近一次：2026-11-27 18:42 America/Los_Angeles（PST，UTC−08:00），合計 914 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 119.4（119.3） | 16 | `apps/server/tests/test_portal.py` |
| 93.9（94.1） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 82.1（82.1） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 75.2（75.0） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 66.1（66.2） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 64.4（62.8） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 54.1（54.6） | 9 | `apps/server/tests/test_production_flow.py` |
| 45.2（51.5） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 42.9（43.2） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 38.1（37.9） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-1.xml

最近一次：2026-11-27 18:42 America/Los_Angeles（PST，UTC−08:00），合計 1557 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 128.9（134.0） | 16 | `apps\server\tests\test_portal.py` |
| 97.8（99.4） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 95.1（94.0） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 93.8（102.1） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 83.5（78.0） | 23 | `packages\rpa_runner\tests\test_debug.py` |
| 73.4（78.2） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 63.4（67.6） | 9 | `apps\server\tests\test_production_flow.py` |
| 58.9（72.1） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |
| 57.5（62.6） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 50.7（60.0） | 20 | `packages\rpa_runner\tests\test_run.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-2.xml

最近一次：2026-11-27 18:42 America/Los_Angeles（PST，UTC−08:00），合計 1038 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 127.2（127.9） | 16 | `apps\server\tests\test_portal.py` |
| 97.4（98.8） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 95.1（95.1） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 91.6（100.2） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 72.5（76.4） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 71.7（76.7） | 23 | `packages\rpa_runner\tests\test_debug.py` |
| 62.9（66.6） | 9 | `apps\server\tests\test_production_flow.py` |
| 60.8（56.6） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 48.2（51.2） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 45.8（47.4） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-3.xml

最近一次：2026-11-27 18:42 America/Los_Angeles（PST，UTC−08:00），合計 1050 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 129.3（134.6） | 16 | `apps\server\tests\test_portal.py` |
| 97.3（99.2） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 93.8（95.1） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 93.2（107.6） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 75.6（75.0） | 23 | `packages\rpa_runner\tests\test_debug.py` |
| 73.0（74.2） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 64.1（67.6） | 9 | `apps\server\tests\test_production_flow.py` |
| 58.8（61.1） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 49.9（51.9） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 45.2（47.5） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |

## 最近 40 次運行

| 開始（洛杉磯） | 流程 | 觸發 | 分支 | 結果 | 耗時 | 最長排隊 | 運行 |
|---|---|---|---|---|---|---|---|
| 11-28 00:47 | 伺服器分發包 | PR | claude/project-thread-louap6 | success | 0.2 分 | 0.1 分 | [#46127421687](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46127421687/attempts/1) |
| 11-28 00:47 | 一鍵安裝腳本 | PR | claude/project-thread-louap6 | success | 0.3 分 | 0.1 分 | [#46127421735](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46127421735/attempts/1) |
| 11-28 00:38 | CI | PR | claude/project-thread-louap6 | success | 5.4 分 | 0.1 分 | [#46126728445](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46126728445/attempts/1) |
| 11-28 00:38 | 伺服器分發包 | PR | claude/project-thread-louap6 | success | 2.7 分 | 0.1 分 | [#46126728205](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46126728205/attempts/1) |
| 11-28 00:38 | 桌面端建置 | PR | claude/project-thread-louap6 | success | 7.2 分 | 0.1 分 | [#46126728171](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46126728171/attempts/1) |
| 11-28 00:37 | 一鍵安裝腳本 | PR | claude/project-thread-louap6 | success | 0.2 分 | 0.1 分 | [#46126689688](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46126689688/attempts/1) |
| 11-28 00:37 | 桌面端建置 | PR | claude/project-thread-louap6 | cancelled | 0.7 分 | 0.1 分 | [#46126689723](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46126689723/attempts/1) |
| 11-28 00:37 | CI | PR | claude/project-thread-louap6 | cancelled | 0.8 分 | 0.1 分 | [#46126689800](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46126689800/attempts/1) |
| 11-27 20:35 | CI | PR | chore/server-upgrade-0.11.0 | success | 5.3 分 | 0.1 分 | [#46108270832](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46108270832/attempts/1) |
| 11-27 20:35 | 一鍵安裝腳本 | PR | chore/server-upgrade-0.11.0 | success | 0.2 分 | 0.0 分 | [#46108270775](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46108270775/attempts/1) |
| 11-27 20:35 | 桌面端建置 | PR | chore/server-upgrade-0.11.0 | success | 0.1 分 | 0.0 分 | [#46108232753](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46108232753/attempts/1) |
| 11-27 20:35 | 一鍵安裝腳本 | PR | chore/server-upgrade-0.11.0 | success | 0.2 分 | 0.0 分 | [#46108232732](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46108232732/attempts/1) |
| 11-27 20:35 | CI | PR | chore/server-upgrade-0.11.0 | cancelled | 0.7 分 | 0.1 分 | [#46108232712](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46108232712/attempts/1) |
| 11-27 20:31 | 發布 | 推送 | v0.12.0 | success | 8.2 分 | 0.1 分 | [#46107919470](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46107919470/attempts/1) |
| 11-27 20:29 | 伺服器分發包 | 推送 | main | success | 0.1 分 | 0.0 分 | [#46107755429](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46107755429/attempts/1) |
| 11-27 20:29 | 一鍵安裝腳本 | 推送 | main | success | 0.1 分 | 0.0 分 | [#46107755454](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46107755454/attempts/1) |
| 11-27 20:29 | CI | 推送 | main | failure | 8.2 分 | 0.0 分 | [#46107755451](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46107755451/attempts/1) |
| 11-27 20:09 | 桌面端建置 | PR | claude/project-thread-70yx5u | success | 0.1 分 | 0.0 分 | [#46106194815](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46106194815/attempts/1) |
| 11-27 20:09 | CI | PR | claude/project-thread-70yx5u | success | 2.5 分 | 0.1 分 | [#46106194863](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46106194863/attempts/1) |
| 11-27 20:09 | 一鍵安裝腳本 | PR | claude/project-thread-70yx5u | success | 0.2 分 | 0.1 分 | [#46106194816](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46106194816/attempts/1) |
| 11-27 20:02 | CI | PR | claude/project-thread-70yx5u | success | 5.5 分 | 0.1 分 | [#46105672518](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46105672518/attempts/1) |
| 11-27 20:02 | 桌面端建置 | PR | claude/project-thread-70yx5u | success | 0.2 分 | 0.0 分 | [#46105672494](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46105672494/attempts/1) |
| 11-27 20:02 | 伺服器分發包 | PR | claude/project-thread-70yx5u | success | 0.1 分 | 0.0 分 | [#46105653130](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46105653130/attempts/1) |
| 11-27 20:02 | 一鍵安裝腳本 | PR | claude/project-thread-70yx5u | success | 0.2 分 | 0.1 分 | [#46105653132](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46105653132/attempts/1) |
| 11-27 20:02 | CI | PR | claude/project-thread-70yx5u | cancelled | 0.5 分 | 0.1 分 | [#46105653112](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46105653112/attempts/1) |
| 11-27 19:59 | CI | 推送 | main | failure | 11.0 分 | 0.1 分 | [#46105386898](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46105386898/attempts/1) |
| 11-27 19:59 | 伺服器分發包 | 推送 | main | success | 0.1 分 | 0.1 分 | [#46105386873](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46105386873/attempts/1) |
| 11-27 19:57 | 伺服器分發包 | 推送 | main | success | 0.1 分 | 0.0 分 | [#46105262637](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46105262637/attempts/1) |
| 11-27 19:57 | 一鍵安裝腳本 | 推送 | main | success | 0.2 分 | 0.0 分 | [#46105262612](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46105262612/attempts/1) |
| 11-27 19:57 | CI | 推送 | main | cancelled | 2.0 分 | 0.1 分 | [#46105262585](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46105262585/attempts/1) |
| 11-27 18:57 | 一鍵安裝腳本 | 排程 | main | failure | 33.4 分 | 0.1 分 | [#46100551790](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46100551790/attempts/1) |
| 11-27 18:42 | 每晚完整測試 | 排程 | main | success | 80.4 分 | 0.1 分 | [#46099408414](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46099408414/attempts/1) |
| 11-27 05:43 | CI | PR | claude/project-thread-70yx5u | success | 5.6 分 | 0.1 分 | [#46009524897](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46009524897/attempts/1) |
| 11-27 05:43 | 伺服器分發包 | PR | claude/project-thread-70yx5u | success | 2.9 分 | 0.2 分 | [#46009524765](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46009524765/attempts/1) |
| 11-27 05:43 | 一鍵安裝腳本 | PR | claude/project-thread-70yx5u | success | 0.2 分 | 0.0 分 | [#46009524640](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46009524640/attempts/1) |
| 11-27 05:43 | 一鍵安裝腳本 | PR | claude/project-thread-70yx5u | success | 0.2 分 | 0.1 分 | [#46009499723](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46009499723/attempts/1) |
| 11-27 05:30 | 桌面端建置 | PR | claude/project-thread-70yx5u | success | 0.2 分 | 0.1 分 | [#46007636226](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46007636226/attempts/1) |
| 11-27 05:30 | 一鍵安裝腳本 | PR | claude/project-thread-70yx5u | success | 0.2 分 | 0.1 分 | [#46007636262](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46007636262/attempts/1) |
| 11-27 05:30 | 伺服器分發包 | PR | claude/project-thread-70yx5u | success | 2.6 分 | 0.1 分 | [#46007636304](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46007636304/attempts/1) |
| 11-27 05:30 | CI | PR | claude/project-thread-70yx5u | success | 5.7 分 | 0.1 分 | [#46007636366](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/46007636366/attempts/1) |

