#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Gemini API functionality
"""

import os
import sys
import json
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_gemini_api():
    """Test Gemini API with various scenarios"""
    
    print("=" * 60)
    print("GEMINI API TEST")
    print("=" * 60)
    
    # Check environment variable
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key:
        print("[X] ERROR: GOOGLE_AI_API_KEY not found in environment variables")
        return False
    
    print(f"[OK] API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Configure API
    try:
        genai.configure(api_key=api_key)
        print("[OK] API configured successfully")
    except Exception as e:
        print(f"[X] Failed to configure API: {e}")
        return False
    
    # Test 1: Simple text generation
    print("\n--- Test 1: Simple text generation ---")
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello, please respond with 'API is working'")
        if response and response.text:
            print(f"[OK] Response: {response.text.strip()}")
        else:
            print("[X] Empty response")
    except Exception as e:
        print(f"[X] Error: {e}")
    
    # Test 2: JSON generation
    print("\n--- Test 2: JSON generation ---")
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = """Return a JSON object with the following structure:
        {
            "status": "success",
            "timestamp": "current time",
            "message": "Gemini API test successful"
        }
        Return ONLY the JSON object."""
        
        response = model.generate_content(prompt)
        if response and response.text:
            print(f"Raw response: {response.text.strip()}")
            try:
                # Try to parse as JSON
                json_data = json.loads(response.text.strip())
                print(f"[OK] Parsed JSON: {json_data}")
            except json.JSONDecodeError:
                print("[!] Response is not valid JSON, might be wrapped in markdown")
                # Try to extract JSON from markdown
                text = response.text.strip()
                if "```json" in text:
                    start = text.find("```json") + 7
                    end = text.find("```", start)
                    if end > start:
                        json_text = text[start:end].strip()
                        try:
                            json_data = json.loads(json_text)
                            print(f"[OK] Extracted and parsed JSON: {json_data}")
                        except:
                            print("[X] Failed to parse extracted JSON")
        else:
            print("[X] Empty response")
    except Exception as e:
        print(f"[X] Error: {e}")
    
    # Test 3: Model availability
    print("\n--- Test 3: Model availability ---")
    models_to_test = [
        'gemini-pro',
        'gemini-1.5-pro-latest',
        'gemini-1.5-flash',
        'models/gemini-1.5-pro-latest'
    ]
    
    for model_name in models_to_test:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say 'yes' if you work")
            if response and response.text:
                print(f"[OK] {model_name}: Working")
            else:
                print(f"[X] {model_name}: Empty response")
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower():
                print(f"[!] {model_name}: QUOTA EXCEEDED")
            elif "not found" in error_msg.lower():
                print(f"[X] {model_name}: Model not found")
            else:
                print(f"[X] {model_name}: {error_msg[:100]}...")
    
    # Test 4: Check available models
    print("\n--- Test 4: List available models ---")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"[OK] Available: {m.name}")
    except Exception as e:
        print(f"[X] Error listing models: {e}")
    
    # Test 5: Test flash model with content generation
    print("\n--- Test 5: Test gemini-1.5-flash for content generation ---")
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        # Test blog topic generation
        prompt = """Generate 3 blog topics about artificial intelligence.
        Return as JSON array:
        [
            {"title": "topic 1", "description": "description 1"},
            {"title": "topic 2", "description": "description 2"},
            {"title": "topic 3", "description": "description 3"}
        ]
        Return ONLY the JSON array."""
        
        response = model.generate_content(prompt)
        if response and response.text:
            print(f"Raw response length: {len(response.text)} characters")
            print(f"Response preview: {response.text[:200]}...")
            
            # Try to parse JSON
            try:
                text = response.text.strip()
                if "```json" in text:
                    start = text.find("```json") + 7
                    end = text.find("```", start)
                    if end > start:
                        text = text[start:end].strip()
                
                topics = json.loads(text)
                print(f"[OK] Successfully parsed {len(topics)} topics")
                for i, topic in enumerate(topics):
                    print(f"  Topic {i+1}: {topic.get('title', 'No title')}")
            except json.JSONDecodeError:
                print("[!] Response is not valid JSON")
        else:
            print("[X] Empty response")
    except Exception as e:
        if "quota" in str(e).lower():
            print("[!] QUOTA EXCEEDED for gemini-1.5-flash")
        else:
            print(f"[X] Error: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_gemini_api()