"""Favoriten-Tabelle hinzufügen

M:N Verknüpfung User <-> Rezept zum Speichern persönlicher Favoriten.

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-26
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "recipe_favorites",
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recipe_id", sa.BigInteger(), sa.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("user_id", "recipe_id"),
    )


def downgrade() -> None:
    op.drop_table("recipe_favorites")
