"""登入角色與 Secrets 的使用權限（M8.1，ADR 0026）：credential_grants，以及批次與組合運行
記下開始的帳號（batches.user_id、workflow_runs.user_id）

既有的 API 用戶端在升級後第一次啟動時自動綁定（rpa_server.grants.Grants.seed_clients）；
帳號不自動綁定，由系統管理員或領域管理員指定。

Revision ID: 0021
Revises: 0020
Create Date: 2026-11-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from rpa_server.db import UtcDateTime

revision: str = "0021"
down_revision: str | None = "0020"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "credential_grants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(10), nullable=False),
        sa.Column("target", sa.String(200), nullable=False),
        sa.Column("principal", sa.String(80), nullable=False),
        sa.Column("granted_at", UtcDateTime(), nullable=False),
        sa.Column("granted_by", sa.String(64), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_credential_grants"),
        sa.UniqueConstraint("kind", "target", "principal", name="uq_credential_grants_kind"),
    )
    op.create_index("ix_credential_grants_principal", "credential_grants", ["principal"])
    with op.batch_alter_table("batches") as batch:
        batch.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
        batch.create_index("ix_batches_user_id", ["user_id"])
    with op.batch_alter_table("workflow_runs") as batch:
        batch.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
        batch.create_index("ix_workflow_runs_user_id", ["user_id"])


def downgrade() -> None:
    with op.batch_alter_table("workflow_runs") as batch:
        batch.drop_index("ix_workflow_runs_user_id")
        batch.drop_column("user_id")
    with op.batch_alter_table("batches") as batch:
        batch.drop_index("ix_batches_user_id")
        batch.drop_column("user_id")
    op.drop_index("ix_credential_grants_principal", table_name="credential_grants")
    op.drop_table("credential_grants")
