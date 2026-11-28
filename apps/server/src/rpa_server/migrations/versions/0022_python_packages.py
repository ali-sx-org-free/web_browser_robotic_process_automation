"""RPA Python 運行環境的套件由伺服器管理（ADR 0027）：python_package_sets，以及執行、批次與
組合運行固定的套件版本（runs.python_packages、batches.python_packages、
workflow_runs.python_packages）

「套件 #1」（和內附的運行環境相同）在升級後第一次用到時由程式內附的鎖定檔建立
（rpa_server.pypackages.PackageService.ensure_defaults）。

Revision ID: 0022
Revises: 0021
Create Date: 2026-11-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from rpa_server.db import JsonType, UtcDateTime

revision: str = "0022"
down_revision: str | None = "0021"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "python_package_sets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("runtime", sa.String(10), nullable=False),
        sa.Column("number", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("requirements", JsonType, nullable=False),
        sa.Column("lock", sa.Text(), nullable=True),
        sa.Column("lock_hash", sa.String(64), nullable=True),
        sa.Column("manifests", JsonType, nullable=True),
        sa.Column("check", JsonType, nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("base_number", sa.Integer(), nullable=True),
        sa.Column("restored_from", sa.Integer(), nullable=True),
        sa.Column("created_by", sa.String(64), nullable=True),
        sa.Column("created_at", UtcDateTime(), nullable=False),
        sa.Column("updated_at", UtcDateTime(), nullable=False),
        sa.Column("published_by", sa.String(64), nullable=True),
        sa.Column("published_at", UtcDateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_python_package_sets"),
        sa.UniqueConstraint("runtime", "number", name="uq_python_package_sets_runtime"),
    )
    op.create_index("ix_python_package_sets_runtime", "python_package_sets", ["runtime"])
    op.create_index("ix_python_package_sets_status", "python_package_sets", ["status"])
    for table in ("runs", "batches", "workflow_runs"):
        with op.batch_alter_table(table) as batch:
            batch.add_column(sa.Column("python_packages", sa.Integer(), nullable=True))


def downgrade() -> None:
    for table in ("workflow_runs", "batches", "runs"):
        with op.batch_alter_table(table) as batch:
            batch.drop_column("python_packages")
    op.drop_index("ix_python_package_sets_status", table_name="python_package_sets")
    op.drop_index("ix_python_package_sets_runtime", table_name="python_package_sets")
    op.drop_table("python_package_sets")
