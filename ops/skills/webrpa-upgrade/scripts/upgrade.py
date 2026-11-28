# ruff: noqa: T201
# 獨立維運命令列工具，print 為預期的狀態輸出。
"""從 Windows／Linux 主控端準備、執行及追蹤指定版本的完整包升級。"""

import argparse
import hashlib
import json
import re
import shlex
import subprocess
import sys
import tarfile
import time
import uuid
from pathlib import Path

TERMINAL = {"succeeded", "already_current", "rolled_back", "needs_human", "blocked"}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def run(args, timeout=120):
    result = subprocess.run(
        args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout
    )
    require(
        result.returncode == 0, "命令失敗：" + str(args[0]) + "; " + result.stderr.strip()[:500]
    )
    return result.stdout.strip()


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def ssh(profile, args):
    return run(
        [
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=15",
            "-o",
            "StrictHostKeyChecking=yes",
            profile["ssh"],
            shlex.join(args),
        ]
    )


def copy(profile, local, remote):
    run(
        [
            "scp",
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=15",
            "-o",
            "StrictHostKeyChecking=yes",
            str(local),
            profile["ssh"] + ":" + remote,
        ],
        timeout=900,
    )


def curl(profile, url, path, resume=False):
    args = [
        "curl",
        "--proxy",
        profile["proxy"],
        "--noproxy",
        "",
        "--http1.1",
        "--location",
        "--fail",
        "--silent",
        "--show-error",
        "--connect-timeout",
        "20",
        "--speed-limit",
        "1024",
        "--speed-time",
        "30",
        "--max-time",
        "600",
    ]
    if resume:
        args += ["--continue-at", "-"]
    run([*args, "--output", str(path), url], timeout=630)


def assets(release, target):
    require(
        release["tag_name"] == "v" + target and not release["draft"] and not release["prerelease"],
        "版本不是指定的正式發布，請人工確認",
    )
    name = "RPA-Server-" + target + "-linux-x64.tar.gz"
    matches = [item for item in release["assets"] if item["name"] == name]
    sums = [item for item in release["assets"] if item["name"] == "SHA256SUMS.txt"]
    require(len(matches) == len(sums) == 1, "正式 Release 缺少唯一的 x64 完整包或校驗文件")
    return matches[0], sums[0]


def official_url(url, repository, target, name):
    require(
        url == f"https://github.com/{repository}/releases/download/v{target}/{name}",
        "資產網址不是指定倉庫的正式 Release",
    )


def download(profile, target, cache):
    cache.mkdir(parents=True, exist_ok=True)
    metadata = cache / "release.json"
    curl(
        profile,
        f"https://api.github.com/repos/{profile['repository']}/releases/tags/v{target}",
        metadata,
    )
    release = json.loads(metadata.read_text(encoding="utf-8"))
    package, sums = assets(release, target)
    for item in (package, sums):
        official_url(item["browser_download_url"], profile["repository"], target, item["name"])
    checksums = cache / "SHA256SUMS.txt"
    curl(profile, sums["browser_download_url"], checksums)
    matches = [
        line.split()[0].lower()
        for line in checksums.read_text().splitlines()
        if len(line.split()) == 2 and line.split()[1].lstrip("*") == package["name"]
    ]
    require(
        len(matches) == 1 and re.fullmatch(r"[a-f0-9]{64}", matches[0]), "官方 SHA-256 格式錯誤"
    )
    expected = matches[0]
    digest = package.get("digest")
    require(not digest or digest == "sha256:" + expected, "Release API 與校驗文件不一致")
    destination = cache / package["name"]
    if destination.exists():
        require(
            destination.stat().st_size == package["size"] and sha256(destination) == expected,
            "既有本機安裝包不符，保留檔案並請人工確認",
        )
    else:
        partial = destination.with_suffix(destination.suffix + ".part")
        for attempt in range(3):
            try:
                curl(profile, package["browser_download_url"], partial, resume=True)
                break
            except (RuntimeError, subprocess.TimeoutExpired):
                if attempt == 2:
                    raise
        require(
            partial.stat().st_size == package["size"] and sha256(partial) == expected,
            "下載校驗失敗，保留 .part，不上傳或安裝",
        )
        partial.replace(destination)
    return destination, {"version": target, "sha256": expected, "size": package["size"]}


def prepare(profile, profile_path, target):
    require(re.fullmatch(r"\d+\.\d+\.\d+", target), "請指定 x.y.z，不接受 latest 或預發布版本")
    require(
        re.fullmatch(r"[A-Za-z0-9_.-]+", profile["ssh"]) and not profile["ssh"].startswith("-"),
        "SSH 別名不合法",
    )
    require(
        re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", profile["repository"]), "倉庫名稱不合法"
    )
    require(re.fullmatch(r"/[A-Za-z0-9_/-]+", profile["work"]), "主機工作目錄不合法")
    require(re.fullmatch(r"/[A-Za-z0-9_./-]+", profile["python"]), "主機 Python 路徑不合法")
    cache = profile_path.parent / "cache" / target
    package, manifest = download(profile, target, cache)
    identifier = uuid.uuid4().hex
    job = profile["work"] + "/jobs/" + identifier
    remote_package = profile["work"] + "/packages/" + manifest["sha256"] + ".tar.gz"
    ssh(
        profile,
        [
            "install",
            "-d",
            "-m",
            "700",
            profile["work"],
            profile["work"] + "/packages",
            profile["work"] + "/jobs",
            job,
        ],
    )
    present = ssh(
        profile, ["sh", "-c", 'if [ -f "$1" ]; then sha256sum "$1"; fi', "_", remote_package]
    )
    if not present.startswith(manifest["sha256"] + " "):
        staging = remote_package + "." + identifier + ".part"
        copy(profile, package, staging)
        actual = ssh(profile, ["sha256sum", staging]).split()[0]
        require(actual == manifest["sha256"], "遠端上傳校驗失敗，未替換正式安裝包")
        ssh(profile, ["mv", staging, remote_package])
    manifest["package"] = remote_package
    local_job = profile_path.parent / "jobs" / identifier
    local_job.mkdir(parents=True)
    (local_job / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    # 凍結本次腳本及設定；維護技能時不讓正在派送的交易混用兩個版本。
    remote_script = local_job / "remote.py"
    remote_script.write_bytes(Path(__file__).with_name("remote.py").read_bytes())
    (local_job / "profile.json").write_text(json.dumps(profile), encoding="utf-8")
    transfer = local_job / "transfer.tar"
    with tarfile.open(transfer, "w") as archive:
        for name in ("remote.py", "profile.json", "manifest.json"):
            archive.add(local_job / name, arcname=name)
    copy(profile, transfer, job + "/transfer.tar")
    uploaded_hash = ssh(
        profile,
        [
            "sh",
            "-c",
            'tar -xf "$1/transfer.tar" -C "$1" && '
            'chmod 600 "$1/remote.py" "$1/profile.json" "$1/manifest.json" && '
            'sha256sum "$1/remote.py"',
            "_",
            job,
        ],
    ).split()[0]
    require(
        uploaded_hash == sha256(remote_script),
        "主機腳本校驗失敗",
    )
    record = {
        "job": job,
        "unit": "webrpa-upgrade-" + identifier,
        "profile": str(local_job / "profile.json"),
        "source_profile": str(profile_path),
    }
    record_path = local_job / "job.json"
    record_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print("Job record: " + str(record_path), flush=True)
    return record, record_path


def status(profile, record):
    result = ssh(profile, ["cat", record["job"] + "/result.json"])
    return json.loads(result)


def launch(profile, record):
    args = [
        profile["python"],
        record["job"] + "/remote.py",
        "--profile",
        record["job"] + "/profile.json",
        "--job",
        record["job"],
        "--apply",
    ]
    # transient systemd 工作不依附 SSH；連線中斷時繼續備份／回退。
    return ssh(
        profile,
        [
            "systemd-run",
            "--collect",
            "--unit",
            record["unit"],
            "--property=Type=exec",
            "--property=UMask=0077",
            "--property=TimeoutStopSec=180",
            *args,
        ],
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profile", type=Path, default=Path.home() / ".codex/webrpa-upgrade/profile.json"
    )
    parser.add_argument("--version")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--status", type=Path)
    args = parser.parse_args()
    require(not (args.status and (args.version or args.apply)), "status 不可同時提交新版本")
    profile_path = args.profile.resolve()
    if args.status:
        record = json.loads(args.status.read_text())
        profile_path = Path(record["profile"])
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    if args.status:
        print(json.dumps(status(profile, record), ensure_ascii=False, indent=2))
        return 0
    require(args.version is not None, "缺少明確目標版本")
    record, record_path = prepare(profile, profile_path, args.version.removeprefix("v"))
    if not args.apply:
        result = ssh(
            profile,
            [
                profile["python"],
                record["job"] + "/remote.py",
                "--profile",
                record["job"] + "/profile.json",
                "--job",
                record["job"],
            ],
        )
        print(result)
        return 0
    # 派送結果不確定時不能再派一次；使用已保存的 job.json 讀取狀態。
    try:
        launch(profile, record)
    except Exception:
        print("Dispatch uncertain. Read status; do not resubmit: " + str(record_path))
        return 3
    previous = None
    for _ in range(90):
        try:
            result = status(profile, record)
            if result["stage"] != previous:
                print(json.dumps(result, ensure_ascii=False), flush=True)
                previous = result["stage"]
            if result["stage"] in TERMINAL:
                return 0 if result["stage"] in ("succeeded", "already_current") else 2
            active = ssh(
                profile, ["systemctl", "show", record["unit"], "-p", "ActiveState", "--value"]
            )
            if active not in ("active", "activating"):
                print(
                    "Job stopped before terminal state. Human recovery required: "
                    + str(record_path)
                )
                return 2
        except Exception:
            print(
                "Connection unavailable; the remote job may still be running. Status: "
                + str(record_path),
                flush=True,
            )
        time.sleep(20)
    print("Continue with --status " + str(record_path))
    return 3


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print("NEEDS_HUMAN: " + str(error), file=sys.stderr)
        raise SystemExit(2) from None
