# CI 運行耗時紀錄

更新：2026-11-09 05:59 America/Los_Angeles（PST，UTC−08:00）。共 4 次運行。

每次 CI、桌面端建置、一鍵安裝腳本、每晚完整測試、發布結束後，由 `.github/workflows/ci-metrics.yml` 追加到 `data/`；本頁由 `tools/ci_metrics.py report` 產生，不要手改。耗時＝第一個工作建立到最後一個工作結束（含排隊）；機器時間＝各工作實際執行的時間總和。
規則與背景見 main 的 `docs/develop/ci.html`。

## 各流程：近 7 天（前 7 天）

| 流程 | 次數 | 通過 | 耗時中位數 | 耗時 P90 | 最長排隊中位數 | 機器時間（Linux／Windows／macOS） |
|---|---|---|---|---|---|---|
| CI | 1（0） | 1（0） | 8.1 分（0.0 分） | 8.1 分（0.0 分） | 3.9 分（0.0 分） | 7／4／0 分（0／0／0 分） |
| 桌面端建置 | 1（0） | 1（0） | 7.0 分（0.0 分） | 7.0 分（0.0 分） | 0.1 分（0.0 分） | 0／6／12 分（0／0／0 分） |
| 伺服器分發包 | 1（0） | 1（0） | 2.5 分（0.0 分） | 2.5 分（0.0 分） | 0.1 分（0.0 分） | 5／0／0 分（0／0／0 分） |
| 一鍵安裝腳本 | 1（0） | 1（0） | 5.1 分（0.0 分） | 5.1 分（0.0 分） | 2.8 分（0.0 分） | 4／2／3 分（0／0／0 分） |
| 每晚完整測試 | 0（0） | 0（0） | 0.0 分（0.0 分） | 0.0 分（0.0 分） | 0.0 分（0.0 分） | 0／0／0 分（0／0／0 分） |
| 發布 | 0（0） | 0（0） | 0.0 分（0.0 分） | 0.0 分（0.0 分） | 0.0 分（0.0 分） | 0／0／0 分（0／0／0 分） |

## 每天的機器時間（分鐘，洛杉磯日期，最近 14 天）

| 日期 | 運行次數 | Linux | Windows | macOS | 合計 |
|---|---|---|---|---|---|
| 2026-11-09 | 4 | 16 | 12 | 16 | 43 |

## 最慢的測試檔案（每份報告最近一次，括號是近 7 次的中位數）

### CI · pytest-report-3.12/pytest-report.xml

最近一次：2026-11-09 05:50 America/Los_Angeles（PST，UTC−08:00），合計 385 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 24.9（24.9） | 25 | `apps/server/tests/test_production_api.py` |
| 24.3（24.3） | 29 | `apps/server/tests/test_api.py` |
| 23.3（23.3） | 22 | `apps/server/tests/test_remote_worker_api.py` |
| 20.6（20.6） | 18 | `apps/cli/tests/test_serve.py` |
| 18.1（18.1） | 11 | `apps/server/tests/test_gitsync.py` |
| 16.3（16.3） | 13 | `apps/server/tests/test_replay.py` |
| 16.3（16.3） | 14 | `apps/server/tests/test_workflow_api.py` |
| 15.9（15.9） | 20 | `apps/server/tests/test_recorder_api.py` |
| 14.2（14.2） | 17 | `apps/worker/tests/test_recorder.py` |
| 14.1（14.1） | 10 | `apps/server/tests/test_videos.py` |

### CI · pytest-report-3.13/pytest-report.xml

最近一次：2026-11-09 05:50 America/Los_Angeles（PST，UTC−08:00），合計 730 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 105.4（105.4） | 12 | `apps/server/tests/test_portal.py` |
| 46.4（46.4） | 4 | `apps/server/tests/test_replay_flow.py` |
| 44.2（44.2） | 3 | `apps/server/tests/test_workflow_flow.py` |
| 32.6（32.6） | 10 | `packages/rpa_runner/tests/test_debug.py` |
| 32.0（32.0） | 5 | `apps/server/tests/test_production_flow.py` |
| 30.3（30.3） | 3 | `apps/server/tests/test_remote_worker_flow.py` |
| 23.2（23.2） | 29 | `apps/server/tests/test_api.py` |
| 22.6（22.6） | 25 | `apps/server/tests/test_production_api.py` |
| 22.6（22.6） | 15 | `apps/server/tests/test_replay.py` |
| 20.3（20.3） | 22 | `apps/server/tests/test_remote_worker_api.py` |

### CI · pytest-report-windows/pytest-report.xml

最近一次：2026-11-09 05:50 America/Los_Angeles（PST，UTC−08:00），合計 664 秒。

| 秒 | 測試數 | 檔案 |
|---|---|---|
| 213.7（213.7） | 16 | `packages\rpa_runner\tests\test_login.py` |
| 115.6（115.6） | 16 | `packages\rpa_runner\tests\test_video_browser.py` |
| 103.1（103.1） | 10 | `packages\rpa_runner\tests\test_frames.py` |
| 77.4（77.4） | 20 | `packages\rpa_runner\tests\test_run.py` |
| 47.2（47.2） | 17 | `packages\rpa_runner\tests\test_upload.py` |
| 39.5（39.5） | 8 | `packages\rpa_runner\tests\test_tabs.py` |
| 33.4（33.4） | 2 | `packages\rpa_runner\tests\test_download_browser.py` |
| 25.4（25.4） | 1 | `packages\rpa_runner\tests\test_profiles.py` |
| 3.8（3.8） | 2 | `tests\smoke\test_browser.py` |
| 2.5（2.5） | 1 | `apps\desktop\tests\test_selftest.py` |

## 最近 40 次運行

| 開始（洛杉磯） | 流程 | 觸發 | 分支 | 結果 | 耗時 | 最長排隊 | 運行 |
|---|---|---|---|---|---|---|---|
| 11-09 05:50 | 伺服器分發包 | PR | chore/github-migration-2 | success | 2.5 分 | 0.1 分 | [#42629078946](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42629078946/attempts/1) |
| 11-09 05:50 | 一鍵安裝腳本 | PR | chore/github-migration-2 | success | 5.1 分 | 2.8 分 | [#42629077646](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42629077646/attempts/1) |
| 11-09 05:50 | 桌面端建置 | PR | chore/github-migration-2 | success | 7.0 分 | 0.1 分 | [#42629077664](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42629077664/attempts/1) |
| 11-09 05:50 | CI | PR | chore/github-migration-2 | success | 8.1 分 | 3.9 分 | [#42629077625](https://github.com/ali-sx-org-free/web_browser_robotic_process_automation/actions/runs/42629077625/attempts/1) |

