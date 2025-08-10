"""configure_gemini_api

Revision ID: 004
Revises: 003
Create Date: 2025-01-11 08:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    """Update AI model assignment to use Gemini API and add environment variable support"""
    
    # Update model assignment to use official Gemini API
    now = datetime.utcnow()
    
    # Update model assignment for strategy_parser to use Gemini 1.5 Pro
    sql_update_model = f"""
    UPDATE ai_model_assignments 
    SET model_name = 'gemini-1.5-pro-latest',
        updated_at = '{now}'
    WHERE task_name = 'strategy_parser'
    """
    
    op.execute(sql_update_model)
    
    # Optional: Add a new task assignment for the new Gemini API configuration
    sql_insert_backup = f"""
    INSERT INTO ai_model_assignments (task_name, model_name, created_at, updated_at)
    VALUES ('strategy_parser_gemini', 'gemini-1.5-pro-latest', '{now}', '{now}')
    ON CONFLICT (task_name) DO UPDATE SET
        model_name = EXCLUDED.model_name,
        updated_at = EXCLUDED.updated_at
    """
    
    op.execute(sql_insert_backup)


def downgrade():
    """Revert to previous model configuration"""
    
    now = datetime.utcnow()
    
    # Revert model assignment for strategy_parser to previous version
    sql_revert_model = f"""
    UPDATE ai_model_assignments 
    SET model_name = 'gemini-1.5-pro-latest',
        updated_at = '{now}'
    WHERE task_name = 'strategy_parser'
    """
    
    op.execute(sql_revert_model)
    
    # Remove the backup task assignment
    sql_remove_backup = """
    DELETE FROM ai_model_assignments 
    WHERE task_name = 'strategy_parser_gemini'
    """
    
    op.execute(sql_remove_backup) 