#!/usr/bin/env python3
"""Check what's in the brief analysis"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import ContentBrief
import json

db = SessionLocal()

# Get the latest brief
brief = db.query(ContentBrief).order_by(ContentBrief.created_at.desc()).first()

if brief and brief.ai_analysis:
    print("=== ANALIZA BRIEFU ===")
    print(f"Brief ID: {brief.id}")
    print(f"Plan ID: {brief.content_plan_id}")
    
    analysis = brief.ai_analysis
    
    print("\n=== COMPANY NEWS (Aktualności firmowe) ===")
    company_news = analysis.get("company_news", [])
    for i, news in enumerate(company_news, 1):
        print(f"{i}. {news}")
    
    print("\n=== KEY TOPICS ===")
    key_topics = analysis.get("key_topics", [])
    for topic in key_topics:
        print(f"- {topic}")
    
    print("\n=== CONTENT INSTRUCTIONS ===")
    instructions = analysis.get("content_instructions", [])
    for instruction in instructions:
        print(f"- {instruction}")
    
    print("\n=== MANDATORY TOPICS ===")
    mandatory = analysis.get("mandatory_topics", [])
    for topic in mandatory:
        print(f"- {topic}")
        
    # Check if there's info about new employee
    print("\n=== SZUKANIE INFO O NOWYM PRACOWNIKU ===")
    full_text = json.dumps(analysis, ensure_ascii=False).lower()
    if "natalia" in full_text:
        print("✓ Znaleziono informacje o Natalii Szarach")
    if "manager" in full_text:
        print("✓ Znaleziono informacje o stanowisku Manager")
else:
    print("Brak briefu lub analizy")

db.close()