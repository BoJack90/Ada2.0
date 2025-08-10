#!/usr/bin/env python3
"""Test brief extraction and analysis directly"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tasks.content_generation import _extract_text_from_file
import base64

# Read the example brief
brief_path = "/app/knx/Akson Brief sierpien.pdf"

with open(brief_path, 'rb') as f:
    content_b64 = base64.b64encode(f.read()).decode('utf-8')

# Extract text
text = _extract_text_from_file(content_b64, "application/pdf")

if text:
    print(f"Extracted text length: {len(text)}")
    print("\n=== FIRST 2000 CHARACTERS ===")
    print(text[:2000])
    print("\n=== CHECKING FOR KEY WORDS ===")
    print(f"Contains 'monitoring': {'monitoring' in text.lower()}")
    print(f"Contains 'CFD': {'CFD' in text}")
    print(f"Contains 'SMART': {'SMART' in text}")
    print(f"Contains 'sztuczna inteligencja': {'sztuczna inteligencja' in text.lower()}")
    print(f"Contains 'AI': {'AI' in text}")
    print(f"Contains 'machine learning': {'machine learning' in text.lower()}")
else:
    print("Failed to extract text")