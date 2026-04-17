"""initial schema

Revision ID: 20260416_000001
Revises:
Create Date: 2026-04-16 15:40:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260416_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "user_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("english_level", sa.String(length=20), nullable=True),
        sa.Column("learning_goal", sa.String(length=255), nullable=True),
        sa.Column("preferred_explanation_language", sa.String(length=20), nullable=False),
        sa.Column("teacher_style", sa.String(length=100), nullable=True),
        sa.Column("daily_target", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    op.create_table(
        "dictionary_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lemma", sa.String(length=100), nullable=False),
        sa.Column("normalized_word", sa.String(length=100), nullable=False),
        sa.Column("display_word", sa.String(length=100), nullable=False),
        sa.Column("phonetic", sa.String(length=120), nullable=True),
        sa.Column("audio_url", sa.Text(), nullable=True),
        sa.Column("cefr_level", sa.String(length=10), nullable=True),
        sa.Column("frequency_rank", sa.Integer(), nullable=True),
        sa.Column("source_provider", sa.String(length=50), nullable=False),
        sa.Column("raw_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("cached_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_dictionary_entries_lemma", "dictionary_entries", ["lemma"], unique=False)
    op.create_index("ix_dictionary_entries_normalized_word", "dictionary_entries", ["normalized_word"], unique=False)
    op.create_index("ix_dictionary_entries_lemma_source_provider", "dictionary_entries", ["lemma", "source_provider"], unique=False)

    op.create_table(
        "dictionary_senses",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entry_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("part_of_speech", sa.String(length=50), nullable=False),
        sa.Column("definition_en", sa.Text(), nullable=True),
        sa.Column("definition_zh", sa.Text(), nullable=True),
        sa.Column("short_definition", sa.Text(), nullable=True),
        sa.Column("sense_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["entry_id"], ["dictionary_entries.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_dictionary_senses_entry_id", "dictionary_senses", ["entry_id"], unique=False)
    op.create_index("ix_dictionary_senses_part_of_speech", "dictionary_senses", ["part_of_speech"], unique=False)

    op.create_table(
        "dictionary_examples",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entry_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sense_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("sentence_en", sa.Text(), nullable=False),
        sa.Column("sentence_zh", sa.Text(), nullable=True),
        sa.Column("example_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["entry_id"], ["dictionary_entries.id"]),
        sa.ForeignKeyConstraint(["sense_id"], ["dictionary_senses.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_dictionary_examples_entry_id", "dictionary_examples", ["entry_id"], unique=False)
    op.create_index("ix_dictionary_examples_sense_id", "dictionary_examples", ["sense_id"], unique=False)

    op.create_table(
        "dictionary_collocations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entry_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("phrase", sa.String(length=255), nullable=False),
        sa.Column("translation_zh", sa.Text(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("collocation_type", sa.String(length=50), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["entry_id"], ["dictionary_entries.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_dictionary_collocations_entry_id", "dictionary_collocations", ["entry_id"], unique=False)
    op.create_index("ix_dictionary_collocations_phrase", "dictionary_collocations", ["phrase"], unique=False)

    op.create_table(
        "user_vocabulary_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dictionary_entry_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("selected_text", sa.String(length=100), nullable=True),
        sa.Column("source_sentence", sa.Text(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("source_title", sa.String(length=255), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("familiarity_score", sa.Integer(), nullable=True),
        sa.Column("first_added_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_review_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["dictionary_entry_id"], ["dictionary_entries.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "dictionary_entry_id", name="uq_user_vocab_user_entry"),
    )
    op.create_index("ix_user_vocabulary_items_status", "user_vocabulary_items", ["status"], unique=False)
    op.create_index("ix_user_vocabulary_items_user_id", "user_vocabulary_items", ["user_id"], unique=False)
    op.create_index("ix_user_vocabulary_items_user_id_next_review_at", "user_vocabulary_items", ["user_id", "next_review_at"], unique=False)

    op.create_table(
        "review_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vocabulary_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("result", sa.String(length=20), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("next_review_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["vocabulary_item_id"], ["user_vocabulary_items.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_review_records_user_id", "review_records", ["user_id"], unique=False)
    op.create_index("ix_review_records_user_id_reviewed_at", "review_records", ["user_id", "reviewed_at"], unique=False)
    op.create_index("ix_review_records_vocabulary_item_id", "review_records", ["vocabulary_item_id"], unique=False)

    op.create_table(
        "ai_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("session_type", sa.String(length=50), nullable=False),
        sa.Column("current_context", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_sessions_user_id", "ai_sessions", ["user_id"], unique=False)
    op.create_index("ix_ai_sessions_user_id_updated_at", "ai_sessions", ["user_id", "updated_at"], unique=False)

    op.create_table(
        "ai_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["ai_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_messages_session_id", "ai_messages", ["session_id"], unique=False)
    op.create_index("ix_ai_messages_session_id_created_at", "ai_messages", ["session_id", "created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ai_messages_session_id_created_at", table_name="ai_messages")
    op.drop_index("ix_ai_messages_session_id", table_name="ai_messages")
    op.drop_table("ai_messages")
    op.drop_index("ix_ai_sessions_user_id_updated_at", table_name="ai_sessions")
    op.drop_index("ix_ai_sessions_user_id", table_name="ai_sessions")
    op.drop_table("ai_sessions")
    op.drop_index("ix_review_records_vocabulary_item_id", table_name="review_records")
    op.drop_index("ix_review_records_user_id_reviewed_at", table_name="review_records")
    op.drop_index("ix_review_records_user_id", table_name="review_records")
    op.drop_table("review_records")
    op.drop_index("ix_user_vocabulary_items_user_id_next_review_at", table_name="user_vocabulary_items")
    op.drop_index("ix_user_vocabulary_items_user_id", table_name="user_vocabulary_items")
    op.drop_index("ix_user_vocabulary_items_status", table_name="user_vocabulary_items")
    op.drop_table("user_vocabulary_items")
    op.drop_index("ix_dictionary_collocations_phrase", table_name="dictionary_collocations")
    op.drop_index("ix_dictionary_collocations_entry_id", table_name="dictionary_collocations")
    op.drop_table("dictionary_collocations")
    op.drop_index("ix_dictionary_examples_sense_id", table_name="dictionary_examples")
    op.drop_index("ix_dictionary_examples_entry_id", table_name="dictionary_examples")
    op.drop_table("dictionary_examples")
    op.drop_index("ix_dictionary_senses_part_of_speech", table_name="dictionary_senses")
    op.drop_index("ix_dictionary_senses_entry_id", table_name="dictionary_senses")
    op.drop_table("dictionary_senses")
    op.drop_index("ix_dictionary_entries_lemma_source_provider", table_name="dictionary_entries")
    op.drop_index("ix_dictionary_entries_normalized_word", table_name="dictionary_entries")
    op.drop_index("ix_dictionary_entries_lemma", table_name="dictionary_entries")
    op.drop_table("dictionary_entries")
    op.drop_table("user_profiles")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
