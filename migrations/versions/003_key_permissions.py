"""Create key_permissions table for granular identity-to-key authorization.

Revision ID: 003_key_permissions
Revises: 002_gateway_and_vault
Create Date: 2026-11-23 04:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003_key_permissions"
down_revision: str | None = "002_gateway_and_vault"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "key_permissions",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("project_id", sa.String(length=26), nullable=False),
        sa.Column("identity_id", sa.String(length=100), nullable=False),
        sa.Column(
            "identity_type",
            sa.String(length=20),
            server_default="client",
            nullable=False,
        ),
        sa.Column("secret_key", sa.String(length=100), nullable=False),
        sa.Column(
            "granted_by", sa.String(length=100), server_default="", nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name="key_permissions_project_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="key_permissions_pkey"),
        sa.UniqueConstraint(
            "project_id", "identity_id", "secret_key", name="uq_project_identity_key"
        ),
    )
    op.create_index(
        "ix_key_permissions_lookup",
        "key_permissions",
        ["project_id", "identity_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_key_permissions_lookup", table_name="key_permissions")
    op.drop_table("key_permissions")
