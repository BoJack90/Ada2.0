"""
Enhanced Tavily integration for content generation
"""

import logging
from typing import Dict, Any, List, Optional
import os
from tavily import TavilyClient

logger = logging.getLogger(__name__)

TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
TAVILY_CLIENT = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None


class ResearchEngine:
    """Engine for performing intelligent research before content generation"""
    
    def __init__(self):
        self.client = TAVILY_CLIENT
        
    def research_for_blog_topics(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive research for blog topic generation
        
        Args:
            context: Super-context with organization and brief data
            
        Returns:
            Enhanced context with research insights
        """
        if not self.client:
            logger.warning("Tavily client not available")
            return context
            
        try:
            enhanced_context = context.copy()
            research_data = {
                "current_trends": [],
                "industry_insights": [],
                "content_gaps": [],
                "competitor_topics": [],
                "seasonal_opportunities": []
            }
            
            # Extract key information
            org_name = context.get("organization", {}).get("name", "")
            industry = context.get("organization", {}).get("industry", "")
            mandatory_topics = context.get("brief_insights", {}).get("mandatory_topics", [])
            
            # 1. Research current trends in the industry
            trends_results = self._search_trends(industry)
            research_data["current_trends"] = trends_results
            
            # 2. Research mandatory topics from briefs
            for topic in mandatory_topics[:3]:  # Limit to top 3
                topic_insights = self._deep_dive_topic(topic, industry)
                research_data["industry_insights"].extend(topic_insights)
            
            # 3. Identify content gaps
            gaps = self._find_content_gaps(industry, org_name)
            research_data["content_gaps"] = gaps
            
            # 4. Analyze competitor content
            competitor_analysis = self._analyze_competitors(industry)
            research_data["competitor_topics"] = competitor_analysis
            
            # 5. Check seasonal/timely opportunities
            seasonal = self._find_seasonal_topics(industry)
            research_data["seasonal_opportunities"] = seasonal
            
            # Add research to context
            enhanced_context["research_data"] = research_data
            
            # Generate content suggestions based on research
            enhanced_context["ai_research_suggestions"] = self._generate_suggestions(research_data)
            
            return enhanced_context
            
        except Exception as e:
            logger.error(f"Research engine error: {e}")
            return context
    
    def _search_trends(self, industry: str) -> List[Dict[str, Any]]:
        """Search for current trends in the industry"""
        query = f"{industry} trends 2024 Poland innovations"
        
        response = self.client.search(
            query,
            search_depth="advanced",
            max_results=5
        )
        
        trends = []
        if response and "results" in response:
            for result in response["results"]:
                trends.append({
                    "trend": result.get("title", ""),
                    "description": result.get("content", "")[:300],
                    "source": result.get("url", ""),
                    "relevance_score": result.get("score", 0)
                })
        
        return trends
    
    def _deep_dive_topic(self, topic: str, industry: str) -> List[Dict[str, Any]]:
        """Deep research on specific topic"""
        queries = [
            f"{topic} {industry} best practices 2024",
            f"{topic} implementation guide {industry}",
            f"{topic} case studies Poland"
        ]
        
        insights = []
        for query in queries:
            response = self.client.search(
                query,
                search_depth="advanced",
                max_results=3
            )
            
            if response and "results" in response:
                for result in response["results"]:
                    insights.append({
                        "aspect": query.split()[0],
                        "insight": result.get("content", "")[:400],
                        "url": result.get("url", "")
                    })
        
        return insights
    
    def _find_content_gaps(self, industry: str, company: str) -> List[Dict[str, Any]]:
        """Identify content gaps in the market"""
        query = f"{industry} content marketing gaps what nobody talks about"
        
        response = self.client.search(
            query,
            search_depth="advanced",
            max_results=5
        )
        
        gaps = []
        if response and "results" in response:
            for result in response["results"]:
                gaps.append({
                    "gap": self._extract_gap_from_content(result.get("content", "")),
                    "opportunity": self._suggest_opportunity(result.get("content", ""))
                })
        
        return gaps
    
    def _analyze_competitors(self, industry: str) -> List[Dict[str, Any]]:
        """Analyze what competitors are writing about"""
        query = f"{industry} top blog posts 2024 most shared content"
        
        response = self.client.search(
            query,
            search_depth="advanced",
            max_results=5
        )
        
        competitor_topics = []
        if response and "results" in response:
            for result in response["results"]:
                competitor_topics.append({
                    "topic": result.get("title", ""),
                    "angle": self._extract_angle(result.get("content", "")),
                    "performance_indicator": "high engagement"
                })
        
        return competitor_topics
    
    def _find_seasonal_topics(self, industry: str) -> List[Dict[str, Any]]:
        """Find seasonal or timely content opportunities"""
        from datetime import datetime
        current_month = datetime.now().strftime("%B")
        
        query = f"{industry} {current_month} seasonal content ideas events"
        
        response = self.client.search(
            query,
            search_depth="basic",
            max_results=3
        )
        
        seasonal = []
        if response and "results" in response:
            for result in response["results"]:
                seasonal.append({
                    "opportunity": result.get("title", ""),
                    "timing": current_month,
                    "relevance": result.get("content", "")[:200]
                })
        
        return seasonal
    
    def _generate_suggestions(self, research_data: Dict[str, Any]) -> List[str]:
        """Generate content suggestions based on research"""
        suggestions = []
        
        # Based on trends
        for trend in research_data.get("current_trends", [])[:3]:
            suggestions.append(
                f"Jak {trend['trend']} zmienia branżę - praktyczny przewodnik"
            )
        
        # Based on gaps
        for gap in research_data.get("content_gaps", [])[:2]:
            if gap.get("opportunity"):
                suggestions.append(gap["opportunity"])
        
        # Based on seasonal
        for seasonal in research_data.get("seasonal_opportunities", [])[:2]:
            suggestions.append(
                f"{seasonal['opportunity']} - co warto wiedzieć"
            )
        
        return suggestions
    
    def _extract_gap_from_content(self, content: str) -> str:
        """Extract content gap from search result"""
        # Simple extraction - in real implementation use NLP
        keywords = ["brakuje", "pomijane", "niewiele się mówi", "gap", "missing"]
        for keyword in keywords:
            if keyword in content.lower():
                # Extract sentence containing keyword
                sentences = content.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower():
                        return sentence.strip()
        return "Potential content opportunity identified"
    
    def _suggest_opportunity(self, content: str) -> str:
        """Suggest content opportunity based on gap"""
        # Simple suggestion generator
        if "automatyzacja" in content.lower():
            return "Kompletny przewodnik po automatyzacji w branży"
        elif "koszty" in content.lower():
            return "Jak optymalizować koszty - sprawdzone metody"
        elif "trendy" in content.lower():
            return "Przyszłość branży - kluczowe trendy na 2025"
        else:
            return "Praktyczne rozwiązania dla typowych wyzwań branżowych"
    
    def _extract_angle(self, content: str) -> str:
        """Extract the angle/approach from competitor content"""
        if "case study" in content.lower():
            return "Studium przypadku"
        elif "poradnik" in content.lower() or "guide" in content.lower():
            return "Praktyczny poradnik"
        elif "trendy" in content.lower() or "trends" in content.lower():
            return "Analiza trendów"
        else:
            return "Artykuł ekspercki"


def enhance_prompt_with_research(prompt_template: str, research_data: Dict[str, Any]) -> str:
    """
    Enhance prompt template with research insights
    
    Args:
        prompt_template: Original prompt template
        research_data: Research data from Tavily
        
    Returns:
        Enhanced prompt with research context
    """
    research_context = "\n\n=== RESEARCH INSIGHTS ===\n"
    
    # Add current trends
    if research_data.get("current_trends"):
        research_context += "\nAKTUALNE TRENDY W BRANŻY:\n"
        for trend in research_data["current_trends"][:3]:
            research_context += f"- {trend['trend']}: {trend['description'][:150]}...\n"
    
    # Add content gaps
    if research_data.get("content_gaps"):
        research_context += "\nZIDENTYFIKOWANE LUKI W TREŚCIACH:\n"
        for gap in research_data["content_gaps"][:3]:
            research_context += f"- {gap['gap']}\n"
    
    # Add AI suggestions
    if research_data.get("ai_research_suggestions"):
        research_context += "\nPROPOZYCJE TEMATÓW NA PODSTAWIE RESEARCH:\n"
        for suggestion in research_data["ai_research_suggestions"][:5]:
            research_context += f"- {suggestion}\n"
    
    # Insert research context into prompt
    enhanced_prompt = prompt_template + research_context
    
    return enhanced_prompt