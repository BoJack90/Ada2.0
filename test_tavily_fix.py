#!/usr/bin/env python
"""
Quick test to verify Tavily API fix
"""
import os
import asyncio
from tavily import TavilyClient

# Test the fixed search method
def test_tavily_search():
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        print("❌ TAVILY_API_KEY not found in environment")
        return False
    
    try:
        client = TavilyClient(api_key=api_key)
        
        # Test with positional argument (fixed version)
        print("Testing fixed search with positional argument...")
        response = client.search(
            "artificial intelligence trends 2024",  # Positional argument
            search_depth="basic",
            max_results=3
        )
        
        if response and "results" in response:
            print(f"✅ Search successful! Found {len(response['results'])} results")
            for i, result in enumerate(response['results'][:2]):
                print(f"  Result {i+1}: {result.get('title', 'No title')[:60]}...")
            return True
        else:
            print("❌ No results returned")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

# Test the async wrapper
async def test_async_search():
    from app.core.external_integrations import TavilyIntegration
    
    try:
        tavily = TavilyIntegration()
        print("\nTesting async search wrapper...")
        
        result = await tavily.search(
            query="python programming best practices",
            search_depth="basic",
            max_results=3
        )
        
        if result and "results" in result:
            print(f"✅ Async search successful! Found {len(result['results'])} results")
            return True
        else:
            print("❌ Async search failed")
            return False
            
    except Exception as e:
        print(f"❌ Async error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Testing Tavily API Fix ===\n")
    
    # Test 1: Direct client
    sync_ok = test_tavily_search()
    
    # Test 2: Async wrapper
    print("\n" + "="*50)
    async_ok = asyncio.run(test_async_search())
    
    print("\n=== Test Summary ===")
    print(f"Direct client test: {'✅ PASSED' if sync_ok else '❌ FAILED'}")
    print(f"Async wrapper test: {'✅ PASSED' if async_ok else '❌ FAILED'}")
    
    if sync_ok and async_ok:
        print("\n🎉 All tests passed! Tavily integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")