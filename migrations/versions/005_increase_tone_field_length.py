"""increase tone field length

Revision ID: 005
Revises: 004
Create Date: 2025-01-11 09:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Zwiększa długość pola tone w tabeli general_styles z 100 do 500 znaków."""
    
    # Zwiększenie limitu pola tone dla obsługi długich opisów z Gemini API
    op.alter_column('general_styles', 'tone',
                    existing_type=sa.String(100),
                    type_=sa.String(500),
                    existing_nullable=False)
    
    print("✅ Zwiększono limit pola 'tone' w tabeli 'general_styles' z 100 do 500 znaków")


def downgrade() -> None:
    """Przywraca limit pola tone z 500 do 100 znaków."""
    
    # UWAGA: Operacja może się nie powieść jeśli istnieją rekordy z tonem > 100 znaków
    op.alter_column('general_styles', 'tone',
                    existing_type=sa.String(500),
                    type_=sa.String(100),
                    existing_nullable=False)
    
    print("⚠️ Przywrócono limit pola 'tone' w tabeli 'general_styles' z 500 do 100 znaków") 