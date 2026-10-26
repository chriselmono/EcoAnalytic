"""Add household features to consumption records.

Revision ID: 5d8a4c1f2b90
Revises: 1bc9f212bf81
Create Date: 2026-10-25
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5d8a4c1f2b90"
down_revision = "1bc9f212bf81"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("consumo", sa.Column("estrato", sa.Integer(), nullable=True))
    op.add_column(
        "consumo",
        sa.Column("personas_vivienda", sa.Integer(), nullable=True),
    )


def downgrade():
    op.drop_column("consumo", "personas_vivienda")
    op.drop_column("consumo", "estrato")
