import os
import sys
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import io

# Set stdout to handle UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Database URL from .env
DATABASE_URL = "postgresql://ada_user:ada_password@localhost:5432/ada_db"

# Create engine
engine = create_engine(DATABASE_URL)

# Query the content_briefs table
with engine.connect() as connection:
    result = connection.execute(text("""
        SELECT id, title, extracted_content, ai_analysis 
        FROM content_briefs
    """))
    
    for row in result:
        print(f"\n{'='*80}")
        print(f"ID: {row.id}")
        print(f"Title: {row.title}")
        print(f"\nExtracted Content:")
        print("-" * 40)
        if row.extracted_content:
            print(row.extracted_content[:1000] + "..." if len(row.extracted_content) > 1000 else row.extracted_content)
        else:
            print("No extracted content")
        
        print(f"\nAI Analysis:")
        print("-" * 40)
        if row.ai_analysis:
            try:
                analysis = json.loads(row.ai_analysis) if isinstance(row.ai_analysis, str) else row.ai_analysis
                print(json.dumps(analysis, indent=2))
            except:
                print(row.ai_analysis)
        else:
            print("No AI analysis")