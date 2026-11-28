# ruff: noqa: PT009, PT027
# 使用標準函式庫 unittest，讓沒有 pytest 的主機也能驗證。
"""隔離檔案系統與假的 systemd；不操作正式服務。"""

import io
import json
import os
import sqlite3
import sys
import tarfile
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import remote
import upgrade as controller


def database(path):
    path.mkdir()
    con = sqlite3.connect(path / "rpa.db")
    for table in ("users", "domains", "scenes", "revisions", "roles"):
        con.execute("CREATE TABLE " + table + "(id INTEGER)")
        con.execute("INSERT INTO " + table + " VALUES (1)")
    con.execute("CREATE TABLE workers(id INTEGER, current_run TEXT)")
    con.execute("INSERT INTO workers VALUES (1, NULL)")
    con.execute("CREATE TABLE recorders(id INTEGER, disabled INTEGER, last_seen_at TEXT)")
    con.execute("INSERT INTO recorders VALUES (1, 0, NULL)")
    for table in ("runs", "recordings", "workflow_runs", "batches"):
        con.execute("CREATE TABLE " + table + "(status TEXT)")
    con.execute("INSERT INTO runs VALUES ('passed')")
    con.commit()
    con.close()
    for folder in ("domains", "roles"):
        (path / folder).mkdir()
        (path / folder / "sample").write_text("original fixture")
    for file in ("secrets.key", "secrets.json"):
        (path / file).write_text("fixture, not a credential")


class FakeUpgrade(remote.Upgrade):
    def __init__(self, profile, job, manifest, failure=None):
        super().__init__(profile, job, manifest)
        self.unit = job.parent.parent.parent / "service"
        self.dropins = job.parent.parent.parent / "dropins"
        self.maintenance = job.parent.parent.parent / "run" / "maintenance.conf"
        self.unit.write_text("original unit")
        self.p["fingerprint"] = self.service_fingerprint()
        self.failure = failure
        self.running = True
        self.stops = 0

    def command(self, args, timeout=120):
        if args[0] == "systemctl":
            if args[1] == "stop":
                self.stops += 1
                self.running = False
            elif args[1] == "start":
                self.running = True
            elif args[1] == "is-enabled":
                return "enabled"
            return ""
        if args[0] == "bash":
            release = self.prefix / "releases/0.12.0-1234567"
            release.mkdir()
            (release / "BUILD_INFO").write_text("version=0.12.0\n")
            (self.prefix / "current").unlink()
            (self.prefix / "current").symlink_to(release)
            if self.failure == "data":
                (self.data / "domains/sample").write_text("unexpected mutation")
            if self.failure == "install":
                raise remote.HelpNeededError("injected install failure")
            return ""
        if args[0].endswith("/bin/rpa"):
            return "rpa 0.12.0"
        return super().command(args, timeout)

    def health(self, loopback=False):
        if not self.running:
            raise remote.HelpNeededError("service stopped")
        current = (self.prefix / "current").resolve().name
        if current.startswith("0.12.0"):
            if self.failure == "private" and loopback:
                raise remote.HelpNeededError("injected private health failure")
            if self.failure == "public" and not loopback:
                raise remote.HelpNeededError("injected public health failure")

    def backup(self):
        if self.failure == "backup":
            raise remote.HelpNeededError("injected backup failure")
        super().backup()


@unittest.skipIf(os.name == "nt", "Linux 的 tar、路徑與符號連結交易在隔離 Linux 目錄驗證")
class TransactionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="webrpa-upgrade-test-")
        self.root = Path(self.temp.name)
        self.prefix = self.root / "prefix"
        self.data = self.root / "data"
        self.work = self.root / "work"
        self.job = self.work / "jobs/fixture"
        self.job.mkdir(parents=True)
        (self.work / "packages").mkdir()
        old = self.prefix / "releases/0.11.0-abcdef0"
        old.mkdir(parents=True)
        (old / "BUILD_INFO").write_text("version=0.11.0\n")
        (self.prefix / "current").symlink_to(old)
        (self.prefix / "rpa-server.env").write_text("preserve me")
        database(self.data)
        package = self.work / "packages/fixture.tar.gz"
        with tarfile.open(package, "w:gz") as tar:
            info = (
                b"app=server\nversion=0.12.0\narch=x86_64\ncommit=1234567\n"
                b"runtime=0123456789abcdef\n"
            )
            item = tarfile.TarInfo("RPA-Server-0.12.0-linux-x64/BUILD_INFO")
            item.size = len(info)
            tar.addfile(item, io.BytesIO(info))
        self.manifest = {
            "version": "0.12.0",
            "package": str(package),
            "sha256": remote.sha256(package),
            "size": package.stat().st_size,
        }
        self.profile = {
            "prefix": str(self.prefix),
            "data": str(self.data),
            "work": str(self.work),
            "service": "rpa-server.service",
            "host": "0.0.0.0",
            "ports": [8080, 8081, 8765],
        }
        self.sleep = patch.object(remote.time, "sleep")
        self.sleep.start()
        self.euid = patch.object(remote.os, "geteuid", return_value=0)
        self.euid.start()

    def tearDown(self):
        self.sleep.stop()
        self.euid.stop()
        self.temp.cleanup()

    def engine(self, failure=None):
        return FakeUpgrade(self.profile, self.job, self.manifest, failure)

    def state(self):
        return json.loads((self.job / "result.json").read_text())["stage"]

    def test_success_preserves_data_and_backup(self):
        engine = self.engine()
        before = remote.snapshot(self.data)
        self.assertEqual(remote.execute(engine, True), 0)
        self.assertEqual(self.state(), "succeeded")
        self.assertEqual(before, remote.snapshot(self.data))
        self.assertTrue((self.job / "data.tar.gz").is_file())
        self.assertFalse(engine.maintenance.exists())

    def test_check_never_stops_or_installs(self):
        engine = self.engine()
        self.assertEqual(remote.execute(engine, False), 0)
        self.assertEqual(self.state(), "checked")
        self.assertEqual(engine.stops, 0)
        self.assertFalse((self.job / "data.tar.gz").exists())

    def test_same_version_noop(self):
        self.manifest["version"] = "0.11.0"
        engine = self.engine()
        self.assertEqual(remote.execute(engine, True), 0)
        self.assertEqual(self.state(), "already_current")
        self.assertEqual(engine.stops, 0)

    def test_downgrade_stops_before_service(self):
        self.manifest["version"] = "0.10.0"
        engine = self.engine()
        self.assertEqual(remote.execute(engine, True), 2)
        self.assertEqual(engine.stops, 0)

    def test_corrupt_package_stops_before_service(self):
        Path(self.manifest["package"]).write_bytes(b"corrupt")
        engine = self.engine()
        self.assertEqual(remote.execute(engine, True), 2)
        self.assertEqual(engine.stops, 0)

    def test_busy_database_stops_before_service(self):
        with sqlite3.connect(self.data / "rpa.db") as con:
            con.execute("INSERT INTO runs VALUES ('running')")
        engine = self.engine()
        self.assertEqual(remote.execute(engine, True), 2)
        self.assertEqual(engine.stops, 0)

    def test_online_recorder_stops_before_service(self):
        with sqlite3.connect(self.data / "rpa.db") as con:
            con.execute("UPDATE recorders SET last_seen_at=?", (datetime.now(UTC).isoformat(),))
        engine = self.engine()
        self.assertEqual(remote.execute(engine, True), 2)
        self.assertEqual(engine.stops, 0)

    def test_config_drift_stops_before_service(self):
        engine = self.engine()
        engine.unit.write_text("changed configuration")
        self.assertEqual(remote.execute(engine, True), 2)
        self.assertEqual(engine.stops, 0)

    def test_backup_failure_restarts_old(self):
        engine = self.engine("backup")
        self.assertEqual(remote.execute(engine, True), 1)
        self.assertEqual(self.state(), "rolled_back")
        self.assertTrue(engine.running)
        self.assertFalse((self.job / "failed-data").exists())

    def test_install_failure_restores_full_backup(self):
        engine = self.engine("install")
        self.assertEqual(remote.execute(engine, True), 1)
        self.assertEqual(self.state(), "rolled_back")
        self.assertEqual((self.prefix / "current").resolve().name, "0.11.0-abcdef0")
        self.assertTrue((self.job / "failed-data").is_dir())

    def test_failed_private_health_restores_old(self):
        engine = self.engine("private")
        self.assertEqual(remote.execute(engine, True), 1)
        self.assertEqual(self.state(), "rolled_back")

    def test_data_change_rolls_back(self):
        engine = self.engine("data")
        self.assertEqual(remote.execute(engine, True), 1)
        self.assertEqual((self.data / "domains/sample").read_text(), "original fixture")
        self.assertEqual(
            (self.job / "failed-data/domains/sample").read_text(), "unexpected mutation"
        )

    def test_public_failure_never_restores_old_data(self):
        engine = self.engine("public")
        self.assertEqual(remote.execute(engine, True), 2)
        self.assertEqual(self.state(), "needs_human")
        self.assertTrue(engine.published)
        self.assertFalse((self.job / "failed-data").exists())
        self.assertEqual((self.prefix / "current").resolve().name, "0.12.0-1234567")

    def test_restore_failure_requests_help(self):
        engine = self.engine("install")
        with patch.object(engine, "restore", side_effect=OSError("restore failed")):
            self.assertEqual(remote.execute(engine, True), 2)
        self.assertEqual(self.state(), "needs_human")

    def test_unknown_run_state_blocks_upgrade(self):
        with sqlite3.connect(self.data / "rpa.db") as con:
            con.execute("INSERT INTO runs VALUES ('new_unknown_state')")
        engine = self.engine()
        self.assertEqual(remote.execute(engine, True), 2)
        self.assertEqual(engine.stops, 0)

    def test_transaction_lock_blocks_second_runner(self):
        import fcntl

        engine = self.engine()
        profile = self.job / "profile.json"
        profile.write_text(json.dumps(self.profile))
        (self.job / "manifest.json").write_text(json.dumps(self.manifest))
        with (self.work / "upgrade.lock").open("w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with (
                patch.object(remote, "Upgrade", return_value=engine),
                patch.object(
                    sys,
                    "argv",
                    ["remote.py", "--profile", str(profile), "--job", str(self.job), "--apply"],
                ),
            ):
                self.assertEqual(remote.main(), 2)
        self.assertEqual(engine.stops, 0)

    def test_unfinished_previous_job_blocks_new_upgrade(self):
        engine = self.engine()
        profile = self.job / "profile.json"
        profile.write_text(json.dumps(self.profile))
        (self.job / "manifest.json").write_text(json.dumps(self.manifest))
        previous = self.work / "jobs/previous"
        previous.mkdir()
        (previous / "result.json").write_text(json.dumps({"stage": "installing"}))
        (self.work / "active.json").write_text(json.dumps({"job": str(previous)}))
        with (
            patch.object(remote, "Upgrade", return_value=engine),
            patch.object(
                sys,
                "argv",
                ["remote.py", "--profile", str(profile), "--job", str(self.job), "--apply"],
            ),
        ):
            self.assertEqual(remote.main(), 2)
        self.assertEqual(engine.stops, 0)


class PureTests(unittest.TestCase):
    def test_full_asset_only(self):
        release = {
            "tag_name": "v0.12.0",
            "draft": False,
            "prerelease": False,
            "assets": [{"name": "RPA-Update-0.12.0.zip"}, {"name": "SHA256SUMS.txt"}],
        }
        with self.assertRaises(RuntimeError):
            controller.assets(release, "0.12.0")

    def test_draft_rejected(self):
        with self.assertRaises(RuntimeError):
            controller.assets({"tag_name": "v0.12.0", "draft": True}, "0.12.0")

    def test_untrusted_download_url_rejected(self):
        with self.assertRaises(RuntimeError):
            controller.official_url("https://example.test/fake", "org/repo", "0.12.0", "a.tar.gz")

    def test_versions_compared_numerically(self):
        self.assertGreater(remote.version("0.12.0"), remote.version("0.9.0"))
        with self.assertRaises(remote.HelpNeededError):
            remote.version("latest")

    def test_archive_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.tar.gz"
            with tarfile.open(path, "w:gz") as tar:
                item = tarfile.TarInfo("bundle/../../outside")
                item.size = 1
                tar.addfile(item, io.BytesIO(b"x"))
            with self.assertRaises(remote.HelpNeededError):
                remote.verify_archive(path, "bundle")

    def test_data_loss_is_not_accepted_as_migration(self):
        with self.assertRaises(remote.HelpNeededError):
            remote.compare_snapshots(
                {"counts": {"scenes": 2}, "hashes": {}}, {"counts": {"scenes": 1}, "hashes": {}}
            )

    def test_new_examples_are_allowed(self):
        remote.compare_snapshots(
            {"counts": {"scenes": 1}, "hashes": {"a": "x"}},
            {"counts": {"scenes": 2}, "hashes": {"a": "x", "b": "y"}},
        )


if __name__ == "__main__":
    unittest.main()
