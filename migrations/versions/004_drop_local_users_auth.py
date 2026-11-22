"""Drop local password authentication column and enforce SSO-only identity.

Revision ID: 004_drop_local_users_auth
Revises: 003_key_permissions
Create Date: 2026-11-23 04:45:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004_drop_local_users_auth"
down_revision: str | None = "003_key_permissions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Remove password storage completely from local database
    op.drop_column("users", "password_hash")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column("password_hash", sa.String(length=255), nullable=True),
    )
