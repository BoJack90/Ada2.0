"""add_brief_file_path_to_content_plans

Revision ID: 010
Revises: cb2c414e9741
Create Date: 2025-01-11 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '010'
down_revision = 'cb2c414e9741'
branch_labels = None
depends_on = None


def upgrade():
    """Add brief_file_path column to content_plans table"""
    op.add_column('content_plans', sa.Column('brief_file_path', sa.String(500), nullable=True))
    

def downgrade():
    """Remove brief_file_path column from content_plans table"""
    op.drop_column('content_plans', 'brief_file_path') 