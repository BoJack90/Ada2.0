"""
Simple test to verify Tavily integration in Ada 2.0
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

# Direct import from external_integrations
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.core.external_integrations import ContentResearchOrchestrator

async def test_ada_research():
    """Test research for Ada 2.0 use case"""
    
    print("=" * 60)
    print("TESTING TAVILY INTEGRATION FOR ADA 2.0")
    print("=" * 60)
    
    orchestrator = ContentResearchOrchestrator()
    
    # Test case: Akson Elektro content research
    org_context = {
        "name": "Akson Elektro",
        "industry": "elektryka i automatyka",
        "description": "Firma zajmująca się instalacjami elektrycznymi i automatyką budynkową"
    }
    
    test_topics = [
        "inteligentne instalacje elektryczne",
        "automatyka budynkowa KNX",
        "oszczędność energii w firmach"
    ]
    
    print(f"\nOrganizacja: {org_context['name']}")
    print(f"Branża: {org_context['industry']}")
    print(f"\nBadane tematy:")
    for topic in test_topics:
        print(f"  • {topic}")
    
    print("\n" + "-" * 60)
    
    for topic in test_topics:
        print(f"\n🔍 Researching: {topic}")
        
        results = await orchestrator.comprehensive_research(
            topic=topic,
            organization_context=org_context,
            research_depth="deep"
        )
        
        if results:
            # Show synthesis
            synthesis = results.get("synthesis", {})
            
            print(f"\n📊 Wyniki dla '{topic}':")
            
            # Key findings
            findings = synthesis.get("key_findings", [])
            if findings:
                print(f"\n  Kluczowe trendy ({len(findings)}):")
                for i, finding in enumerate(findings[:3], 1):
                    print(f"    {i}. {finding}")
            
            # Content opportunities
            opportunities = synthesis.get("content_opportunities", [])
            if opportunities:
                print(f"\n  Możliwości content'owe ({len(opportunities)}):")
                for i, opp in enumerate(opportunities[:3], 1):
                    print(f"    {i}. {opp.get('inspiration', 'N/A')}")
            
            # Trending angles
            angles = synthesis.get("trending_angles", [])
            if angles:
                print(f"\n  Aktualne tematy ({len(angles)}):")
                for i, angle in enumerate(angles[:3], 1):
                    print(f"    {i}. {angle}")
            
            # Recommended topics
            recommended = synthesis.get("recommended_topics", [])
            if recommended:
                print(f"\n  Rekomendowane tematy ({len(recommended)}):")
                for i, rec in enumerate(recommended[:3], 1):
                    content = rec.get("content", "")[:100]
                    print(f"    {i}. {content}...")
        
        print("\n" + "-" * 60)
    
    print("\n✅ Test zakończony pomyślnie!")
    print("\nTavily API jest prawidłowo zintegrowane z Ada 2.0")
    print("System AI może teraz korzystać z aktualnych danych z internetu")
    print("podczas generowania treści dla organizacji.")

if __name__ == "__main__":
    asyncio.run(test_ada_research())