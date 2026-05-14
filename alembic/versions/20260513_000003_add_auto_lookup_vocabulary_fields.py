"""add auto lookup vocabulary fields

Revision ID: 20260513_000003
Revises: 20260506_000002
Create Date: 2026-05-13 15:20:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260513_000003"
down_revision = "20260506_000002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user_vocabulary_items", sa.Column("text", sa.String(length=100), nullable=True))
    op.add_column("user_vocabulary_items", sa.Column("normalized_text", sa.String(length=100), nullable=True))
    op.add_column(
        "user_vocabulary_items",
        sa.Column("lookup_status", sa.String(length=20), server_default="failed", nullable=False),
    )
    op.alter_column("user_vocabulary_items", "dictionary_entry_id", existing_type=sa.UUID(), nullable=True)
    op.execute(
        """
        UPDATE user_vocabulary_items AS uvi
        SET text = COALESCE(uvi.selected_text, de.display_word),
            normalized_text = de.normalized_word
        FROM dictionary_entries AS de
        WHERE uvi.dictionary_entry_id = de.id
        """
    )
    op.execute("UPDATE user_vocabulary_items SET text = selected_text WHERE text IS NULL")
    op.execute("UPDATE user_vocabulary_items SET normalized_text = lower(trim(text)) WHERE normalized_text IS NULL")
    op.alter_column("user_vocabulary_items", "text", existing_type=sa.String(length=100), nullable=False)
    op.alter_column("user_vocabulary_items", "normalized_text", existing_type=sa.String(length=100), nullable=False)
    op.create_index("ix_user_vocabulary_items_normalized_text", "user_vocabulary_items", ["normalized_text"], unique=False)
    op.drop_constraint("uq_user_vocab_user_entry", "user_vocabulary_items", type_="unique")
    op.create_unique_constraint(
        "uq_user_vocab_user_normalized_text", "user_vocabulary_items", ["user_id", "normalized_text"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_user_vocab_user_normalized_text", "user_vocabulary_items", type_="unique")
    op.create_unique_constraint("uq_user_vocab_user_entry", "user_vocabulary_items", ["user_id", "dictionary_entry_id"])
    op.drop_index("ix_user_vocabulary_items_normalized_text", table_name="user_vocabulary_items")
    op.alter_column("user_vocabulary_items", "dictionary_entry_id", existing_type=sa.UUID(), nullable=False)
    op.drop_column("user_vocabulary_items", "lookup_status")
    op.drop_column("user_vocabulary_items", "normalized_text")
    op.drop_column("user_vocabulary_items", "text")
