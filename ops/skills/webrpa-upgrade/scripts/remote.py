# ruff: noqa: T201
# 獨立維運命令列工具，print 為預期的狀態輸出。
"""受管理 Linux 主機的完整包升級交易；僅用標準函式庫。"""

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import sqlite3
import subprocess
import sys
import tarfile
import time
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo


class HelpNeededError(RuntimeError):
    """目前條件無法自動處理，保留現況與證據。"""


def require(condition, reason):
    if not condition:
        raise HelpNeededError(reason)


def timestamp():
    return datetime.now(ZoneInfo("America/Los_Angeles")).isoformat()


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def version(value):
    require(bool(re.fullmatch(r"\d+\.\d+\.\d+", value)), "需指定穩定版 x.y.z")
    return tuple(map(int, value.split(".")))


def build_info(path):
    return dict(line.split("=", 1) for line in Path(path).read_text().splitlines() if "=" in line)


def validate_profile(profile):
    for name in ("prefix", "data", "work"):
        value = profile[name]
        require(bool(re.fullmatch(r"/[A-Za-z0-9_./-]+", value)), "設定路徑格式不支援")
        path = Path(value)
        require(".." not in path.parts and len(path.parts) >= 3, "設定路徑過於寬泛")
        require(path.resolve() == path, "設定路徑不能含符號連結")
    paths = [Path(profile[name]) for name in ("prefix", "data", "work")]
    require(
        all(
            a != b and a not in b.parents and b not in a.parents
            for i, a in enumerate(paths)
            for b in paths[i + 1 :]
        ),
        "工作、安裝及資料目錄不可重疊",
    )
    require(profile["service"] == "rpa-server.service", "僅支援已接管的 rpa-server.service")
    require(profile["host"] == "0.0.0.0", "監聽方式已改變，需要重新核對")
    require(profile["ports"] == [8080, 8081, 8765], "端口已改變，需要重新核對")


def snapshot(data, idle=False):
    """不輸出業務內容；完整性、筆數、既有檔案雜湊保存在主機受限目錄。"""
    data = Path(data)
    con = sqlite3.connect(f"file:{data}/rpa.db?mode=ro", uri=True)
    try:
        con.execute("PRAGMA query_only=ON")
        require(
            con.execute("PRAGMA integrity_check").fetchall() == [("ok",)], "資料庫完整性檢查失敗"
        )
        tables = {
            row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        required = (
            "users",
            "domains",
            "scenes",
            "revisions",
            "roles",
            "workers",
            "recorders",
            "runs",
        )
        require(set(required) <= tables, "資料庫結構不在已驗證範圍")
        counts = {
            name: con.execute("SELECT count(*) FROM " + name).fetchone()[0] for name in required
        }
        if idle:
            terminal = (
                "passed",
                "failed",
                "cancelled",
                "timed_out",
                "needs_login",
                "done",
                "finished",
                "stopped",
                "draft",
            )
            for name in ("runs", "recordings", "workflow_runs", "batches"):
                require(name in tables, "缺少工作狀態資料表")
                states = {row[0] for row in con.execute("SELECT DISTINCT status FROM " + name)}
                require(states <= set(terminal), "仍有工作或未知狀態：" + name)
            require(
                con.execute(
                    "SELECT count(*) FROM workers WHERE current_run IS NOT NULL"
                ).fetchone()[0]
                == 0,
                "仍有已指派的 Worker 任務",
            )
            # 調試及人工登入只保存在記憶體；在線錄製端不能被誤判成閒置。
            for (seen,) in con.execute("SELECT last_seen_at FROM recorders WHERE disabled=0"):
                if seen:
                    when = datetime.fromisoformat(seen)
                    when = when.replace(tzinfo=UTC) if when.tzinfo is None else when
                    require(
                        (datetime.now(UTC) - when).total_seconds() > 180,
                        "錄製端仍在線，請先結束調試／人工登入並關閉錄製端",
                    )
    finally:
        con.close()
    hashes = {}
    for name in ("secrets.key", "secrets.json", "domains", "roles"):
        target = data / name
        require(target.exists(), "缺少既有關鍵資料：" + name)
        require(not target.is_symlink(), "關鍵資料目錄含符號連結")
        files = target.rglob("*") if target.is_dir() else [target]
        for file in files:
            require(not file.is_symlink(), "資料含外部連結，需人工確認備份範圍")
            if file.is_file():
                hashes[str(file.relative_to(data))] = sha256(file)
    return {"counts": counts, "hashes": hashes}


def compare_snapshots(before, after):
    # 自動匯入的新範例可以增加筆數；刪除舊資料及變更既有檔案不得悄悄接受。
    require(
        all(after["counts"].get(key, -1) >= value for key, value in before["counts"].items()),
        "升級後既有資料筆數減少",
    )
    require(
        all(after["hashes"].get(key) == value for key, value in before["hashes"].items()),
        "升級改變既有場景或憑證檔案，需審閱遷移",
    )


def verify_archive(archive, root):
    """先掃描完整壓縮包；data filter 再限制解壓連結的範圍。"""
    total = 0
    with tarfile.open(archive, "r:gz") as bundle:
        for member in bundle:
            parts = Path(member.name).parts
            require(parts and parts[0] == root and ".." not in parts, "安裝包含非預期路徑")
            require(
                member.isfile() or member.isdir() or member.issym() or member.islnk(),
                "安裝包含特殊檔案",
            )
            total += member.size
    return total


class Upgrade:
    def __init__(self, profile, job, manifest):
        validate_profile(profile)
        self.p = profile
        self.prefix = Path(profile["prefix"])
        self.data = Path(profile["data"])
        self.work = Path(profile["work"])
        self.job = Path(job).resolve()
        require(self.job.parent == self.work / "jobs", "交易目錄不在設定的工作目錄")
        self.m = manifest
        self.bundle = self.job / ("RPA-Server-" + manifest["version"] + "-linux-x64")
        self.package = Path(manifest["package"])
        require(self.package.parent == self.work / "packages", "安裝包路徑不正確")
        self.maintenance = Path("/run/systemd/system/rpa-server.service.d/90-webrpa-upgrade.conf")
        self.unit = Path("/etc/systemd/system/rpa-server.service")
        self.dropins = Path("/etc/systemd/system/rpa-server.service.d")
        self.stopped = False
        self.dirty = False
        self.published = False
        self.backed_up = False
        self.old = ""
        self.baseline = {}

    def command(self, args, timeout=120):
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        with (self.job / "commands.log").open("a", encoding="utf-8") as log:
            log.write(result.stdout + result.stderr)
        require(result.returncode == 0, "命令失敗，詳細內容見主機 commands.log：" + str(args[0]))
        return result.stdout.strip()

    def state(self, stage, **extra):
        result = {
            "stage": stage,
            "version": self.m["version"],
            "job": str(self.job),
            "time": timestamp(),
            **extra,
        }
        write_json(self.job / "result.json", result)
        print(json.dumps(result, ensure_ascii=False), flush=True)

    def systemctl(self, *args):
        return self.command(["systemctl", *args, self.p["service"]])

    def service_fingerprint(self):
        paths = [self.unit, self.prefix / "rpa-server.env"]
        if self.dropins.exists():
            paths.extend(sorted(self.dropins.glob("*.conf")))
        return {str(path): sha256(path) for path in paths}

    def check_process(self, loopback=False):
        require(self.systemctl("is-active") == "active", "服務未運作")
        group = self.systemctl("show", "-p", "ControlGroup", "--value")
        found = []
        for proc in Path("/proc").iterdir():
            if not proc.name.isdigit():
                continue
            try:
                groups = [
                    line.rsplit(":", 1)[-1] for line in (proc / "cgroup").read_text().splitlines()
                ]
                if group not in groups:
                    continue
                args = [arg.decode() for arg in (proc / "cmdline").read_bytes().split(b"\0") if arg]
                if "-m" in args and "rpa_cli" in args and "serve" in args:
                    found.append((proc, args))
            except (FileNotFoundError, ProcessLookupError, PermissionError):
                continue
        require(len(found) == 1, "無法唯一識別 systemd 管理的 RPA 程序")
        proc, args = found[0]
        host = "127.0.0.1" if loopback else self.p["host"]
        expected = {
            "--data": str(self.data),
            "--host": host,
            "--port": "8080",
            "--worker-host": host,
            "--worker-port": "8081",
            "--testsite-host": host,
        }
        for key, value in expected.items():
            require(
                key in args
                and args.index(key) + 1 < len(args)
                and args[args.index(key) + 1] == value,
                "實際程序參數與設定不同：" + key,
            )
        require("--no-local-worker" in args, "本機 Worker 已啟用，需重新評估")
        expected_exe = (self.prefix / "current/python/bin/python3").resolve()
        require((proc / "exe").resolve() == expected_exe, "實際執行環境不是 current 版本")
        environment = dict(
            item.decode().split("=", 1)
            for item in (proc / "environ").read_bytes().split(b"\0")
            if b"=" in item
        )
        release = (self.prefix / "current").resolve()
        require(environment.get("RPA_RELEASE_DIR") == str(release), "執行程序仍使用另一個版本")
        require(environment.get("PYTHONPATH") == str(release / "app"), "執行中的程式碼層不符")

    def health(self, loopback=False):
        self.check_process(loopback)
        for port, path, expected in (
            (8080, "/login", "200"),
            (8081, "/", "401"),
            (8765, "/", "200"),
        ):
            code = self.command(
                [
                    "curl",
                    "--noproxy",
                    "*",
                    "-sS",
                    "-o",
                    "/dev/null",
                    "-w",
                    "%{http_code}",
                    "--max-time",
                    "5",
                    f"http://127.0.0.1:{port}{path}",
                ]
            )
            require(code == expected, "端點檢查失敗：" + str(port))

    def await_health(self, loopback):
        for _ in range(30):
            try:
                self.health(loopback)
                return
            except HelpNeededError:
                time.sleep(1)
        raise HelpNeededError("服務啟動逾時")

    def preflight(self):
        require(os.geteuid() == 0, "此設定需要 root 執行")
        require(sys.version_info >= (3, 12), "交易腳本需要 Python 3.12 以上")
        require(not self.maintenance.exists(), "發現未收尾的維護模式，請人工處理")
        require(self.service_fingerprint() == self.p["fingerprint"], "服務設定已漂移，需重新確認")
        self.health()
        current = (self.prefix / "current").resolve()
        require(current.parent == self.prefix / "releases", "current 不是既有分層安裝")
        info = build_info(current / "BUILD_INFO")
        self.old = current.name
        target = version(self.m["version"])
        previous = version(info["version"])
        require(target >= previous, "拒絕自動降級")
        if target == previous:
            self.state("already_current", current=self.old)
            return False
        require(not (self.prefix / "run/update.state").exists(), "仍有未完成的應用程式更新")
        require(not (self.prefix / "run/restart.request").exists(), "仍有待執行的重新啟動")
        self.baseline = snapshot(self.data, idle=True)
        require(
            self.work.stat().st_dev == self.prefix.stat().st_dev == self.data.stat().st_dev,
            "安裝、資料及備份位於不同檔案系統，需人工安排回退",
        )
        require(
            self.package.is_file() and sha256(self.package) == self.m["sha256"],
            "主機安裝包校驗失敗",
        )
        require(self.package.stat().st_size == self.m["size"], "主機安裝包大小錯誤")
        unpacked = verify_archive(self.package, self.bundle.name)
        size = sum(
            path.stat().st_size
            for root in (self.data, self.prefix)
            for path in root.rglob("*")
            if path.is_file() and not path.is_symlink()
        )
        require(
            shutil.disk_usage(self.work).free > size * 2 + unpacked * 3 + 512 * 1024**2,
            "磁碟空間不足以保留完整備份及失敗現場",
        )
        self.state("checked", current=self.old)
        return True

    def backup(self):
        for source, name in ((self.prefix, "installation.tar.gz"), (self.data, "data.tar.gz")):
            archive = self.job / name
            self.command(
                ["tar", "-I", "gzip -1", "-cf", str(archive), "-C", "/", str(source).lstrip("/")],
                timeout=600,
            )
            self.command(["gzip", "-t", str(archive)], timeout=300)
            # 列舉整個檔案可發現 gzip 正常但 tar 結構損壞的情況。
            with tarfile.open(archive) as contents:
                for _ in contents:
                    pass
        sums = {name: sha256(self.job / name) for name in ("installation.tar.gz", "data.tar.gz")}
        write_json(self.job / "backup-sha256.json", sums)
        write_json(self.job / "baseline.json", self.baseline)
        self.backed_up = True
        self.state("backed_up")

    def maintenance_mode(self):
        self.maintenance.parent.mkdir(parents=True, exist_ok=True)
        args = (
            f"{self.prefix}/bin/rpa serve --host 127.0.0.1 --port 8080 --data {self.data} "
            "--worker-host 127.0.0.1 --worker-port 8081 --no-local-worker --testsite-host 127.0.0.1"
        )
        self.maintenance.write_text("[Service]\nExecStart=\nExecStart=" + args + "\n")
        self.command(["systemctl", "daemon-reload"])

    def remove_maintenance(self):
        self.maintenance.unlink(missing_ok=True)
        self.command(["systemctl", "daemon-reload"])

    def restore(self):
        self.state("rolling_back")
        self.systemctl("stop")
        if self.dirty:
            require(self.backed_up, "缺少已驗證備份，不自動恢復")
            sums = json.loads((self.job / "backup-sha256.json").read_text())
            require(
                all(sha256(self.job / name) == value for name, value in sums.items()),
                "回退備份校驗失敗",
            )
            # 保留失敗現場；不刪除或覆蓋新版本的資料。
            for source, name in ((self.prefix, "installation"), (self.data, "data")):
                require(source.resolve() == source, "回退路徑已變動")
                source.rename(self.job / ("failed-" + name))
                self.command(
                    ["tar", "-xzf", str(self.job / (name + ".tar.gz")), "-C", "/"], timeout=600
                )
        self.remove_maintenance()
        self.systemctl("start")
        self.await_health(False)
        require((self.prefix / "current").resolve().name == self.old, "回退版本不符")
        self.state("rolled_back", reason="新版未通過驗證，已恢復原版本與資料", current=self.old)

    def apply(self):
        self.state("extracting")
        require(not self.bundle.exists(), "交易已執行過，請查看 status，不重複套用")
        with tarfile.open(self.package) as archive:
            archive.extractall(self.job, filter="data")
        info = build_info(self.bundle / "BUILD_INFO")
        require(
            info.get("version") == self.m["version"] and info.get("arch") == "x86_64",
            "完整包版本或架構不符",
        )
        require(
            info.get("app") == "server" and re.fullmatch(r"[0-9a-f]{7,40}", info.get("commit", "")),
            "完整包建置資訊不完整",
        )
        require(re.fullmatch(r"[0-9a-f]{16}", info.get("runtime", "")), "缺少執行環境代號")
        require(
            self.m["version"] in self.command([str(self.bundle / "bin/rpa"), "--version"]),
            "包內程式無法啟動",
        )
        snapshot(self.data, idle=True)
        self.state("stopping", previous=self.old)
        self.stopped = True
        self.systemctl("stop")
        self.baseline = snapshot(self.data, idle=True)
        self.backup()
        self.state("installing")
        self.dirty = True
        self.maintenance_mode()
        keep = len(list((self.prefix / "releases").iterdir())) + 2
        self.command(
            [
                "bash",
                str(self.bundle / "install.sh"),
                "--prefix",
                str(self.prefix),
                "--skip-system-packages",
                "--keep",
                str(keep),
            ],
            timeout=600,
        )
        require(self.service_fingerprint() == self.p["fingerprint"], "安裝過程改變服務設定")
        target = self.m["version"] + "-" + info["commit"]
        require((self.prefix / "current").resolve().name == target, "安裝未切換至目標版本")
        self.systemctl("start")
        self.await_health(True)
        compare_snapshots(self.baseline, snapshot(self.data))
        time.sleep(10)
        self.health(True)
        require((self.prefix / "current").resolve().name == target, "應用程式自行退回舊版")
        self.state("verified_private")
        self.systemctl("stop")
        self.remove_maintenance()
        # 對外服務之後可能有新寫入；之後失敗不能還原舊資料覆蓋新資料。
        self.published = True
        self.state("publishing")
        self.systemctl("start")
        self.await_health(False)
        require((self.prefix / "current").resolve().name == target, "對外啟動後版本不符")
        require(self.systemctl("is-enabled") == "enabled", "開機啟動未啟用")
        time.sleep(10)
        self.health(False)
        self.state(
            "succeeded",
            current=target,
            backup=str(self.job),
            protected_files=len(self.baseline["hashes"]),
        )


def execute(upgrade, apply):
    try:
        if upgrade.preflight() and apply:
            upgrade.apply()
        return 0
    except Exception as caught:
        reason = str(caught)
        if upgrade.stopped and not upgrade.published:
            try:
                upgrade.restore()
                return 1
            except Exception as recovery_error:
                reason = "自動回退未完成：" + str(recovery_error)
        stage = "needs_human" if upgrade.stopped else "blocked"
        upgrade.state(stage, reason=reason, exposed=upgrade.published)
        return 2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True)
    parser.add_argument("--job", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    os.umask(0o077)
    profile = json.loads(Path(args.profile).read_text())
    job = Path(args.job)
    manifest = json.loads((job / "manifest.json").read_text())
    upgrade = Upgrade(profile, job, manifest)
    import fcntl

    with (upgrade.work / "upgrade.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            upgrade.state("needs_human", reason="另一個升級交易仍在執行")
            return 2
        active = upgrade.work / "active.json"
        if active.exists():
            old = json.loads(active.read_text())
            if old["job"] != str(job):
                result = Path(old["job"]) / "result.json"
                stage = json.loads(result.read_text()).get("stage") if result.exists() else None
                if stage not in (
                    "succeeded",
                    "already_current",
                    "checked",
                    "rolled_back",
                    "blocked",
                ):
                    upgrade.state("needs_human", reason="上一個交易未安全結束：" + str(old["job"]))
                    return 2
        existing = job / "result.json"
        require(
            not existing.exists() or json.loads(existing.read_text())["stage"] == "checked",
            "不可重放交易；使用 status 檢查既有結果",
        )
        if args.apply:
            write_json(active, {"job": str(job)})

        def interrupted(signum, frame):
            raise HelpNeededError("升級程序收到中斷訊號")

        signal.signal(signal.SIGTERM, interrupted)
        signal.signal(signal.SIGINT, interrupted)
        return execute(upgrade, args.apply)


if __name__ == "__main__":
    raise SystemExit(main())
