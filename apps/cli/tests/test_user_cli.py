"""`rpa user`（M8，ADR 0025）：在伺服器這台建立系統管理員、重設忘記的密碼。"""

from pathlib import Path

from click.testing import CliRunner, Result
from sqlalchemy.orm import sessionmaker

from rpa_cli.i18n import install_click_translations
from rpa_cli.main import build_cli
from rpa_core.i18n import use_locale
from rpa_server.auth import AccountService
from rpa_server.config import sqlite_url
from rpa_server.db import create_db_engine


def invoke(args: list[str], answers: str) -> Result:
    with use_locale("zh-Hant"):
        install_click_translations()
        return CliRunner().invoke(build_cli(), args, input=answers, env={"RPA_DATA_DIR": ""})


def accounts(data: Path) -> AccountService:
    engine = create_db_engine(sqlite_url(data / "rpa.db"))
    return AccountService(sessionmaker(engine, expire_on_commit=False))


def test_create_admin_and_reset_password(tmp_path: Path) -> None:
    data = tmp_path / "data"
    created = invoke(
        ["user", "create", "Root", "--admin", "--name", "管理員", "--data", str(data)],
        "first-password\nfirst-password\n",
    )
    assert created.exit_code == 0, created.output
    assert "已建立帳號 root" in created.output
    users = accounts(data).list_users()
    assert [(user.username, user.display_name, user.system_admin) for user in users] == [
        ("root", "管理員", True)
    ]
    accounts(data).login("root", "first-password")

    reset = invoke(["user", "password", "root", "--data", str(data)], "second-pass\nsecond-pass\n")
    assert reset.exit_code == 0, reset.output
    assert "已重設 root 的密碼" in reset.output
    accounts(data).login("root", "second-pass")

    missing = invoke(
        ["user", "password", "nobody", "--data", str(data)], "x-password\nx-password\n"
    )
    assert missing.exit_code == 1
    assert "找不到帳號 nobody" in missing.output
    short = invoke(["user", "create", "amy", "--data", str(data)], "short\nshort\n")
    assert short.exit_code == 1
    assert "密碼至少要 8 個字" in short.output
