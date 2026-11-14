"""批次執行（M7.3，ADR 0024）：批次 batches、每一列 batch_rows；執行記下屬於哪個批次的第幾列

既有資料不受影響：之前的執行 batch_id、batch_row 是 NULL。

Revision ID: 0018
Revises: 0017
Create Date: 2026-11-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from rpa_server.db import JsonType, UtcDateTime

revision: str = "0018"
down_revision: str | None = "0017"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "batches",
        sa.Column("id", sa.String(120), nullable=False),
        sa.Column("scene_id", sa.String(64), nullable=False),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("scene_name", sa.String(200), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("columns", JsonType, nullable=False),
        sa.Column("mapping", JsonType, nullable=False),
        sa.Column("source", sa.String(255), nullable=True),
        sa.Column("on_failure", sa.String(10), nullable=False),
        sa.Column("concurrency", sa.Integer(), nullable=False),
        sa.Column("round_number", sa.Integer(), nullable=False),
        sa.Column("engine", sa.String(20), nullable=True),
        sa.Column("base_url", sa.String(2000), nullable=True),
        sa.Column("headless", sa.Boolean(), nullable=True),
        sa.Column("target", sa.String(10), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", UtcDateTime(), nullable=False),
        sa.Column("started_at", UtcDateTime(), nullable=True),
        sa.Column("finished_at", UtcDateTime(), nullable=True),
        sa.Column("client_id", sa.String(64), nullable=True),
        sa.Column("idempotency_key", sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(["scene_id"], ["scenes.id"], name="fk_batches_scene_id_scenes"),
        sa.PrimaryKeyConstraint("id", name="pk_batches"),
        sa.UniqueConstraint("idempotency_key", name="uq_batches_idempotency_key"),
    )
    op.create_index("ix_batches_scene_id", "batches", ["scene_id"])
    op.create_index("ix_batches_status", "batches", ["status"])
    op.create_index("ix_batches_created_at", "batches", ["created_at"])
    op.create_index("ix_batches_client_id", "batches", ["client_id"])
    op.create_table(
        "batch_rows",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("batch_id", sa.String(120), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("cells", JsonType, nullable=False),
        sa.Column("run_id", sa.String(120), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("round_number", sa.Integer(), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["batch_id"], ["batches.id"], name="fk_batch_rows_batch_id_batches"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_batch_rows"),
        sa.UniqueConstraint("batch_id", "number", name="uq_batch_rows_batch_id"),
    )
    with op.batch_alter_table("runs") as batch:
        batch.add_column(sa.Column("batch_id", sa.String(120), nullable=True))
        batch.add_column(sa.Column("batch_row", sa.Integer(), nullable=True))
        batch.create_index("ix_runs_batch_id", ["batch_id"])
        batch.create_foreign_key("fk_runs_batch_id_batches", "batches", ["batch_id"], ["id"])


def downgrade() -> None:
    with op.batch_alter_table("runs") as batch:
        batch.drop_constraint("fk_runs_batch_id_batches", type_="foreignkey")
        batch.drop_index("ix_runs_batch_id")
        batch.drop_column("batch_row")
        batch.drop_column("batch_id")
    op.drop_table("batch_rows")
    op.drop_index("ix_batches_client_id", table_name="batches")
    op.drop_index("ix_batches_created_at", table_name="batches")
    op.drop_index("ix_batches_status", table_name="batches")
    op.drop_index("ix_batches_scene_id", table_name="batches")
    op.drop_table("batches")
