"""
Test Tavily integration in content generation flow
"""

import asyncio
import sys
import json
from app.tasks.main_flow import _enhance_context_with_research

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_research_enhancement():
    """Test the research enhancement function"""
    
    # Create a sample super context
    super_context = {
        "organization": {
            "name": "Akson Elektro",
            "description": "Firma instalacyjna specjalizująca się w elektryce i automatyce",
            "industry": "elektryka i automatyka",
            "website": "https://akson.pl"
        },
        "brief_insights": {
            "mandatory_topics": [
                "inteligentne instalacje elektryczne",
                "automatyka budynkowa",
                "oszczędność energii"
            ],
            "key_topics": [
                "smart home",
                "fotowoltaika",
                "ładowarki do samochodów elektrycznych"
            ]
        }
    }
    
    print("=" * 60)
    print("TESTING RESEARCH ENHANCEMENT IN CONTENT FLOW")
    print("=" * 60)
    
    print("\nOriginal context:")
    print(json.dumps(super_context, indent=2, ensure_ascii=False))
    
    print("\nEnhancing context with Tavily research...")
    
    # Run the enhancement
    enhanced_context = _enhance_context_with_research(super_context)
    
    print("\nEnhanced context includes:")
    
    # Check if research was added
    if "research_data" in enhanced_context:
        print("✅ Research data added successfully!")
        
        research_data = enhanced_context["research_data"]
        print(f"\nResearched topics:")
        for topic, data in research_data.items():
            if isinstance(data, dict):
                sources = data.get("sources", {})
                synthesis = data.get("synthesis", {})
                
                print(f"\n📌 {topic}:")
                print(f"   - Web search: {'✓' if sources.get('web_search') and 'error' not in sources['web_search'] else '✗'}")
                print(f"   - Recent news: {'✓' if sources.get('recent_news') and 'error' not in sources['recent_news'] else '✗'}")
                print(f"   - Competitor insights: {'✓' if sources.get('competitor_insights') else '✗'}")
                
                if synthesis:
                    print(f"   - Key findings: {len(synthesis.get('key_findings', []))}")
                    print(f"   - Content opportunities: {len(synthesis.get('content_opportunities', []))}")
    else:
        print("❌ No research data found in enhanced context")
    
    # Check AI insights
    if "ai_research_insights" in enhanced_context:
        insights = enhanced_context["ai_research_insights"]
        print(f"\n✅ AI research insights: {len(insights)} insights extracted")
        print("\nTop 3 insights:")
        for i, insight in enumerate(insights[:3], 1):
            print(f"   {i}. {insight}")
    else:
        print("\n❌ No AI research insights found")
    
    return enhanced_context

if __name__ == "__main__":
    result = test_research_enhancement()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)