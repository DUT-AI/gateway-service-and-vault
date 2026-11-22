"""create gateway and vault platform tables

Revision ID: 002_gateway_and_vault
Revises: 001_initial
Create Date: 2026-11-23 02:45:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002_gateway_and_vault"
down_revision: str | None = "001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. projects table
    op.create_table(
        "projects",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_projects_slug"), "projects", ["slug"], unique=True)

    # 2. upstream_services table
    op.create_table(
        "upstream_services",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("base_url", sa.String(length=255), nullable=False),
        sa.Column("auth_type", sa.String(length=30), nullable=False),
        sa.Column("encrypted_credential", sa.Text(), nullable=False),
        sa.Column("timeout_seconds", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_upstream_services_slug"), "upstream_services", ["slug"], unique=True
    )

    # 3. project_upstream_allowlist table
    op.create_table(
        "project_upstream_allowlist",
        sa.Column("project_id", sa.String(length=26), nullable=False),
        sa.Column("service_id", sa.String(length=26), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["service_id"], ["upstream_services.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("project_id", "service_id"),
    )

    # 4. registered_clients table
    op.create_table(
        "registered_clients",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("client_type", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("owner_id", sa.String(length=100), nullable=False),
        sa.Column("cert_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("cert_serial", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_revoked", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_registered_clients_owner_id"),
        "registered_clients",
        ["owner_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_registered_clients_cert_fingerprint"),
        "registered_clients",
        ["cert_fingerprint"],
        unique=True,
    )

    # 5. virtual_access_keys table
    op.create_table(
        "virtual_access_keys",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("key_hash", sa.String(length=64), nullable=False),
        sa.Column("key_prefix", sa.String(length=16), nullable=False),
        sa.Column("client_id", sa.String(length=26), nullable=False),
        sa.Column("project_id", sa.String(length=26), nullable=False),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="ACTIVE"
        ),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["client_id"], ["registered_clients.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_virtual_access_keys_key_hash"),
        "virtual_access_keys",
        ["key_hash"],
        unique=True,
    )
    op.create_index(
        "ix_virtual_keys_client_project",
        "virtual_access_keys",
        ["client_id", "project_id"],
        unique=False,
    )

    # 6. quota_policies table
    op.create_table(
        "quota_policies",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("project_id", sa.String(length=26), nullable=False),
        sa.Column("service_id", sa.String(length=26), nullable=False),
        sa.Column("client_id", sa.String(length=26), nullable=True),
        sa.Column("rate_limit_rpm", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("quota_daily", sa.Integer(), nullable=False, server_default="10000"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["service_id"], ["upstream_services.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["client_id"], ["registered_clients.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 7. audit_events table
    op.create_table(
        "audit_events",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("client_type", sa.String(length=20), nullable=False),
        sa.Column("actor_id", sa.String(length=100), nullable=False),
        sa.Column("project_id", sa.String(length=26), nullable=False),
        sa.Column("service_id", sa.String(length=26), nullable=True),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("decision", sa.String(length=10), nullable=False),
        sa.Column("client_ip", sa.String(length=45), nullable=True),
        sa.Column("error_code", sa.String(length=50), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_audit_events_timestamp"), "audit_events", ["timestamp"], unique=False
    )
    op.create_index(
        op.f("ix_audit_events_actor_id"), "audit_events", ["actor_id"], unique=False
    )
    op.create_index(
        op.f("ix_audit_events_project_id"), "audit_events", ["project_id"], unique=False
    )
    op.create_index(
        op.f("ix_audit_events_action"), "audit_events", ["action"], unique=False
    )

    # 8. secret_scopes table
    op.create_table(
        "secret_scopes",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("project_id", sa.String(length=26), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "name", name="uq_scope_project_name"),
    )

    # 9. secrets table
    op.create_table(
        "secrets",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("project_id", sa.String(length=26), nullable=False),
        sa.Column("scope_id", sa.String(length=26), nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("encrypted_value", sa.Text(), nullable=False),
        sa.Column("nonce", sa.String(length=32), nullable=False),
        sa.Column("auth_tag", sa.String(length=32), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "created_by", sa.String(length=100), nullable=False, server_default=""
        ),
        sa.Column(
            "updated_by", sa.String(length=100), nullable=False, server_default=""
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["scope_id"], ["secret_scopes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scope_id", "key", name="uq_secret_scope_key"),
    )

    # 10. secret_histories table
    op.create_table(
        "secret_histories",
        sa.Column("id", sa.String(length=26), nullable=False),
        sa.Column("secret_id", sa.String(length=26), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("encrypted_value", sa.Text(), nullable=False),
        sa.Column("nonce", sa.String(length=32), nullable=False),
        sa.Column("auth_tag", sa.String(length=32), nullable=False),
        sa.Column("modified_by", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["secret_id"], ["secrets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("secret_histories")
    op.drop_table("secrets")
    op.drop_table("secret_scopes")
    op.drop_table("audit_events")
    op.drop_table("quota_policies")
    op.drop_table("virtual_access_keys")
    op.drop_table("registered_clients")
    op.drop_table("project_upstream_allowlist")
    op.drop_table("upstream_services")
    op.drop_table("projects")
