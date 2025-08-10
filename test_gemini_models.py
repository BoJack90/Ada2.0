"""
Test available Gemini models
"""

import os
import sys
from dotenv import load_dotenv

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

try:
    import google.generativeai as genai
    
    # Configure API
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file!")
        sys.exit(1)
    
    genai.configure(api_key=api_key)
    
    print("=" * 60)
    print("TESTING GEMINI API MODELS")
    print("=" * 60)
    
    # List available models
    print("\n📋 Available models:")
    for model in genai.list_models():
        print(f"\n✅ {model.name}")
        print(f"   Display name: {model.display_name}")
        print(f"   Description: {model.description[:100]}..." if model.description else "   No description")
        print(f"   Supported methods: {', '.join(model.supported_generation_methods)}")
    
    # Test specific models
    test_models = [
        "gemini-1.5-pro-latest",
        "gemini-1.5-flash-latest", 
        "gemini-2.0-flash-exp",
        "gemini-2.0-pro",
        "models/gemini-2.0-flash-exp",
        "models/gemini-1.5-pro-latest"
    ]
    
    print("\n" + "=" * 60)
    print("TESTING SPECIFIC MODELS")
    print("=" * 60)
    
    for model_name in test_models:
        print(f"\n🔍 Testing: {model_name}")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say 'Hello, I'm working!' in one sentence.")
            if response and response.text:
                print(f"   ✅ Success: {response.text.strip()[:50]}...")
            else:
                print(f"   ❌ Empty response")
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}...")
    
except ImportError:
    print("❌ google-generativeai not installed!")
    print("Run: pip install google-generativeai")
except Exception as e:
    print(f"❌ Error: {e}")