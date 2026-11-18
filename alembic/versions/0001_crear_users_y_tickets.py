"""Migración 1: crear tablas users y tickets (relación 1:N)

Un usuario puede tener muchos tickets.
tickets.owner_id es la llave foránea que apunta a users.id

Revision ID: 0001
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column("rol", sa.String(), server_default="empleado"),
        sa.Column("fecha", sa.String(), nullable=False),

    )
    op.create_table(
        "tickets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("titulo", sa.String(), nullable=False),
        sa.Column("descripcion", sa.String(), nullable=False),
        sa.Column("estado", sa.String(), server_default="abierto"),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("fecha", sa.String(), nullable=False),
    )


def downgrade():
    op.drop_table("tickets")
    op.drop_table("users")
