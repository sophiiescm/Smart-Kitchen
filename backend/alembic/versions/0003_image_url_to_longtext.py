"""Spalte image_url auf LONGTEXT erweitern

TEXT (64 KB) ist zu klein für Base64-encodierte Bilder. Wir wechseln zu
LONGTEXT (bis 4 GB), damit Rezeptbilder als Data-URL gespeichert werden können.

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-25
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "recipes",
        "image_url",
        existing_type=sa.Text(),
        type_=mysql.LONGTEXT(),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "recipes",
        "image_url",
        existing_type=mysql.LONGTEXT(),
        type_=sa.Text(),
        existing_nullable=True,
    )
