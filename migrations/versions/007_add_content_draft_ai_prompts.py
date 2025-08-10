"""add_content_draft_ai_prompts

Revision ID: 007
Revises: 006
Create Date: 2025-01-12 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    # Insert seed data for content draft AI prompts
    now = datetime.utcnow()
    
    # Prompt 1: generate_initial_draft
    op.execute(
        """
        INSERT INTO ai_prompts (prompt_name, prompt_template, version, created_at, updated_at)
        VALUES ('generate_initial_draft', 
                'Jesteś ekspertem w tworzeniu treści marketingowych. Twoim zadaniem jest stworzenie wysokiej jakości wersji roboczej treści na podstawie kontekstu strategii komunikacji i szczegółów zaplanowanego postu.

KONTEKST ORGANIZACJI I STRATEGII:
{context_data}

SZCZEGÓŁY POSTU:
{post_details}

WYTYCZNE:
1. Tworzona treść musi być zgodna z tonem i stylem komunikacji organizacji
2. Uwzględnij preferowane zwroty i unikaj zakazanych fraz
3. Dostosuj długość i styl do platformy docelowej
4. Włącz odpowiednie call-to-action zgodnie z zasadami CTA
5. Treść powinna być angażująca i wartościowa dla grupy docelowej

PĘTLA AUTOR-RECENZENT:
Jako Autor: Stwórz pierwszą wersję treści
Jako Recenzent: Oceń jakość i zaproponuj ulepszenia
Jako Autor: Zaimplementuj ulepszenia i stwórz finalną wersję

Zwróć TYLKO finalną, dopracowaną treść bez dodatkowych komentarzy.',
                1, 
                %s, 
                %s)
        """,
        (now, now)
    )
    
    # Prompt 2: revise_draft_with_feedback
    op.execute(
        """
        INSERT INTO ai_prompts (prompt_name, prompt_template, version, created_at, updated_at)
        VALUES ('revise_draft_with_feedback', 
                'Jesteś ekspertem w poprawianiu treści marketingowych na podstawie feedbacku operatora. Otrzymałeś opinię na temat istniejącej wersji roboczej i musisz ją poprawić.

KONTEKST ORGANIZACJI I STRATEGII:
{context_data}

SZCZEGÓŁY POSTU:
{post_details}

POPRZEDNIA WERSJA TREŚCI:
{previous_content}

FEEDBACK OPERATORA:
{feedback_text}

DODATKOWY KONTEKST REWIZJI:
{revision_context}

WYTYCZNE POPRAWKI:
1. Dokładnie przeanalizuj feedback operatora i zrozum co należy poprawić
2. Zachowaj elementy poprzedniej wersji, które działały dobrze
3. Wprowadź konkretne zmiany sugerowane w feedbacku
4. Upewnij się, że poprawiona treść nadal jest zgodna ze strategią komunikacji
5. Wykorzystaj pętlę Autor-Recenzent do optymalizacji

PĘTLA AUTOR-RECENZENT:
Jako Autor: Zaimplementuj feedback i popraw treść
Jako Recenzent: Sprawdź czy feedback został właściwie uwzględniony
Jako Autor: Dopracuj finalną wersję

Zwróć TYLKO poprawioną, finalną treść bez dodatkowych komentarzy.',
                1, 
                %s, 
                %s)
        """,
        (now, now)
    )
    
    # Prompt 3: regenerate_draft_from_rejection
    op.execute(
        """
        INSERT INTO ai_prompts (prompt_name, prompt_template, version, created_at, updated_at)
        VALUES ('regenerate_draft_from_rejection', 
                'Jesteś ekspertem w tworzeniu treści marketingowych. Poprzednia wersja treści została odrzucona, a Twoim zadaniem jest stworzenie zupełnie nowej, alternatywnej wersji.

KONTEKST ORGANIZACJI I STRATEGII:
{context_data}

SZCZEGÓŁY POSTU:
{post_details}

ODRZUCONA WERSJA (do analizy błędów):
{rejected_content}

PRZYCZYNA ODRZUCENIA:
{rejection_reason}

DODATKOWY KONTEKST:
{revision_context}

WYTYCZNE REGENERACJI:
1. Przeanalizuj odrzuconą wersję i zidentyfikuj główne problemy
2. Stwórz zupełnie nowe podejście do tematu, unikając błędów poprzedniej wersji
3. Zastosuj inne kąty, przykłady lub strukturę narracji
4. Zachowaj zgodność ze strategią komunikacji organizacji
5. Wykorzystaj pętlę Autor-Recenzent do stworzenia wysokiej jakości treści

PĘTLA AUTOR-RECENZENT:
Jako Autor: Stwórz nową, odmienną wersję treści
Jako Recenzent: Oceń czy nowa wersja unika problemów poprzedniej
Jako Autor: Dopracuj i zoptymalizuj finalną wersję

Zwróć TYLKO nową, finalną treść bez dodatkowych komentarzy.',
                1, 
                %s, 
                %s)
        """,
        (now, now)
    )
    
    # Model assignments dla content draft tasks
    op.execute(
        """
        INSERT INTO ai_model_assignments (task_name, model_name, created_at, updated_at)
        VALUES ('generate_initial_draft', 'gemini-1.5-pro-latest', %s, %s)
        """,
        (now, now)
    )
    
    op.execute(
        """
        INSERT INTO ai_model_assignments (task_name, model_name, created_at, updated_at)
        VALUES ('revise_draft_with_feedback', 'gemini-1.5-pro-latest', %s, %s)
        """,
        (now, now)
    )
    
    op.execute(
        """
        INSERT INTO ai_model_assignments (task_name, model_name, created_at, updated_at)
        VALUES ('regenerate_draft_from_rejection', 'gemini-1.5-pro-latest', %s, %s)
        """,
        (now, now)
    )


def downgrade():
    # Remove model assignments
    op.execute("DELETE FROM ai_model_assignments WHERE task_name IN ('generate_initial_draft', 'revise_draft_with_feedback', 'regenerate_draft_from_rejection')")
    
    # Remove prompts
    op.execute("DELETE FROM ai_prompts WHERE prompt_name IN ('generate_initial_draft', 'revise_draft_with_feedback', 'regenerate_draft_from_rejection')") 