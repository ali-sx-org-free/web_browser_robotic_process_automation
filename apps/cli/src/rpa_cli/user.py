"""`rpa user`：在伺服器那台電腦上直接管理帳號（M8，ADR 0025）。

給沒有瀏覽器的伺服器與忘記密碼時用：``rpa user create 帳號 --admin`` 建立（第一個）系統管理員，
``rpa user password 帳號`` 重設密碼（那個帳號的登入全部失效）。直接改資料目錄的資料庫，
不經過管理 Portal；密碼由提示輸入，不放在命令列。
"""

from pathlib import Path
from typing import TYPE_CHECKING

import click

from rpa_cli.i18n import t

if TYPE_CHECKING:
    from rpa_server.auth import AccountService

__all__ = ["build_user_command"]


def _accounts(data_dir: Path | None) -> "AccountService":
    # 伺服器的依賴（SQLAlchemy 等）只在用到時載入，其他子命令不受影響
    from sqlalchemy.orm import sessionmaker

    from rpa_server.auth import AccountService
    from rpa_server.config import Settings
    from rpa_server.db import create_db_engine, upgrade

    settings = Settings.from_env(data_dir=data_dir)
    settings.data_dir.mkdir(parents=True, exist_ok=True)  # 新的資料夾（還沒啟動過伺服器）
    engine = create_db_engine(settings.database_url)
    upgrade(engine)
    return AccountService(sessionmaker(engine, expire_on_commit=False))


def build_user_command() -> click.Group:
    data_option = click.option(
        "--data",
        "data_dir",
        type=click.Path(file_okay=False, path_type=Path),
        default=None,
        help=t("cli.serve.data_help"),
    )

    @click.group(name="user", help=t("cli.user.help"))
    def user() -> None:
        pass

    @user.command(name="create", help=t("cli.user.create_help"))
    @click.argument("username")
    @click.option("--name", "display_name", default="", help=t("cli.user.name_help"))
    @click.option("--admin", is_flag=True, help=t("cli.user.admin_help"))
    @data_option
    def create(username: str, display_name: str, admin: bool, data_dir: Path | None) -> None:
        from rpa_server.errors import ServiceError

        password = click.prompt(
            t("cli.user.password_prompt"), hide_input=True, confirmation_prompt=True
        )
        accounts = _accounts(data_dir)
        try:
            record = accounts.create_user(username, display_name, password, system_admin=admin)
        except ServiceError as error:
            raise click.ClickException(error.message) from error
        click.echo(t("cli.user.created", username=record.username))

    @user.command(name="password", help=t("cli.user.password_help"))
    @click.argument("username")
    @data_option
    def password(username: str, data_dir: Path | None) -> None:
        from rpa_server.errors import ServiceError

        new = click.prompt(t("cli.user.password_prompt"), hide_input=True, confirmation_prompt=True)
        accounts = _accounts(data_dir)
        name = username.strip().lower()
        found = next((item for item in accounts.list_users() if item.username == name), None)
        if found is None:
            raise click.ClickException(t("cli.user.not_found", username=name))
        try:
            accounts.set_password(found.id, new)
        except ServiceError as error:
            raise click.ClickException(error.message) from error
        click.echo(t("cli.user.password_set", username=name))
        if found.disabled:
            click.echo(t("cli.user.still_disabled", username=name))

    return user
