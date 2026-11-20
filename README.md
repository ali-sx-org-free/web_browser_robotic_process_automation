# CI 運行耗時紀錄

更新：2026-11-19 18:28 America/Los_Angeles（PST，UTC−08:00）。共 303 次運行。

每次 CI、桌面端建置、一鍵安裝腳本、每晚完整測試、發布結束後，由 `.github/workflows/ci-metrics.yml` 追加到 `data/`；本頁由 `tools/ci_metrics.py report` 產生，不要手改。耗時＝第一個工作建立到最後一個工作結束（含排隊）；機器時間＝各工作實際執行的時間總和。
規則與背景見 main 的 `docs/develop/ci.html`。

## 各流程：近 7 天（前 7 天）

| 流程 | 次數 | 通過 | 耗時中位數 | 耗時 P90 | 最長排隊中位數 | 機器時間（Linux／Windows／macOS） |
|---|---|---|---|---|---|---|
| CI | 45（41） | 26（31） | 4.8 分（4.7 分） | 7.6 分（8.7 分） | 0.1 分（0.1 分） | 315／82／0 分（322／50／0 分） |
| 桌面端建置 | 31（28） | 27（27） | 0.2 分（0.2 分） | 5.8 分（6.3 分） | 0.1 分（0.1 分） | 5／37／47 分（3／49／42 分） |
| 伺服器分發包 | 36（31） | 33（30） | 0.3 分（0.2 分） | 2.8 分（2.7 分） | 0.1 分（0.1 分） | 70／0／0 分（55／0／0 分） |
| 一鍵安裝腳本 | 39（36） | 38（33） | 0.2 分（0.2 分） | 31.0 分（26.0 分） | 0.1 分（0.1 分） | 230／297／296 分（115／146／146 分） |
| 每晚完整測試 | 7（5） | 6（3） | 71.0 分（58.9 分） | 78.5 分（64.9 分） | 0.1 分（0.1 分） | 443／406／505 分（255／246／268 分） |
| 發布 | 1（3） | 1（3） | 7.8 分（8.0 分） | 7.8 分（8.2 分） | 0.1 分（0.1 分） | 5／6／11 分（16／16／34 分） |

## 每天的機器時間（分鐘，洛杉磯日期，最近 14 天）

| 日期 | 運行次數 | Linux | Windows | macOS | 合計 |
|---|---|---|---|---|---|
| 2026-11-19 | 1 | 35 | 42 | 43 | 121 |
| 2026-11-18 | 2 | 112 | 113 | 131 | 356 |
| 2026-11-17 | 2 | 116 | 111 | 133 | 361 |
| 2026-11-16 | 16 | 152 | 115 | 138 | 405 |
| 2026-11-15 | 2 | 98 | 113 | 123 | 335 |
| 2026-11-14 | 76 | 310 | 172 | 171 | 652 |
| 2026-11-13 | 53 | 233 | 157 | 120 | 509 |
| 2026-11-12 | 12 | 117 | 97 | 104 | 318 |
| 2026-11-11 | 41 | 210 | 120 | 96 | 426 |
| 2026-11-10 | 61 | 265 | 177 | 153 | 595 |
| 2026-11-09 | 37 | 186 | 119 | 138 | 442 |

## 最慢的測試檔案（每份報告最近一次，括號是近 7 次的中位數）

### CI · pytest-report-3.12/pytest-report.xml

最近一次：2026-11-16 21:54 America/Los_Angeles（PST，UTC−08:00），合計 1793 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 169.2（188.8） | 16 | `apps/server/tests/test_portal.py` |
| 115.7（129.2） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 114.8（121.2） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 102.7（116.9） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 94.4（103.6） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 93.5（103.0） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 77.8（88.8） | 9 | `apps/server/tests/test_production_flow.py` |
| 65.5（78.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 60.8（69.1） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 56.6（64.6） | 20 | `packages/rpa_runner/tests/test_run.py` |

### CI · pytest-report-3.13/pytest-report.xml

最近一次：2026-11-16 21:54 America/Los_Angeles（PST，UTC−08:00），合計 932 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 113.9（92.7） | 13 | `apps/server/tests/test_portal.py` |
| 49.2（40.4） | 4 | `apps/server/tests/test_replay_flow.py` |
| 48.4（36.9） | 3 | `apps/server/tests/test_workflow_flow.py` |
| 37.7（30.5） | 12 | `packages/rpa_runner/tests/test_debug.py` |
| 36.9（27.3） | 3 | `apps/server/tests/test_remote_worker_flow.py` |
| 33.0（24.7） | 30 | `apps/server/tests/test_production_api.py` |
| 30.7（22.9） | 5 | `apps/server/tests/test_production_flow.py` |
| 27.8（20.2） | 29 | `apps/server/tests/test_api.py` |
| 25.7（19.6） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 25.6（20.7） | 21 | `apps/server/tests/test_workflow_api.py` |

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

最近一次：2026-11-18 17:53 America/Los_Angeles（PST，UTC−08:00），合計 1907 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 180.0（172.2） | 16 | `apps/server/tests/test_portal.py` |
| 125.8（109.3） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 123.3（122.6） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 120.3（120.4） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 118.3（115.9） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 94.7（110.5） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 91.8（88.5） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 90.4（90.4） | 18 | `apps/cli/tests/test_serve.py` |
| 85.2（78.8） | 9 | `apps/server/tests/test_production_flow.py` |
| 85.1（75.5） | 5 | `apps/server/tests/test_remote_worker_flow.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-2.xml

最近一次：2026-11-18 17:53 America/Los_Angeles（PST，UTC−08:00），合計 1310 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 190.1（179.7） | 16 | `apps/server/tests/test_portal.py` |
| 119.4（116.4） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 114.8（120.5） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 98.0（95.7） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 92.0（93.6） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 88.8（72.7） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 82.9（101.7） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 76.4（86.1） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 72.7（72.7） | 9 | `apps/server/tests/test_production_flow.py` |
| 60.7（55.5） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-macos-latest-3.13/pass-3.xml

最近一次：2026-11-18 17:53 America/Los_Angeles（PST，UTC−08:00），合計 1244 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 158.0（169.7） | 16 | `apps/server/tests/test_portal.py` |
| 111.3（111.3） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 104.7（95.0） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 103.8（108.6） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 98.7（88.0） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 98.4（93.6） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 87.5（94.2） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 74.4（75.4） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 73.9（77.7） | 9 | `apps/server/tests/test_production_flow.py` |
| 46.2（50.0） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.12/pass-1.xml

最近一次：2026-11-18 17:53 America/Los_Angeles（PST，UTC−08:00），合計 1376 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 126.1（112.7） | 16 | `apps/server/tests/test_portal.py` |
| 96.8（90.1） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 85.3（76.9） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 80.3（66.4） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 69.4（58.7） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 64.5（56.7） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 57.0（47.5） | 9 | `apps/server/tests/test_production_flow.py` |
| 53.2（48.8） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 51.7（45.9） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 45.8（39.6） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-1.xml

最近一次：2026-11-18 17:53 America/Los_Angeles（PST，UTC−08:00），合計 1359 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 122.5（121.3） | 16 | `apps/server/tests/test_portal.py` |
| 94.2（94.2） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 84.2（84.2） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 76.4（76.4） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 67.1（67.4） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 62.3（62.3） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 58.1（51.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 57.5（56.7） | 9 | `apps/server/tests/test_production_flow.py` |
| 50.0（48.7） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |
| 44.0（44.0） | 20 | `packages/rpa_runner/tests/test_run.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-2.xml

最近一次：2026-11-18 17:53 America/Los_Angeles（PST，UTC−08:00），合計 925 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 123.1（120.2） | 16 | `apps/server/tests/test_portal.py` |
| 94.3（94.3） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 84.0（84.0） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 75.6（75.6） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 67.2（62.1） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 62.2（62.2） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 56.1（56.0） | 9 | `apps/server/tests/test_production_flow.py` |
| 50.5（47.2） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 43.6（43.6） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 38.3（34.5） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |

### 每晚完整測試 · test-results-ubuntu-latest-3.13/pass-3.xml

最近一次：2026-11-18 17:53 America/Los_Angeles（PST，UTC−08:00），合計 923 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 119.6（119.6） | 16 | `apps/server/tests/test_portal.py` |
| 94.5（94.5） | 16 | `packages/rpa_runner/tests/test_video_browser.py` |
| 82.9（82.9） | 6 | `apps/server/tests/test_workflow_flow.py` |
| 78.6（78.6） | 16 | `packages/rpa_runner/tests/test_login.py` |
| 67.0（61.1） | 23 | `packages/rpa_runner/tests/test_debug.py` |
| 64.4（63.7） | 27 | `packages/rpa_runner/tests/test_flow_browser.py` |
| 55.7（55.7） | 9 | `apps/server/tests/test_production_flow.py` |
| 47.7（47.9） | 5 | `apps/server/tests/test_remote_worker_flow.py` |
| 43.8（43.8） | 20 | `packages/rpa_runner/tests/test_run.py` |
| 39.1（33.2） | 20 | `packages/rpa_runner/tests/test_call_browser.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-1.xml

最近一次：2026-11-18 17:53 America/Los_Angeles（PST，UTC−08:00），合計 1800 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 156.5（145.1） | 16 | `apps\server\tests\test_portal.py` |
| 108.4（105.8） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 106.9（113.2） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 105.2（105.0） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 83.8（84.5） | 23 | `packages\rpa_runner\tests\test_debug.py` |
| 82.7（76.6） | 9 | `apps\server\tests\test_production_flow.py` |
| 81.2（79.0） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 76.2（65.4） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |
| 70.9（56.8） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 64.0（63.1） | 5 | `apps\server\tests\test_remote_worker_flow.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-2.xml

最近一次：2026-11-18 17:53 America/Los_Angeles（PST，UTC−08:00），合計 1174 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 147.8（142.4） | 16 | `apps\server\tests\test_portal.py` |
| 107.9（104.2） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 105.2（105.2） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 104.2（104.0） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 84.6（82.7） | 23 | `packages\rpa_runner\tests\test_debug.py` |
| 78.9（77.3） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 75.2（73.9） | 9 | `apps\server\tests\test_production_flow.py` |
| 60.8（61.4） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 56.4（56.3） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 55.9（48.7） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |

### 每晚完整測試 · test-results-windows-latest-3.13/pass-3.xml

最近一次：2026-11-18 17:53 America/Los_Angeles（PST，UTC−08:00），合計 1202 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 156.7（142.6） | 16 | `apps\server\tests\test_portal.py` |
| 106.9（106.8） | 6 | `apps\server\tests\test_workflow_flow.py` |
| 105.7（103.9） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 103.6（107.7） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 83.5（83.3） | 23 | `packages\rpa_runner\tests\test_debug.py` |
| 81.3（77.7） | 27 | `packages\rpa_runner\tests\test_flow_browser.py` |
| 77.0（72.1） | 9 | `apps\server\tests\test_production_flow.py` |
| 66.8（60.7） | 5 | `apps\server\tests\test_remote_worker_flow.py` |
| 59.5（56.0） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 56.1（53.6） | 20 | `packages\rpa_runner\tests\test_call_browser.py` |

## 最近 40 次運行

| 開始（洛杉磯） | 流程 | 觸發 | 分支 | 結果 | 耗時 | 最長排隊 | 運行 |
|---|---|---|---|---|---|---|---|
| 11-19 17:54 | 一鍵安裝腳本 | 排程 | main | success | 33.5 分 | 0.1 分 | [#44656964332](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44656964332/attempts/1) |
| 11-18 18:01 | 一鍵安裝腳本 | 排程 | main | success | 38.7 分 | 0.1 分 | [#44441238925](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44441238925/attempts/1) |
| 11-18 17:53 | 每晚完整測試 | 排程 | main | success | 75.9 分 | 0.1 分 | [#44440221457](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44440221457/attempts/1) |
| 11-17 18:37 | 一鍵安裝腳本 | 排程 | main | success | 34.8 分 | 0.1 分 | [#44224618237](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44224618237/attempts/1) |
| 11-17 18:26 | 每晚完整測試 | 排程 | main | success | 82.4 分 | 0.1 分 | [#44223299599](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44223299599/attempts/1) |
| 11-16 22:00 | 發布 | 推送 | v0.10.0 | success | 7.8 分 | 0.1 分 | [#44028056829](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44028056829/attempts/1) |
| 11-16 21:54 | 一鍵安裝腳本 | 推送 | main | success | 0.2 分 | 0.0 分 | [#44027323838](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44027323838/attempts/1) |
| 11-16 21:54 | 桌面端建置 | 推送 | main | success | 0.1 分 | 0.1 分 | [#44027323798](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44027323798/attempts/1) |
| 11-16 21:54 | CI | 推送 | main | success | 8.8 分 | 0.1 分 | [#44027323816](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44027323816/attempts/1) |
| 11-16 20:47 | 桌面端建置 | PR | chore/release-0.10.0 | success | 0.1 分 | 0.0 分 | [#44019625800](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44019625800/attempts/1) |
| 11-16 20:47 | 一鍵安裝腳本 | PR | chore/release-0.10.0 | success | 0.2 分 | 0.0 分 | [#44019625786](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44019625786/attempts/1) |
| 11-16 20:47 | CI | PR | chore/release-0.10.0 | success | 2.7 分 | 0.1 分 | [#44019625829](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44019625829/attempts/1) |
| 11-16 20:41 | 伺服器分發包 | PR | chore/release-0.10.0 | success | 0.1 分 | 0.0 分 | [#44018922488](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44018922488/attempts/1) |
| 11-16 20:41 | 一鍵安裝腳本 | PR | chore/release-0.10.0 | success | 0.2 分 | 0.0 分 | [#44018922369](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44018922369/attempts/1) |
| 11-16 20:41 | CI | PR | chore/release-0.10.0 | success | 5.4 分 | 0.1 分 | [#44018922439](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44018922439/attempts/1) |
| 11-16 20:33 | 伺服器分發包 | 推送 | main | success | 0.3 分 | 0.1 分 | [#44018029085](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44018029085/attempts/1) |
| 11-16 20:33 | 桌面端建置 | 推送 | main | success | 0.1 分 | 0.1 分 | [#44018028898](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44018028898/attempts/1) |
| 11-16 20:33 | 一鍵安裝腳本 | 推送 | main | success | 0.3 分 | 0.1 分 | [#44018028894](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44018028894/attempts/1) |
| 11-16 20:33 | CI | 推送 | main | success | 10.4 分 | 0.1 分 | [#44018028874](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44018028874/attempts/1) |
| 11-16 19:12 | 一鍵安裝腳本 | 排程 | main | success | 31.0 分 | 0.1 分 | [#44008481627](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44008481627/attempts/1) |
| 11-16 18:57 | 每晚完整測試 | 排程 | main | success | 78.5 分 | 0.1 分 | [#44006689373](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/44006689373/attempts/1) |
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

