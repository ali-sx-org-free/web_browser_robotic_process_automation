"""多用戶與治理（M8，ADR 0025）：帳號 users、登入工作階段 login_sessions、領域成員
domain_members、稽核紀錄 audit_events

既有資料不受影響；升級後第一次打開管理 Portal 時，在伺服器那台電腦上建立第一個系統管理員。

Revision ID: 0020
Revises: 0019
Create Date: 2026-11-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from rpa_server.db import UtcDateTime

revision: str = "0020"
down_revision: str | None = "0019"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(64), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column("provider", sa.String(20), server_default="local", nullable=False),
        sa.Column("subject", sa.String(255), nullable=True),
        sa.Column("system_admin", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("disabled", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("created_at", UtcDateTime(), nullable=False),
        sa.Column("password_changed_at", UtcDateTime(), nullable=True),
        sa.Column("last_login_at", UtcDateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )
    op.create_table(
        "login_sessions",
        sa.Column("id", sa.String(64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", UtcDateTime(), nullable=False),
        sa.Column("last_seen_at", UtcDateTime(), nullable=False),
        sa.Column("expires_at", UtcDateTime(), nullable=False),
        sa.Column("ip", sa.String(64), nullable=True),
        sa.Column("user_agent", sa.String(255), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_login_sessions_user_id_users"),
        sa.PrimaryKeyConstraint("id", name="pk_login_sessions"),
    )
    op.create_index("ix_login_sessions_user_id", "login_sessions", ["user_id"])
    op.create_index("ix_login_sessions_expires_at", "login_sessions", ["expires_at"])
    op.create_table(
        "domain_members",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("domain_id", sa.String(64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(10), nullable=False),
        sa.Column("created_at", UtcDateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["domain_id"], ["domains.id"], name="fk_domain_members_domain_id_domains"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_domain_members_user_id_users"),
        sa.PrimaryKeyConstraint("id", name="pk_domain_members"),
        sa.UniqueConstraint("domain_id", "user_id", name="uq_domain_members_domain_id"),
    )
    op.create_index("ix_domain_members_domain_id", "domain_members", ["domain_id"])
    op.create_index("ix_domain_members_user_id", "domain_members", ["user_id"])
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("at", UtcDateTime(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("username", sa.String(64), nullable=True),
        sa.Column("action", sa.String(40), nullable=False),
        sa.Column("target", sa.String(500), nullable=True),
        sa.Column("status", sa.Integer(), nullable=True),
        sa.Column("ip", sa.String(64), nullable=True),
        sa.Column("via", sa.String(64), nullable=True),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("prev_hash", sa.String(64), nullable=False),
        sa.Column("hash", sa.String(64), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_audit_events"),
    )
    op.create_index("ix_audit_events_at", "audit_events", ["at"])
    op.create_index("ix_audit_events_user_id", "audit_events", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_audit_events_user_id", table_name="audit_events")
    op.drop_index("ix_audit_events_at", table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_index("ix_domain_members_user_id", table_name="domain_members")
    op.drop_index("ix_domain_members_domain_id", table_name="domain_members")
    op.drop_table("domain_members")
    op.drop_index("ix_login_sessions_expires_at", table_name="login_sessions")
    op.drop_index("ix_login_sessions_user_id", table_name="login_sessions")
    op.drop_table("login_sessions")
    op.drop_table("users")
