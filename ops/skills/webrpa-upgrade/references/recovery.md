# 狀態及人工接手

交易目錄為 profile 的 `work/jobs/<唯一識別碼>`；權限 700。`result.json` 是狀態，`commands.log` 是命令輸出，`baseline.json` 含受保護的比對資料，兩份 `*.tar.gz` 與 `backup-sha256.json` 是完整備份。日誌可能帶業務路徑，不整份貼到對話或 Git。

| 狀態 | 含義及下一步 |
| --- | --- |
| `already_current` | 實際服務已是該版本，沒有停機或重裝。 |
| `checked` | 檢查模式通過，尚未部署。 |
| `extracting` 至 `verified_private` | 執行中；只追蹤原交易。 |
| `publishing` | 正在恢復對外服務，不能自動還原舊資料。 |
| `succeeded` | 主機驗證通過，再從主控端檢查網路可達性。 |
| `blocked` | 停機前退出；按 reason 解決，再建立新交易。 |
| `rolled_back` | 新版失敗但原版及資料已恢復；請人類決定是否修復後重試，不循環升級。 |
| `needs_human` | 不確定的中斷、回退失敗或已開放服務後的問題；保留現場，人工接手。 |

## 斷線或重開機

先用原 `job.json` 查狀態，再查相應 `webrpa-upgrade-<id>.service`。工作仍執行就等候。工作已退出且沒有終態、主機在交易中重開機、或存在未收尾 `active.json` 時，請人工檢查；不能因檔案年齡而刪除鎖、清除 active 或再派送。

交易鎖由 flock 隨程序釋放；active.json 的未完成狀態仍阻止下一次安裝。先核對 `current`、執行程序、主機 `rpa-server.service`、維護覆寫與備份，再決定恢復哪一步。不要只修改狀態文字偽造成功。

## 回退

自動回退只在對外開放前發生。腳本會停止服務、核對兩份備份雜湊，將失敗安裝與資料移到該交易的 `failed-installation`／`failed-data`，完整恢復原路徑，移除暫時的維護覆寫並啟動原服務。既有配置與外部服務 unit 不應被安裝腳本修改；配置漂移會中止。

若需要人工回退：先保存所有新寫入，停止服務後比對備份範圍和 SHA-256；確認可還原的資料時間點。資料恢復會捨棄該時間點之後的寫入，這種情況需要使用者選擇，不能把完整舊備份直接蓋上去。保留 `commands.log`、失敗資料及程序狀態。

## 設定漂移與技能維護

profile 中的 fingerprint 綁定主機既有 service、drop-in 和 env。只有在確認是使用者已批准的設定調整後，才重新計算指紋；不能為了讓檢查變綠而自動接受漂移。主機換機、非 root 執行、其他架構／端口、跨檔案系統或非 systemd 部署，需要重新制定對應方案。

這次既有主機已完成 systemd 接管。原手動程序的首次遷移只在歷史部署紀錄裡，不套用於每次升級。

## 驗證技能變更

```text
python -X utf8 -m unittest discover -s <技能目錄>/tests -v
python -X utf8 <skill-creator>/scripts/quick_validate.py <技能目錄>
```

Windows 只執行可攜式檢查；涉及 tar、symlink 及回退的測試要在 Linux 的臨時隔離目錄執行。測試以假的 systemd 和假安裝器替代服務操作，會真的建立 SQLite、打包、校驗及還原備份，不接觸正式資料。測試清單與結果要明列平台與跳過項目。

對正式主機驗證設定與相同版本冪等性即可；不要為測試回退而對正式資料故障注入。下一個真實版本仍須按新版本的發布說明及實際結果記錄，測試通過不代表未知的未來版本已驗收。
