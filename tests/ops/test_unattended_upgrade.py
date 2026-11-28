"""從既有 CI 執行獨立維運技能的標準函式庫測試。"""

import subprocess
import sys
from pathlib import Path


def test_unattended_upgrade_transactions() -> None:
    root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [
            sys.executable,
            "-X",
            "utf8",
            "-m",
            "unittest",
            "discover",
            "-s",
            str(root / "ops/skills/webrpa-upgrade/tests"),
            "-v",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=180,
        cwd=root,
    )
    assert result.returncode == 0, result.stdout + result.stderr
