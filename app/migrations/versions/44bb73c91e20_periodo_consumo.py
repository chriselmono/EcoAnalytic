"""Add billing period to consumption records.

Revision ID: 44bb73c91e20
Revises: 5d8a4c1f2b90
Create Date: 2026-10-25
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "44bb73c91e20"
down_revision = "5d8a4c1f2b90"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("consumo", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("periodo_consumo", sa.Date(), nullable=True)
        )
        # The old model required mes. Keep legacy values in the database, but
        # allow new application code to stop writing that obsolete column.
        batch_op.alter_column(
            "mes",
            existing_type=sa.String(length=255),
            nullable=True,
        )


def downgrade():
    with op.batch_alter_table("consumo", schema=None) as batch_op:
        batch_op.drop_column("periodo_consumo")
