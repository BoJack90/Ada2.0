"""
Test Tavily Integration
Test script to verify Tavily API integration is working properly
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from app.core.external_integrations import TavilyIntegration, ContentResearchOrchestrator

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

async def test_tavily_search():
    """Test basic Tavily search functionality"""
    print("Testing Tavily Search...")
    
    tavily = TavilyIntegration()
    
    # Test basic search
    results = await tavily.search(
        query="elektryka innowacje 2024 Polska",
        search_depth="advanced",
        max_results=3
    )
    
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        return False
    
    print(f"✅ Search successful! Found {results.get('total_results', 0)} results")
    print(f"   Themes: {', '.join(results.get('themes', [])[:5])}")
    
    if results.get('summary'):
        print(f"   Summary: {results['summary'][:200]}...")
    
    return True

async def test_tavily_news():
    """Test Tavily news search"""
    print("\nTesting Tavily News Search...")
    
    tavily = TavilyIntegration()
    
    results = await tavily.get_news(
        topic="elektryka automatyka",
        days=30,
        max_results=5
    )
    
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        return False
    
    print(f"✅ News search successful!")
    filtered_news = results.get("filtered_news", [])
    print(f"   Found {len(filtered_news)} recent news items")
    
    return True

async def test_competitor_analysis():
    """Test Tavily competitor analysis"""
    print("\nTesting Competitor Analysis...")
    
    tavily = TavilyIntegration()
    
    results = await tavily.analyze_competitors(
        company_name="Akson",
        industry="elektryka",
        aspects=["content marketing", "blog topics"]
    )
    
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        return False
    
    print(f"✅ Competitor analysis successful!")
    for aspect, data in results.items():
        print(f"   {aspect}: {len(data.get('examples', []))} examples found")
    
    return True

async def test_research_orchestrator():
    """Test comprehensive research orchestrator"""
    print("\nTesting Research Orchestrator...")
    
    orchestrator = ContentResearchOrchestrator()
    
    org_context = {
        "name": "Akson Elektro",
        "industry": "elektryka i automatyka",
        "description": "Firma zajmująca się instalacjami elektrycznymi"
    }
    
    results = await orchestrator.comprehensive_research(
        topic="inteligentne instalacje elektryczne",
        organization_context=org_context,
        research_depth="deep"
    )
    
    if not results:
        print(f"❌ No results returned")
        return False
    
    print(f"✅ Comprehensive research successful!")
    
    # Check sources
    sources = results.get("sources", {})
    for source_name, source_data in sources.items():
        if isinstance(source_data, dict) and "error" not in source_data:
            print(f"   ✓ {source_name}: Data retrieved successfully")
        else:
            print(f"   ✗ {source_name}: Failed or no data")
    
    # Check synthesis
    synthesis = results.get("synthesis", {})
    if synthesis:
        print(f"\n   Synthesis Results:")
        print(f"   - Key findings: {len(synthesis.get('key_findings', []))}")
        print(f"   - Content opportunities: {len(synthesis.get('content_opportunities', []))}")
        print(f"   - Trending angles: {len(synthesis.get('trending_angles', []))}")
    
    return True

async def main():
    """Run all tests"""
    print("=" * 60)
    print("TAVILY INTEGRATION TEST SUITE")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv('TAVILY_API_KEY')
    if not api_key:
        print("❌ TAVILY_API_KEY not found in environment variables!")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Run tests
    tests = [
        test_tavily_search(),
        test_tavily_news(),
        test_competitor_analysis(),
        test_research_orchestrator()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r is True)
    failed = len(results) - passed
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! Tavily integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())