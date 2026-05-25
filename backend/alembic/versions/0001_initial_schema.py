"""Initial schema – alle Tabellen des SmartKitchen-Projekts

Revision ID: 0001
Revises: -
Create Date: 2026-05-25

Enthält: users, recipes, recipe_ingredients, recipe_steps,
         recipe_ratings, tags, recipe_tags, groups, group_recipes
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. users
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("username", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_email", "users", ["email"])

    # ------------------------------------------------------------------
    # 2. recipes
    # ------------------------------------------------------------------
    op.create_table(
        "recipes",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("prep_time_minutes", sa.Integer(), nullable=True),
        sa.Column("servings", sa.Integer(), nullable=True),
        sa.Column("difficulty", sa.String(50), nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=True, server_default=sa.false()),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_recipes_id", "recipes", ["id"])

    # ------------------------------------------------------------------
    # 3. recipe_ingredients
    # ------------------------------------------------------------------
    op.create_table(
        "recipe_ingredients",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column(
            "recipe_id", sa.BigInteger(), sa.ForeignKey("recipes.id"), nullable=True
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("amount", sa.Float(), nullable=True),
        sa.Column("unit", sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # ------------------------------------------------------------------
    # 4. recipe_steps
    # ------------------------------------------------------------------
    op.create_table(
        "recipe_steps",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column(
            "recipe_id", sa.BigInteger(), sa.ForeignKey("recipes.id"), nullable=True
        ),
        sa.Column("step_number", sa.Integer(), nullable=True),
        sa.Column("instruction", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # ------------------------------------------------------------------
    # 5. recipe_ratings
    # ------------------------------------------------------------------
    op.create_table(
        "recipe_ratings",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column(
            "recipe_id", sa.BigInteger(), sa.ForeignKey("recipes.id"), nullable=True
        ),
        sa.Column(
            "user_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=True
        ),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # ------------------------------------------------------------------
    # 6. tags
    # ------------------------------------------------------------------
    op.create_table(
        "tags",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_tags_id", "tags", ["id"])

    # ------------------------------------------------------------------
    # 6b. recipe_tags  (M:N Verknüpfung)
    # ------------------------------------------------------------------
    op.create_table(
        "recipe_tags",
        sa.Column("recipe_id", sa.BigInteger(), sa.ForeignKey("recipes.id"), nullable=False),
        sa.Column("tag_id", sa.BigInteger(), sa.ForeignKey("tags.id"), nullable=False),
        sa.PrimaryKeyConstraint("recipe_id", "tag_id"),
    )

    # ------------------------------------------------------------------
    # 7. groups
    # ------------------------------------------------------------------
    op.create_table(
        "groups",
        sa.Column("id", sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "owner_id", sa.BigInteger(), sa.ForeignKey("users.id"), nullable=True
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_groups_id", "groups", ["id"])

    # ------------------------------------------------------------------
    # 7b. group_recipes  (M:N Verknüpfung)
    # ------------------------------------------------------------------
    op.create_table(
        "group_recipes",
        sa.Column("group_id", sa.BigInteger(), sa.ForeignKey("groups.id"), nullable=False),
        sa.Column("recipe_id", sa.BigInteger(), sa.ForeignKey("recipes.id"), nullable=False),
        sa.PrimaryKeyConstraint("group_id", "recipe_id"),
    )


def downgrade() -> None:
    op.drop_table("group_recipes")
    op.drop_table("groups")
    op.drop_table("recipe_tags")
    op.drop_table("tags")
    op.drop_table("recipe_ratings")
    op.drop_table("recipe_steps")
    op.drop_table("recipe_ingredients")
    op.drop_table("recipes")
    op.drop_table("users")
