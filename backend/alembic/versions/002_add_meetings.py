"""Add meetings table

Revision ID: 002_add_meetings
Revises: 
Create Date: 2026-02-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_meetings'
down_revision = None  # Will be updated based on your existing migrations
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    op.execute("""
        CREATE TYPE platformtype AS ENUM (
            'google_meet', 
            'zoom', 
            'microsoft_teams', 
            'webex', 
            'jitsi', 
            'other'
        )
    """)
    
    op.execute("""
        CREATE TYPE meetingstatus AS ENUM (
            'scheduled', 
            'in_progress', 
            'completed', 
            'cancelled', 
            'failed'
        )
    """)
    
    # Create meetings table
    op.create_table(
        'meetings',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('platform', sa.Enum('GOOGLE_MEET', 'ZOOM', 'MICROSOFT_TEAMS', 'WEBEX', 'JITSI', 'OTHER', name='platformtype'), nullable=False),
        sa.Column('meeting_code', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('scheduled_time', sa.DateTime(), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('purpose', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'FAILED', name='meetingstatus'), nullable=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('join_attempted_at', sa.DateTime(), nullable=True),
        sa.Column('join_successful', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_meetings_url', 'meetings', ['url'], unique=False)
    op.create_index('ix_meetings_scheduled_time', 'meetings', ['scheduled_time'], unique=False)
    op.create_index('ix_meetings_user_id', 'meetings', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_meetings_user_id', table_name='meetings')
    op.drop_index('ix_meetings_scheduled_time', table_name='meetings')
    op.drop_index('ix_meetings_url', table_name='meetings')
    
    # Drop table
    op.drop_table('meetings')
    
    # Drop enum types
    op.execute('DROP TYPE meetingstatus')
    op.execute('DROP TYPE platformtype')
