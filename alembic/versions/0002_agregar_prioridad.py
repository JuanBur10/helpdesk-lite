"""Migración 2: agregar el campo prioridad a la tabla tickets

Valores: bajo, medio, alto. Por defecto: medio.

Revision ID: 0002
Revises: 0001
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    # batch_alter_table se usa porque SQLite no deja alterar tablas directamente
    with op.batch_alter_table("tickets") as batch_op:
        batch_op.add_column(sa.Column("prioridad", sa.String(), server_default="medio"))


def downgrade():
    with op.batch_alter_table("tickets") as batch_op:
        batch_op.drop_column("prioridad")
