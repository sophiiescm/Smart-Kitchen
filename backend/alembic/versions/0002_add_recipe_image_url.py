"""Add image_url column to recipes

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-25
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "recipes",
        sa.Column("image_url", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("recipes", "image_url")
