"""組合場景的批次（M7 收尾）：batches.workflow_id（這時 scene_id 是 NULL）；組合運行記下批次、
第幾列與表格給節點的入參 workflow_runs.batch_id、batch_row、inputs

既有資料不受影響：之前的批次都是場景的批次，之前的組合運行不屬於批次。

Revision ID: 0019
Revises: 0018
Create Date: 2026-11-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from rpa_server.db import JsonType

revision: str = "0019"
down_revision: str | None = "0018"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("batches") as batch:
        batch.alter_column("scene_id", existing_type=sa.String(64), nullable=True)
        batch.add_column(sa.Column("workflow_id", sa.Integer(), nullable=True))
        batch.create_index("ix_batches_workflow_id", ["workflow_id"])
    with op.batch_alter_table("workflow_runs") as batch:
        batch.add_column(sa.Column("batch_id", sa.String(120), nullable=True))
        batch.add_column(sa.Column("batch_row", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("inputs", JsonType, nullable=True))
        batch.create_index("ix_workflow_runs_batch_id", ["batch_id"])
        batch.create_foreign_key(
            "fk_workflow_runs_batch_id_batches", "batches", ["batch_id"], ["id"]
        )


def downgrade() -> None:
    with op.batch_alter_table("workflow_runs") as batch:
        batch.drop_constraint("fk_workflow_runs_batch_id_batches", type_="foreignkey")
        batch.drop_index("ix_workflow_runs_batch_id")
        batch.drop_column("inputs")
        batch.drop_column("batch_row")
        batch.drop_column("batch_id")
    with op.batch_alter_table("batches") as batch:
        batch.drop_index("ix_batches_workflow_id")
        batch.drop_column("workflow_id")
        batch.alter_column("scene_id", existing_type=sa.String(64), nullable=False)
