"""
Migration 003: Add recording_path and audio_path columns to meetings table.
These store the file paths for audio/video captured by the bot-worker container.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('meetings', sa.Column('recording_path', sa.String(), nullable=True))
    op.add_column('meetings', sa.Column('audio_path', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('meetings', 'audio_path')
    op.drop_column('meetings', 'recording_path')
