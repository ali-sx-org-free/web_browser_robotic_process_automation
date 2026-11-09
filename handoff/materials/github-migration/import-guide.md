# RPA 專案搬家包：導入新的 GitHub 倉庫

> 這是搬家包 `rpa-github-migration-2026-11-08.zip` 裡的教程原文，收進倉庫備查。文中的 `01-repos/`、`02-github-metadata/`、`03-tools/` 指搬家包裡的資料夾；`02-github-metadata/` 的檔案就是本資料夾的其他檔案。實際的搬家經過見 `handoff/tasks/20261108-github-migration.html`。

製作：Claude，2026-11-08（新加坡時間）。對象：`DevopsLeaDevops/web_browser_robotic_process_automation`（主倉庫）與 `DevopsLeaDevops/web_browser_robotic_process_automation_site`（領域資料倉庫）。

照第 1～11 節依序做，就能盡量完整地搬到新倉庫；第 12 節是逐項打勾的檢查清單。命令在 macOS、Linux 的終端機執行；Windows 請用 Git for Windows 附的 **Git Bash**。

---

## 0. 先看這裡

### 這個包裡有什麼

| 路徑 | 內容 |
|---|---|
| `01-repos/web_browser_robotic_process_automation/` | 主倉庫，已解開的工作資料夾。工作區停在 `main`（`673dc4c`），`.git` 裡有完整歷史：從第一個提交 `d548c06` 起，`main` 上 373 個提交、11 個版本標籤 v0.2.0～v0.8.0，以及分支 `docs/refresh-v0-8`（未合併的 PR #114） |
| `01-repos/web_browser_robotic_process_automation.bundle` | 同一份歷史的單檔備份（git bundle）。資料夾解壓出問題時用它（第 3.4 節） |
| `01-repos/web_browser_robotic_process_automation_site/` | 資料倉庫：`testsite/` 領域資料夾。GitHub 上只有一個提交 `5c98ad6`（2026-10-21），這就是它的全部歷史 |
| `01-repos/web_browser_robotic_process_automation_site.bundle` | 資料倉庫的單檔備份 |
| `02-github-metadata/repository-info.md` | 只存在 GitHub 上的資料：分支、標籤與 Release、Secrets、工作流程、寫死的舊網址、拿不回來的東西 |
| `02-github-metadata/pull-requests-merged.md`、`.csv` | 已合併的 98 個 PR 對照表（編號、標題、在 main 上的提交、合併時間），從 git 歷史整理 |
| `02-github-metadata/open-pr-114.md` | 未合併的 PR #114 的說明原文 |
| `03-tools/push-to-new-github.sh` | 一次推送全部分支與標籤，並逐一核對 |
| `03-tools/update-repo-url.sh` | 把程式、安裝腳本與文件裡的舊倉庫網址換成新的 |
| `SHA256SUMS.txt` | 包裡每個檔案的校驗碼 |

### 資料有多新

- 主倉庫的 `main` 是 2026-11-06 17:50 PST 合併的 `673dc4c`（PR #112）。之後 GitHub 開始拒絕連線，如果之後有人在 GitHub 上又合併了東西，這裡沒有；就我所知沒有。
- `docs/refresh-v0-8` 比 GitHub 上多一個提交 `c48f095`（帳號停權後只在本機）。
- 最新的正式版本是 v0.8.0。`main` 上另有還沒發布的 Python 節點（PR #109）。

### 重要：GitHub 回的是「帳號已停權」，不只是密碼

從 2026-11-06 約 18:15 PST 起，GitHub 對這個帳號的 API 與 git 都回 **403「Sorry. Your account was suspended」**。2026-11-08 再試，結果一樣。忘記密碼可以自己重設；停權只能找 GitHub 處理。動手搬家之前，請先看第 1 節。

---

## 1. 先試著找回舊帳號（能找回就最完整）

能找回舊帳號，最完整的做法不是重新上傳，而是用 GitHub 的 **Transfer**（轉移）把倉庫轉給新帳號或組織。依 GitHub 文件，轉移時 issues、PR、wiki、star 與 watcher 會一起轉過去，舊網址也會自動轉到新位置。這個包重建不了這些東西。

1. **只是忘了密碼**：到 <https://github.com/password_reset> 輸入帳號註冊時驗證過的 email 重設。有開兩步驟驗證的，還要有驗證 App、recovery codes（預設檔名 `github-recovery-codes.txt`）或 passkey 才登得進去。
2. **帳號被停權**：登入時如果看到停權的訊息，或收到 GitHub 寄來的停權 email，只能經由 GitHub Support 申訴：<https://support.github.com/>，要用帳號驗證過的 email 聯絡。社群裡的經驗是回覆要等幾天到幾週。
3. **找回之後**：到舊倉庫的 Settings › General 最下面的 Danger Zone › **Transfer**，輸入新帳號或組織名稱。兩個倉庫都要轉。轉完後，第 4 節的改網址照樣要做；第 3 節（推送）不用做。Secrets 是否一起轉過去，請轉完後到 Settings › Secrets 確認，沒有就照第 5 節重設。

> 關於另開新帳號：如果舊帳號確實是被停權，社群裡的回覆普遍建議先申訴，不要另開帳號繞過停權，否則新帳號也可能被停權；GitHub 的可接受使用政策也禁止假帳號（fake accounts）。要用新帳號，請先確認不違反 GitHub 的規定，例如改用你所屬組織既有的合法帳號。這個包的 git 資料也能放到 GitLab、Gitea 等其他平台；但 `.github/workflows/` 是 GitHub Actions 專用的，換平台就要重寫 CI，本教程不涵蓋。

決定用新的 GitHub 倉庫之後，從第 2 節開始。

---

## 2. 準備

1. **解壓縮**到路徑沒有空白、不太深的地方，例如 `~/rpa-migration/`（Windows：`C:\rpa-migration\`）。Windows 內建解壓遇到中文檔名有時會變成亂碼；這時改用 7-Zip，或照第 3.4 節從 bundle 還原。
2. **安裝 Git**：<https://git-scm.com/downloads>。Windows 版附 Git Bash，下面的命令都在 Git Bash 執行。
3. **讓這台電腦能推送到新帳號**，三選一：
   - GitHub CLI（建議）：安裝 <https://cli.github.com/> 後執行 `gh auth login`，選 GitHub.com、HTTPS、用瀏覽器登入。
   - GitHub Desktop：登入一次，之後命令列推送時會用它的認證。
   - 個人存取權杖（PAT）：GitHub 的 git 推送不接受帳號密碼，要在 Settings › Developer settings 建一個權杖，推送時把它當密碼輸入。classic 權杖要勾 `repo` 和 **`workflow`**：這個倉庫有 `.github/workflows/`，少了 `workflow` 權限會被拒。
4. **保護新帳號**：開兩步驟驗證，recovery codes 存到密碼管理器。這次就是少了這一步才進不去。

---

## 3. 建立新倉庫並推送

### 3.1 建立兩個空倉庫

在 GitHub 右上角「+ › New repository」建立兩個倉庫：

| 倉庫 | 建議名稱 | 說明 |
|---|---|---|
| 主倉庫 | `web_browser_robotic_process_automation` | 沿用原名，要改的地方最少 |
| 資料倉庫 | `web_browser_robotic_process_automation_site` | RPA 伺服器同步領域資料用；放的是你們的場景，可以設成 Private |

- **README、.gitignore、License 都不要勾**，倉庫必須是空的。
- Public 或 Private：舊倉庫最後是公開的。私有倉庫的 Actions 分鐘數與產物儲存空間會計入帳號方案的額度；`docs/develop/ci.html` 有說明。
- 用 GitHub CLI 也可以：
  ```bash
  gh repo create 新帳號/web_browser_robotic_process_automation --public
  gh repo create 新帳號/web_browser_robotic_process_automation_site --private
  ```

### 3.2 用腳本推送（建議）

```bash
cd ~/rpa-migration/rpa-github-migration-2026-11-08/03-tools
bash push-to-new-github.sh \
  https://github.com/新帳號/web_browser_robotic_process_automation.git \
  https://github.com/新帳號/web_browser_robotic_process_automation_site.git
```

腳本會做這些事：

1. 把舊的 `origin` 改名成 `old-github`，保留舊網址備查；`origin` 指向新倉庫。
2. 先單獨推 `main`（空倉庫收到的第一個分支會成為預設分支），再推其他分支。
3. 一次推完全部標籤。
4. 逐一核對每個分支與標籤，和本機的一致才算完成。

成功時最後會看到：

```
  ✓ 新倉庫和本機一致：2 個分支、11 個標籤
  ✓ 新倉庫和本機一致：1 個分支、0 個標籤
```

腳本可以重複執行：已經推過的會顯示 `Everything up-to-date`。

### 3.3 手動推送（和腳本做的一樣）

```bash
cd ~/rpa-migration/rpa-github-migration-2026-11-08/01-repos/web_browser_robotic_process_automation
git remote rename origin old-github
git remote add origin https://github.com/新帳號/web_browser_robotic_process_automation.git
git push -u origin main
git push origin docs/refresh-v0-8
git push origin --tags

cd ../web_browser_robotic_process_automation_site
git remote rename origin old-github
git remote add origin https://github.com/新帳號/web_browser_robotic_process_automation_site.git
git push -u origin main
```

### 3.4 資料夾有問題時，從 bundle 還原

```bash
cd ~/rpa-migration/rpa-github-migration-2026-11-08/01-repos
git clone web_browser_robotic_process_automation.bundle rpa-from-bundle
cd rpa-from-bundle
git branch docs/refresh-v0-8 origin/docs/refresh-v0-8
git fetch origin 'refs/tags/*:refs/tags/*'
git remote set-url origin https://github.com/新帳號/web_browser_robotic_process_automation.git
git push -u origin main && git push origin docs/refresh-v0-8 && git push origin --tags
```

資料倉庫一樣：`git clone web_browser_robotic_process_automation_site.bundle site-from-bundle`，改 `origin` 後 `git push -u origin main`。

### 3.5 推送之後會發生什麼

- 推送 `main` 會觸發 CI、桌面端建置、伺服器分發包、RPA Python 運行環境、一鍵安裝腳本等工作流程；第一次全部完整建置，要一段時間。還沒設 Secrets 之前，桌面端建置會留下「沒有 RPA_UPDATE_CI_KEY」的警告，不影響結果。
- 11 個標籤一次推上去**不會**觸發「發布」：GitHub 在一次推送超過 3 個標籤時不產生事件。之後如果只推 1～3 個 `v` 開頭的標籤，就會觸發發布（第 8 節就是用這個方式重建 Release）。
- 每晚測試、一鍵安裝腳本、Python 依賴更新會照排程在新倉庫跑（時間見 `repository-info.md`）。

在新倉庫的網頁上確認：Code 頁的提交數、Branches 有 `main` 與 `docs/refresh-v0-8`、Tags 有 11 個；Settings › General › Default branch 是 `main`。

---

## 4. 把程式裡的舊網址換成新的

App 的「下載新版」按鈕、一鍵安裝腳本、Windows 安裝檔的網址和文件裡，都寫著舊倉庫的網址。在主倉庫資料夾執行：

```bash
cd ~/rpa-migration/rpa-github-migration-2026-11-08/01-repos/web_browser_robotic_process_automation
git switch -c chore/new-repo-url
bash ../../03-tools/update-repo-url.sh 新帳號/web_browser_robotic_process_automation
git diff                       # 看一下改了什麼
git commit -am "chore: 倉庫搬到 新帳號/web_browser_robotic_process_automation"
git push -u origin chore/new-repo-url
```

再到新倉庫的網頁開 PR，等 CI 通過後合併。

腳本做的事：

- 只換 `DevopsLeaDevops/web_browser_robotic_process_automation` 這串路徑。目前會改 17 個檔案：`release.py`、`rpa_worker.iss`、三個安裝腳本，以及開發環境、本機從零運行、macOS、遠端 Worker 的文件（繁中、英文、簡中）。
- 英文頁記錄了它對照的繁中版本，腳本會重新記錄（`tools/i18n.py stamp`）。這一步需要 Python 3.12 以上或 uv；都沒有時，腳本會告訴你之後要補跑哪一行。

**刻意不改的**：

- `io.github.devopsleadevops.rpa.recorder`、`io.github.devopsleadevops.rpa.worker`：macOS App 的識別碼與開機自動啟動的名稱。改了，已安裝的 App 會被當成另一個程式。
- `rpa_worker.iss` 的 `AppId`：Windows 的升級與解除安裝靠它，檔案裡註明永遠不要改。`AppPublisher=DevopsLeaDevops` 只是顯示的發行者名稱，要改可以手動改。
- `handoff/` 的舊連結：那是歷史紀錄，指向舊的 PR、提交與 CI 頁。提交的 SHA 在新倉庫裡不變，舊的 PR 編號對照見 `02-github-metadata/pull-requests-merged.md`。

合併之後，文件裡的一鍵安裝命令（`curl … | bash`、`irm …`）就會從新倉庫下載。已安裝的 App 要等下一次更新，「下載新版」才會連到新網址。

---

## 5. 重建 Secrets

GitHub 不讓任何人讀回 Secret 的值，所以要重新設定。位置：新倉庫的 Settings › Secrets and variables › Actions › New repository secret。

### 5.1 `RPA_UPDATE_SIGNING_KEY`（發布用的簽章私鑰，最重要）

已安裝的伺服器、RPA Worker 與錄製端，只接受用這把私鑰簽章的更新檔。它的公鑰寫在 `packages/rpa_update/src/rpa_update/keys.py`：

```
+zBkjVUh9RensU1hgeWNOeJuRqH82tguO7byaNXCr6w=
```

私鑰是你 2026-10-25 自己產生的 `rpa-update-signing.pem`，當時的文件要求另外備份到密碼管理器。先找找看。

**情況 A：找得到 `rpa-update-signing.pem`**

1. 確認它對得上公鑰。macOS 內建的 openssl 是 LibreSSL，不支援 Ed25519，請用 Homebrew 的 `openssl@3`，或在 Linux、Git Bash 執行：
   ```bash
   openssl pkey -in rpa-update-signing.pem -pubout -outform DER | tail -c 32 | base64
   ```
   印出的要和上面那串一模一樣。
2. 設成 Secret：
   ```bash
   gh secret set RPA_UPDATE_SIGNING_KEY --repo 新帳號/web_browser_robotic_process_automation < rpa-update-signing.pem
   ```
   也可以在網頁上新增，值貼上檔案全部內容，包含 `-----BEGIN PRIVATE KEY-----` 與 `-----END PRIVATE KEY-----` 兩行。
3. 已安裝的伺服器與裝置照舊能用更新檔升級，什麼都不用換。

**情況 B：找不到私鑰**

用舊私鑰簽章已經不可能，要換一把新的：

1. 在主倉庫資料夾產生新的私鑰。這一步要先跑過一次一鍵安裝，或執行 `uv sync`：
   ```bash
   uv run python -m rpa_update.build keygen --private rpa-update-signing.pem
   ```
   印出的那一行是新的公鑰。
2. 打開 `packages/rpa_update/src/rpa_update/keys.py`，把 `RELEASE_KEYS` 裡的舊公鑰換成新的。舊的已經沒有私鑰，留著沒有用。用 PR 合併。
3. `gh secret set RPA_UPDATE_SIGNING_KEY --repo 新帳號/web_browser_robotic_process_automation < rpa-update-signing.pem`
4. 把 `rpa-update-signing.pem` 備份到密碼管理器，再從電腦刪掉。
5. 後果：`keys.py` 改了，下一個版本的伺服器、RPA Worker、錄製端**都要用完整的安裝包**重新安裝一次。之後的版本又能只用更新檔。v0.8.0 也重建不了（第 8 節）。

### 5.2 `RPA_UPDATE_CI_KEY`（CI 的測試金鑰）

只給 CI 的試用包用，和發布無關，直接產生新的就好（不要和發布金鑰共用）：

```bash
uv run python -m rpa_update.build keygen --private rpa-update-ci.pem
gh secret set RPA_UPDATE_CI_KEY --repo 新帳號/web_browser_robotic_process_automation < rpa-update-ci.pem
rm rpa-update-ci.pem
```

沒設也能跑，只是桌面端建置每次都完整建置，並留下警告。

---

## 6. Actions 與倉庫設定

在新倉庫的 Settings 裡：

1. **Actions › General**
   - Actions permissions：Allow all actions and reusable workflows（預設就是）。
   - Workflow permissions：維持預設即可，各工作流程自己宣告了需要的權限。
   - 勾選 **Allow GitHub Actions to create and approve pull requests**：每週的 Python 依賴更新（`uv-upgrade.yml`）要用它開 PR。
2. **General › Features**：Issues 要開著。每晚測試與一鍵安裝腳本失敗時會自動開 issue。
3. **Code security**（可選）：開啟 Dependabot alerts 與 security updates。版本更新已經由倉庫裡的 `.github/dependabot.yml` 設定好。
4. **Branches**（可選，建議）：替 `main` 加保護規則，要求透過 PR 合併、CI 通過才能合併。舊倉庫原本有沒有設，我不知道。
5. 舊倉庫的 `ci-metrics` 分支（CI 耗時統計）沒有帶過來。第一次 CI 結束後會自動建立新的。

---

## 7. 資料倉庫與 RPA 伺服器的 git 同步

`web_browser_robotic_process_automation_site` 是 RPA 伺服器「git 同步」推送的領域資料（`testsite/`）。領域資料的正本在你的 RPA 伺服器上，GitHub 只是同步的對象。

1. **看伺服器上有沒有更新的歷史**。在 RPA 伺服器上執行，資料目錄見 `~/rpa-server/rpa-server.env` 的 `RPA_DATA_DIR`：
   ```bash
   git --git-dir "<資料目錄>/git/repos/testsite.git" log --oneline --all | head
   ```
   如果比包裡的 `5c98ad6`（2026-10-21）新，就從伺服器把完整歷史推到新倉庫：
   ```bash
   git --git-dir "<資料目錄>/git/repos/testsite.git" for-each-ref        # 看分支叫什麼，通常是 refs/remotes/origin/main
   git --git-dir "<資料目錄>/git/repos/testsite.git" push \
     https://github.com/新帳號/web_browser_robotic_process_automation_site.git \
     "refs/remotes/origin/main:refs/heads/main"
   ```
   這只是讀取伺服器的資料再推出去，不會改動伺服器。
2. **在管理 Portal 改同步的對象**：管理後台 › 領域管理 › `testsite` 的「資料來源與同步」。網址改成新倉庫，認證二選一：
   - **SSH**：網址用 `git@github.com:新帳號/web_browser_robotic_process_automation_site.git`，在同步頁讓 Portal 產生部署金鑰。把公鑰加到新倉庫的 Settings › Deploy keys › Add deploy key，並**勾選 Allow write access**。舊倉庫用的就是這種方式。
   - **HTTPS**：網址用 `https://github.com/新帳號/web_browser_robotic_process_automation_site.git`，使用者名稱填新帳號，權杖用只開放這個倉庫、Contents 可讀寫的 fine-grained 權杖。
3. 在同步頁檢查狀態，拉取或推送一次，看到「已同步」就完成了。

---

## 8. 重建 Release（安裝檔）

舊 Release 的安裝檔只在舊 GitHub 上，要在新倉庫重新建置。建好的是**草稿**，確認後按「Publish release」才會公開。

**有原本的私鑰（5.1 情況 A）**：可以重建 v0.8.0。

```bash
cd …/01-repos/web_browser_robotic_process_automation
git push origin :refs/tags/v0.8.0     # 先刪掉新倉庫上的標籤
git push origin v0.8.0                # 再單獨推一次，觸發「發布」
```

新倉庫還沒有上一個 Release，所以說明裡不會有「從 v0.7.1 升級」那一段，其他照舊。舊版本一般不必重建。

**換了新私鑰（5.1 情況 B）**：v0.8.0 重建不了，因為那個標籤的 `keys.py` 是舊公鑰，發布流程核對對不上就會停下。改發一個新版本：

```bash
git switch -c release/0.8.1
python3 tools/release_version.py bump 0.8.1     # 一次改全部套件與 uv.lock
git commit -am "chore: 版本 0.8.1"
git push -u origin release/0.8.1               # 開 PR，CI 通過後合併
git switch main && git pull
git tag v0.8.1 && git push origin v0.8.1       # 觸發「發布」
```

版本號由你決定。不論哪種情況，`main` 上還有尚未發布的 Python 節點：依 ADR 0020，它會讓下一個版本的 RPA Worker 與伺服器分發包都要用完整的安裝包。詳細流程見 `docs/design/desktop.html` 的「發布」。

---

## 9. 更新已經在用的伺服器與電腦

- **用一鍵安裝（git clone）裝的伺服器**：在 clone 的資料夾執行：
  ```bash
  git remote set-url origin https://github.com/新帳號/web_browser_robotic_process_automation.git
  git fetch origin
  ```
- **用分發包裝的伺服器**：沒有 git，下一次照新倉庫的 Release 升級即可。
- **RPA Worker 與錄製端**：連的是你的管理 Portal，不是 GitHub，所以照常運作。只有「下載新版」會連到舊網址，要等裝了新版本才會改。新版本請從新倉庫的 Releases 下載。
- **開發用的電腦**：舊的 clone 一樣用 `git remote set-url origin <新網址>` 改過去。

---

## 10. 讓 Claude、ChatGPT／Codex 繼續接手

1. 在 claude.ai 的 Settings › Connectors 連接新的 GitHub 帳號，並把 Claude 的 GitHub App 安裝到兩個新倉庫。舊帳號的安裝已經不能用了。ChatGPT／Codex 也一樣要重新連接。
2. PR #114（文檔對齊 v0.8.0）的分支 `docs/refresh-v0-8` 已經推上去了，在新倉庫從它開一個 PR 到 `main`。說明可以照 `02-github-metadata/open-pr-114.md` 貼上。
3. 新倉庫的 PR 與 issue 編號從 #1 重新開始，`handoff/` 裡的 #1～#114 指的都是舊倉庫。建議在 `handoff/decisions.html` 記一條決定：搬家的日期、新網址，以及「`handoff/` 裡 2026-11-08 以前的 #編號都是舊倉庫的；對照見 PR 對照表」。這樣之後接手的人不會搞混。把 `02-github-metadata/` 放進倉庫（例如 `handoff/materials/github-migration/`）也可以。

---

## 11. 只在舊 GitHub 上、帶不走的東西

除非找回舊帳號再用 Transfer，否則以下這些沒有辦法帶走（詳見 `02-github-metadata/repository-info.md`）：

- PR 的說明、討論與審閱留言。程式改動都在 git 歷史裡；PR 對照表在 `pull-requests-merged.md`；`handoff/tasks/` 的任務紀錄寫了各項工作的來龍去脈。
- Issues（多半是每晚測試與安裝腳本自動開的失敗通知）。
- Release 的安裝檔與原始說明：第 8 節重建；各版內容見 `handoff/tasks/*release*` 的紀錄。
- Actions 的執行紀錄、日誌與產物；`ci-metrics` 分支。
- Secrets 的值（第 5 節重設）、分支保護、Webhook、部署金鑰（第 6、7 節重設）。
- Star 與 Watch。

---

## 12. 檢查清單

- [ ] 試過找回舊帳號（重設密碼或向 GitHub Support 申訴）；找回了就改用 Transfer
- [ ] 解壓縮後確認校驗碼（見下方）
- [ ] 新帳號開了兩步驟驗證，recovery codes 已保存
- [ ] 建立兩個空倉庫（不勾 README、.gitignore、License）
- [ ] `push-to-new-github.sh` 顯示兩個 ✓
- [ ] 新倉庫：預設分支是 `main`，有 2 個分支、11 個標籤
- [ ] `update-repo-url.sh` 改完網址，PR 合併
- [ ] `RPA_UPDATE_SIGNING_KEY`：找回舊私鑰並核對公鑰，或換新金鑰並改好 `keys.py`
- [ ] `RPA_UPDATE_CI_KEY` 設好
- [ ] Actions：勾選「Allow GitHub Actions to create and approve pull requests」；Issues 開著
- [ ] 第一次 CI 全部通過
- [ ] 資料倉庫：伺服器上更新的歷史推上去了；Portal 的同步改成新倉庫並同步成功
- [ ] 重建 Release（v0.8.0 或新版本），確認後發布
- [ ] 伺服器 clone 的 `origin` 改成新網址
- [ ] 重新連接 Claude、ChatGPT／Codex
- [ ] `docs/refresh-v0-8` 開 PR；在 `handoff/decisions.html` 記下搬家

---

## 附錄 A：常見問題

| 狀況 | 怎麼辦 |
|---|---|
| `remote: Permission to … denied`、`403` | 這台電腦還沒登入新帳號，或用了沒有權限的權杖。執行 `gh auth login`，或改用有 `repo` 權限的權杖 |
| `refusing to allow a Personal Access Token to create or update workflow … without workflow scope` | 權杖少了 `workflow` 權限。用 GitHub CLI 的話執行 `gh auth refresh -s workflow`；用權杖的話建一個勾了 `workflow` 的新權杖 |
| `! [rejected] main -> main (fetch first)` | 新倉庫不是空的，建立時勾了 README 之類。刪掉倉庫重建，不要勾任何東西 |
| `shallow update not allowed` | 不該出現；包裡的兩個倉庫都是完整歷史。真的遇到了，改用第 3.4 節從 bundle 還原 |
| 解壓後 `git status` 顯示有檔案被刪除或改動 | 多半是解壓工具把中文檔名（`docs/design-system/驗證紀錄.txt` 等）弄壞了。執行 `git restore .`，或改用 7-Zip 解壓，或從 bundle 還原 |
| 推了一兩個 `v` 標籤，觸發了不想要的「發布」 | 到 Actions 取消那次執行；如果已經建了草稿 Release，在 Releases 頁刪掉草稿 |
| 推送後看不到 Actions 在跑 | Settings › Actions › General 確認沒有被停用 |

## 附錄 B：校驗

```bash
cd ~/rpa-migration/rpa-github-migration-2026-11-08
shasum -a 256 -c SHA256SUMS.txt      # Linux 用 sha256sum -c SHA256SUMS.txt
```

全部顯示 `OK` 就代表檔案完整。也可以在主倉庫資料夾執行 `git fsck --full`，沒有輸出錯誤就代表 git 資料完整。

## 附錄 C：這個包是怎麼做的

- 主倉庫：2026-11-07 在 GitHub 停權前 clone，`git fetch --depth=300` 已經抓到第一個提交，所以是完整歷史。乾淨地 clone 一份、`main` 為工作區，`git fsck --full` 通過，再做成 bundle（`--branches --tags`）。
- 資料倉庫：clone 時只抓了最新的提交，但它就是根提交（沒有上一個提交），所以拿掉淺層標記後就是完整歷史。`git fsck --full` 通過。
- 兩支腳本：在模擬環境推到空的 bare 倉庫，全部分支與標籤核對一致，重複執行沒有問題。`update-repo-url.sh` 改完後，文檔與多語言測試和改之前相同：367 項通過，1 項是需要 OpenCC 的簡中產生檢查，製作環境沒有 OpenCC；安裝檔與 App 的網址也確認一致。
- PR 對照表：從 `main` 歷史裡的「Merge pull request #N」與壓縮合併標題的「(#N)」整理而成。
