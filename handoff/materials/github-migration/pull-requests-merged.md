# 已合併到 main 的 PR（從 git 歷史整理）

共 98 個，取自 main 的第一父提交：合併提交（Merge pull request #N）與壓縮合併（標題結尾的 (#N)）。提交的 SHA 在新倉庫裡不變，可以用 `git show <SHA>` 看當時的改動。PR 的討論、審閱留言與 CI 紀錄只在舊的 GitHub 上，這裡沒有。

沒有出現在 main 歷史裡的編號（未合併的 PR、issue 或被關閉的 PR，GitHub 的 PR 與 issue 共用編號）：#2、#3、#21、#32、#33、#37、#57、#58、#59、#74、#80、#99、#108、#111；另外 #113 之後的見 `repository-info.md`。

| PR | 方式 | 標題 | 提交 | 合併時間（America/Los_Angeles） |
|---|---|---|---|---|
| #1 | merge commit | feat: M0 工程骨架、設計文件與 HTML 文檔站 | `44fc4c9` | 2026-10-09 01:12 PDT |
| #4 | squash | docs(develop): 新增 macOS 本機運行指南 | `7ffc31b` | 2026-10-09 02:09 PDT |
| #5 | squash | docs(develop): 新增本機從零運行文檔與一鍵安裝腳本 | `b0503aa` | 2026-10-09 04:54 PDT |
| #6 | squash | feat(i18n): 產品與文檔支援英文、繁體中文、簡體中文 | `bcb9dca` | 2026-10-10 01:13 PDT |
| #7 | squash | docs: M0 收尾；ADR 0008 資料庫同時支援 SQLite 與 PostgreSQL | `3752b42` | 2026-10-10 02:18 PDT |
| #8 | squash | feat(core): M1 場景 DSL v0：模型、YAML 載入與校驗、rpa validate | `0f80bad` | 2026-10-10 04:23 PDT |
| #9 | squash | feat: M1.1 場景契約與方案 v2（結合 MVP 原型） | `66c4cd3` | 2026-10-10 05:16 PDT |
| #10 | squash | feat: M2 Runner 與執行契約（rpa run） | `9600d6a` | 2026-10-10 08:57 PDT |
| #11 | squash | feat: M3 管理 Portal（rpa serve） | `b8ddf97` | 2026-10-10 22:09 PDT |
| #12 | squash | feat: 場景管理依領域劃分；測試網站自動化與真實案例；rpa serve 埠號自動換與一起啟動測試網站 | `7be956a` | 2026-10-11 23:34 PDT |
| #13 | squash | fix(i18n): 補上新功能的多語言：範例領域名稱跟著介面語言、對話框訊息、執行日誌 | `ed98e07` | 2026-10-12 00:10 PDT |
| #14 | squash | fix: 瀏覽器還沒下載時說明怎麼修；rpa serve 啟動時先檢查 | `e04a08e` | 2026-10-12 00:17 PDT |
| #15 | squash | feat(portal): 執行報告的篩選改成可複選的下拉選單；執行時可選有頭或無頭模式，預設有頭 | `8a95060` | 2026-10-12 01:09 PDT |
| #16 | squash | feat: M4 場景生產與登入（錄製、逐步調試、登入角色與 needs_login、入參出參表單） | `a814baa` | 2026-10-12 07:40 PDT |
| #17 | squash | fix(portal): 資料目錄用相對路徑時錄製一開始就失敗；說明資料夾 | `6bf2eee` | 2026-10-12 22:52 PDT |
| #18 | squash | fix(m4): 接著既有場景錄製、斷言轉成出參、腳本分段編輯、入參出參表格與 YAML、介面整理與設計系統 v1.1 | `7198781` | 2026-10-12 23:51 PDT |
| #19 | squash | chore(deps): Bump astral-sh/setup-uv | `30fe7b8` | 2026-10-13 23:13 PDT |
| #20 | squash | docs: M4 完成；路線圖改為先做 M6 自由試驗場，再做 M5 AI 助手 | `06e57b7` | 2026-10-13 01:43 PDT |
| #22 | squash | feat(m6): 自由試驗場：已發布場景的固定版本排成序列、出參綁定、失敗即停、從停下的節點繼續 (#21) | `683acb0` | 2026-10-13 05:17 PDT |
| #23 | squash | M9a：遠端 worker——執行交給另一台電腦（Worker API、rpa worker、執行位置） | `151a935` | 2026-10-13 20:54 PDT |
| #24 | squash | docs: 交接材料與專案脈絡備忘（handoff/，HTML） | `8f91944` | 2026-10-13 20:58 PDT |
| #25 | squash | fix(setup): 受限語言模式下沒有 uv 與 winget 時，改用官方 uv 壓縮包並校驗 SHA-256 | `e3daa6e` | 2026-10-13 20:58 PDT |
| #26 | squash | docs(handoff): 補齊交接——驗收紀錄、未完成工作、決定分類、運作環境、研發方法、專案文件原文 | `32f240b` | 2026-10-14 00:54 PDT |
| #27 | squash | docs: 建立 Claude 與 ChatGPT 共用協作流程 | `bbea5a4` | 2026-10-14 02:47 PDT |
| #28 | squash | feat(playground): 新增 DAG 畫布與組合場景自動化管理 | `878e4e0` | 2026-10-14 08:18 PDT |
| #29 | squash | docs(handoff): M6 收尾——回填 PR #28 合併、CI 與人工驗收 | `8a170c4` | 2026-10-15 00:19 PDT |
| #30 | squash | M10 桌面端分發：設計與 M10.0 打包地基 | `ce88275` | 2026-10-16 20:48 PDT |
| #31 | squash | M10.1（1/3）：裝置邀請與配對、裝置頁、M9a 收尾三項 | `a9b14ca` | 2026-10-18 05:59 PDT |
| #34 | squash | M10.1：把 #32、#33 帶進 main（Worker App 與安裝檔） | `6b3562e` | 2026-10-18 06:50 PDT |
| #35 | squash | M10.1 收尾：版本改成 0.2.0、路線圖與交接 | `d71f513` | 2026-10-18 08:53 PDT |
| #36 | squash | M10.2（1/3）：錄製端——伺服器端、Client API 互動子程序、rpa recorder | `7990b7c` | 2026-10-19 04:17 PDT |
| #38 | squash | M10.2（2/3）：RPA 錄製端 App（macOS，WKWebView 視窗連本機閘道） (#37) | `4f0b53e` | 2026-10-19 06:10 PDT |
| #39 | squash | M10.2：Linux 伺服器透過錄製端也能錄製、人工登入、有頭調試 | `0bc0127` | 2026-10-19 06:12 PDT |
| #40 | squash | M11 資料存放升級：設計與決定（領域資料夾、驗證與發布紀錄、git 同步） | `a779e2a` | 2026-10-19 17:57 PDT |
| #41 | squash | docs: 新增「部署與操作」，回填 M10.2 的驗收與合併情況 | `3c29f91` | 2026-10-19 08:32 PDT |
| #42 | squash | chore(deps): 更新 Python 依賴（Playwright 1.64 等），修正 record.py 的型別檢查 | `e8c1e89` | 2026-10-19 17:41 PDT |
| #43 | squash | M10.2（3/3）：錄製端 DMG 進 Release、macOS 端到端、不開 App 視窗的模式、v0.3.0 | `2cf3c9f` | 2026-10-19 09:27 PDT |
| #44 | squash | feat(setup): 新增 RHEL 衍生版 Linux 伺服器安裝 | `060b67d` | 2026-10-19 18:05 PDT |
| #45 | squash | ci: 縮短 CI 與一鍵安裝腳本的執行時間（平行化、每晚完整測試） | `1613148` | 2026-10-19 17:38 PDT |
| #46 | squash | ci: 依生產角色分配測試、只改文件沿用結果、手動觸發選項與運行耗時紀錄 | `9dc68be` | 2026-10-19 23:43 PDT |
| #47 | squash | fix(portal): 沒有畫面時調試與錄製變灰、提示用錄製端；起始網址不能是 Portal 自己；測試網站可對外開放 | `a6164f7` | 2026-10-20 01:39 PDT |
| #48 | squash | M11 PR 1：領域資料夾（場景與角色）、驗證與發布紀錄、rpa pack check、遷移 | `cfef585` | 2026-10-20 07:17 PDT |
| #49 | squash | M11 PR 2：組合場景放進領域資料夾（版本、驗證紀錄、發布、依賴檢查） | `e54025c` | 2026-10-20 07:34 PDT |
| #50 | squash | fix(portal): 人工登入在開視窗的那台確認、「檢查」交給有瀏覽器的電腦、看得懂的登入錯誤 | `53a0578` | 2026-10-20 05:40 PDT |
| #51 | squash | fix(runner): 人工登入的 Firefox 在背景不再停住 | `acf3f93` | 2026-10-20 07:38 PDT |
| #52 | squash | feat(setup): Linux 伺服器安裝測速後選最快的套件來源 | `0fef3cd` | 2026-10-20 08:18 PDT |
| #53 | squash | fix(server): 舊資料庫升級時，SQLite 的遷移不被外鍵檢查擋下 | `1be5a90` | 2026-10-20 17:39 PDT |
| #54 | squash | M11 PR 3：領域資料夾的 git 同步（資料來源、拉取、推送、衝突三選一） | `677853c` | 2026-10-20 19:16 PDT |
| #55 | squash | test(desktop): 等背景的監看處理完結束的請求，不再偶發失敗 | `a77c603` | 2026-10-20 20:10 PDT |
| #56 | squash | M11 收尾：依賴補全、組合場景改代號／搬領域／封存、執行用版本快照 | `b9a3387` | 2026-10-20 20:10 PDT |
| #60 | merge commit | docs: 把 #57（M11 PR 4）補進 main | `097464c` | 2026-10-20 23:20 PDT |
| #61 | merge commit | M12 PR 1：運行錄影與資料（runner、worker、伺服器的設定與保留規則） | `b306dbe` | 2026-10-21 04:39 PDT |
| #62 | merge commit | feat(m7a): 支援 iframe 裡的元素（定位器的 frame） | `54a2df5` | 2026-10-21 04:12 PDT |
| #63 | merge commit | feat(setup): 瀏覽器安裝測速後選用最快來源 | `848b0bf` | 2026-10-21 02:52 PDT |
| #64 | merge commit | M12 PR 2：回看頁（播放器、縮圖時間軸、步驟關聯）與「運行回看」入口 | `9798db4` | 2026-10-21 05:03 PDT |
| #65 | merge commit | chore(release): 升級 0.4.0 並重新打包 Worker 與 Recorder | `fcb8e8f` | 2026-10-21 05:54 PDT |
| #66 | merge commit | feat(m7b): 支援點擊開出的新分頁（步驟的 popup 與 page） | `588e6a4` | 2026-10-22 00:30 PDT |
| #67 | merge commit | feat(dsl): 入參的動態值（{{today}}、{{today+1}}、{{random:10:30}}） | `df47b14` | 2026-10-22 05:24 PDT |
| #68 | merge commit | docs(design): 設計文件對齊 v0.4.0（系統架構、桌面端分發的圖、其他頁） | `e63559a` | 2026-10-22 03:36 PDT |
| #69 | merge commit | fix(replay): 保留多分頁錄影並修正 Chromium 回看對時 | `62598a6` | 2026-10-22 03:30 PDT |
| #70 | merge commit | feat(server): Linux 伺服器分發包（自帶 Python 的 tar.gz、install.sh 安裝與升級） | `ba1886f` | 2026-10-22 07:18 PDT |
| #71 | merge commit | feat(desktop): macOS 版 RPA Worker（選單列、登入時自動啟動、鑰匙圈、DMG） | `ca0bc93` | 2026-10-22 07:28 PDT |
| #72 | merge commit | feat(portal): 選單改成五個第一級並依三段分工顯示（領域排序、錄製端預設不顯示叢集管理與管理後台） | `748cba8` | 2026-10-22 07:32 PDT |
| #73 | merge commit | chore(release): 統一 0.5.0 版本並準備安裝包 | `6522d74` | 2026-10-22 21:00 PDT |
| #75 | merge commit | ci(release): 縮短產物保存期、發布後刪除產物，新增手動清理產物 | `986dbf7` | 2026-10-22 23:04 PDT |
| #76 | merge commit | docs(handoff): 記錄清理產物、重跑發布與 v0.5.0 草稿的結果 | `3d99504` | 2026-10-23 03:29 PDT |
| #77 | merge commit | docs(design): 設計文件改成目前 v0.5.0，倉庫改為私有 | `29176b1` | 2026-10-25 01:57 PDT |
| #78 | merge commit | feat(server): 新增專案空間與專案管理，取代組合場景自動化 | `a8cde7f` | 2026-10-23 18:11 PDT |
| #79 | merge commit | feat(server): 對外 Agent API 第一期（M14）：API 用戶端、/agent-api/v1、專案與組合場景 | `d66b4a6` | 2026-10-25 06:21 PDT |
| #81 | merge commit | fix(ci): 修復排程測試環境、Portal 探測與回看錯誤提示 | `c587cda` | 2026-10-25 16:54 PDT |
| #82 | merge commit | docs(handoff): Python 腳本場景的設計第二版（本機自動化、專用運行環境；待確認，只有設計） | `4b64adb` | 2026-10-25 16:57 PDT |
| #83 | merge commit | feat: 分層熱更新：伺服器用更新檔升級，Worker 與錄製端跟著伺服器更新（ADR 0018） | `06afe18` | 2026-10-25 17:08 PDT |
| #84 | merge commit | fix(runner): Windows 上 steps.json 被開著時改名寫入重試 | `9fd0861` | 2026-10-25 07:53 PDT |
| #85 | squash | chore(release): 準備 v0.6.0 完整安裝包與更新檔 | `f76a950` | 2026-10-25 17:31 PDT |
| #86 | merge commit | fix(portal): 場景詳情頁、運行檔案與運行報告的集中修正 | `299348f` | 2026-10-26 00:58 PDT |
| #87 | merge commit | chore(release): 準備 v0.6.1 更新檔 | `262e107` | 2026-10-26 01:35 PDT |
| #88 | merge commit | fix(updates): 裝置能跟著伺服器熱更新、入參與出參的錨點 | `e6b6885` | 2026-10-26 04:46 PDT |
| #89 | merge commit | chore(release): v0.6.2 | `8e84c6a` | 2026-10-26 05:03 PDT |
| #90 | merge commit | fix(debug): 在錄製端調試時可以換版本（Portal 存成新版本並繼續調試、Agent API reload） | `84b4611` | 2026-10-26 08:24 PDT |
| #91 | merge commit | chore(release): v0.6.3 | `066ded2` | 2026-10-26 08:45 PDT |
| #92 | merge commit | docs(handoff): v0.6.3 草稿 Release 已核對，待發布 | `ed38493` | 2026-10-26 21:38 PDT |
| #93 | merge commit | fix(updates): 排程在 macOS、Windows 的兩個失敗（issue #80、#74） | `4da719a` | 2026-10-26 21:39 PDT |
| #94 | merge commit | ci: 依層建置：同一組輸入只驗證一次，外殼沒變不重新打包 | `256918d` | 2026-10-26 21:44 PDT |
| #95 | merge commit | test(update): 更新檔清單的測試在 Windows 失敗（issue #80、#74 的第三個原因） | `30f2290` | 2026-10-26 21:48 PDT |
| #96 | merge commit | feat(portal): 組合運行的匯總報告 | `56936f6` | 2026-10-27 17:36 PDT |
| #97 | merge commit | feat: M7c 上傳檔案（Excel 匯入、圖片上傳）：檔案入參、upload 步驟、場景附件、Portal 選檔與遠端下載 | `a26b929` | 2026-10-28 00:46 PDT |
| #98 | merge commit | feat(portal): 組合運行的合併回看 | `56953fc` | 2026-10-28 00:34 PDT |
| #100 | merge commit | docs: 文檔站對齊 main（v0.6.3 之後：路線圖、架構、桌面端分發、開發文件） | `b559285` | 2026-10-28 06:33 PDT |
| #101 | merge commit | fix: main 的 CI 紅燈（驗證後馬上發布、有頭測試沒有螢幕、回看邊界、點擊後頁面關閉） | `abdfcb8` | 2026-10-28 02:06 PDT |
| #102 | merge commit | chore(release): v0.7.0 | `469c3be` | 2026-10-28 02:30 PDT |
| #103 | merge commit | fix(portal): 回看的舊快取、點步驟不動、詳情從右側滑出、場景用顏色分隔 | `3f3725b` | 2026-10-29 03:54 PDT |
| #104 | merge commit | v0.7.1 | `2089d48` | 2026-10-29 04:08 PDT |
| #105 | merge commit | ci(nightly): Windows 放大動態連接埠並記錄連線狀態；排不到機器時也開 issue | `c9a9d7f` | 2026-10-29 05:26 PDT |
| #106 | merge commit | 回看：依步驟的章節軸、每一步的截圖，步驟詳情從清單上方滑出 | `a4298ea` | 2026-10-29 06:26 PDT |
| #107 | squash | chore(release): 準備 v0.8.0 版本與發布紀錄 | `e5b585e` | 2026-10-29 06:37 PDT |
| #109 | merge commit | feat(python): Python 節點，和瀏覽器場景串在組合場景裡（ADR 0020） | `e6cb462` | 2026-11-06 04:55 PST |
| #110 | merge commit | chore(deps): bump astral-sh/setup-uv from 10.3.0 to 10.3.2 in the actions group | `8c89539` | 2026-11-05 17:14 PST |
| #112 | merge commit | chore(deps): bump astral-sh/setup-uv from 10.3.2 to 10.3.3 in the actions group | `673dc4c` | 2026-11-06 17:50 PST |
