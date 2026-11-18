"""Migración 3: agregar el campo fecha a la tabla tickets

Revision ID: 0003
Revises: 0002
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("tickets") as batch_op:
        batch_op.add_column(sa.Column("fecha", sa.Date(), nullable=True))


def downgrade():
    with op.batch_alter_table("tickets") as batch_op:
        batch_op.drop_column("fecha")
