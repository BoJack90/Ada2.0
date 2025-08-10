"""
Deep Reasoning System for Advanced Content Generation

This module implements a multi-step reasoning approach for content generation,
using Chain-of-Thought, research integration, and iterative refinement.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import asyncio
import aiohttp

from sqlalchemy.orm import Session

from app.core.prompt_manager import PromptManager
from app.core.ai_config_service import AIConfigService
from app.tasks.content_generation import _call_gemini_api

logger = logging.getLogger(__name__)


class DeepReasoningEngine:
    """
    Advanced reasoning engine that uses multi-step approach for content generation
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.prompt_manager = PromptManager(db)
        self.ai_config = AIConfigService(db)
        
    async def analyze_with_reasoning(
        self, 
        context: Dict[str, Any], 
        task_type: str = "generate_topics"
    ) -> Dict[str, Any]:
        """
        Perform deep analysis using Chain-of-Thought reasoning
        
        Args:
            context: Input context including briefs, strategy, etc.
            task_type: Type of task (generate_topics, analyze_brief, etc.)
            
        Returns:
            Enhanced context with reasoning steps and results
        """
        logger.info(f"Starting deep reasoning for task: {task_type}")
        
        # Step 1: Context Understanding
        understanding = await self._understand_context(context)
        
        # Step 2: Research Enhancement
        research_data = await self._conduct_research(understanding)
        
        # Step 3: Strategy Formulation
        strategy = await self._formulate_strategy(understanding, research_data)
        
        # Step 4: Creative Generation
        creative_output = await self._generate_creative_content(strategy, context)
        
        # Step 5: Quality Evaluation
        evaluated_output = await self._evaluate_and_refine(creative_output, context)
        
        return {
            "reasoning_steps": {
                "understanding": understanding,
                "research": research_data,
                "strategy": strategy,
                "creative_output": creative_output,
                "final_output": evaluated_output
            },
            "result": evaluated_output
        }
    
    async def _understand_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 1: Deep understanding of the context using Chain-of-Thought
        """
        prompt = f"""
Analyze the following context for content generation using step-by-step reasoning:

Context:
{json.dumps(context, ensure_ascii=False, indent=2)}

Please think through this step-by-step:

1. **Organization Analysis**:
   - What is the company's industry and main focus?
   - What are their communication goals?
   - Who is their target audience?

2. **Brief Analysis**:
   - What are the key topics from the briefs?
   - What priorities are mentioned?
   - Are there any specific requirements or constraints?

3. **Strategy Understanding**:
   - What is the preferred tone and style?
   - Are there forbidden phrases or required CTAs?
   - What platforms are we targeting?

4. **Content Requirements**:
   - How many pieces of content are needed?
   - What types of content (blog, social media)?
   - Are there any correlations required?

5. **Key Insights**:
   - What unique angles can we explore?
   - What industry trends are relevant?
   - What would resonate with the target audience?

Provide your analysis in JSON format with detailed reasoning for each section.
"""
        
        model = self.ai_config._get_cached_model("deep_reasoning") or "gemini-1.5-pro-latest"
        response = _call_gemini_api(prompt, model)
        
        try:
            return json.loads(response)
        except:
            return {"error": "Failed to parse understanding", "raw": response}
    
    async def _conduct_research(self, understanding: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 2: Conduct research using Tavily and other sources
        """
        research_topics = []
        
        # Extract topics to research from understanding
        if "organization_analysis" in understanding:
            industry = understanding["organization_analysis"].get("industry", "")
            if industry:
                research_topics.append(f"{industry} trends 2024")
                research_topics.append(f"{industry} content marketing best practices")
        
        if "key_insights" in understanding:
            trends = understanding["key_insights"].get("industry_trends", [])
            research_topics.extend(trends[:3])
        
        # Conduct Tavily research
        research_results = {}
        if research_topics:
            research_results = await self._tavily_research(research_topics)
        
        # Analyze research results
        research_prompt = f"""
Based on the research data below, extract key insights for content creation:

Research Results:
{json.dumps(research_results, ensure_ascii=False, indent=2)}

Original Understanding:
{json.dumps(understanding, ensure_ascii=False, indent=2)}

Provide:
1. Top 5 trending topics in the industry
2. Content gaps we can fill
3. Competitor content strategies
4. Audience interests and pain points
5. Seasonal or timely opportunities

Format as JSON.
"""
        
        model = self.ai_config._get_cached_model("research_analysis") or "gemini-1.5-pro-latest"
        response = _call_gemini_api(research_prompt, model)
        
        try:
            return json.loads(response)
        except:
            return {"research_topics": research_topics, "raw_results": research_results}
    
    async def _tavily_research(self, topics: List[str]) -> Dict[str, Any]:
        """
        Perform research using Tavily API
        """
        import os
        tavily_api_key = os.getenv('TAVILY_API_KEY')
        
        if not tavily_api_key:
            logger.warning("Tavily API key not found")
            return {}
        
        results = {}
        
        try:
            # Use Tavily REST API
            headers = {
                "api-key": tavily_api_key,
                "content-type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                for topic in topics[:5]:  # Limit to 5 searches
                    payload = {
                        "query": topic,
                        "search_depth": "advanced",
                        "max_results": 5,
                        "include_answer": True
                    }
                    
                    async with session.post(
                        "https://api.tavily.com/search",
                        json=payload,
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            results[topic] = {
                                "answer": data.get("answer", ""),
                                "results": [
                                    {
                                        "title": r.get("title", ""),
                                        "content": r.get("content", "")[:500],
                                        "url": r.get("url", "")
                                    }
                                    for r in data.get("results", [])[:3]
                                ]
                            }
                        else:
                            logger.error(f"Tavily API error: {response.status}")
                            
        except Exception as e:
            logger.error(f"Tavily research error: {e}")
            
        return results
    
    async def _formulate_strategy(
        self, 
        understanding: Dict[str, Any], 
        research: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Step 3: Formulate content strategy based on understanding and research
        """
        strategy_prompt = f"""
Based on the deep understanding and research, formulate a content strategy:

Understanding:
{json.dumps(understanding, ensure_ascii=False, indent=2)}

Research Insights:
{json.dumps(research, ensure_ascii=False, indent=2)}

Create a comprehensive content strategy that includes:

1. **Content Pillars** (3-5 main themes):
   - Each pillar should align with business goals
   - Consider research insights and trends
   - Ensure variety and audience appeal

2. **Content Mix**:
   - Educational content ratio
   - Promotional content ratio
   - Engagement content ratio
   - Thought leadership ratio

3. **Topic Clusters**:
   - Group related topics together
   - Plan content series
   - Identify cornerstone content

4. **Differentiation Strategy**:
   - Unique angles to explore
   - Brand voice implementation
   - Competitive advantages

5. **Brief Alignment**:
   - How each topic connects to brief requirements
   - Priority mapping
   - Key message integration

Provide as detailed JSON with rationale for each decision.
"""
        
        model = self.ai_config._get_cached_model("strategy_formulation") or "gemini-1.5-pro-latest"
        response = _call_gemini_api(strategy_prompt, model)
        
        try:
            return json.loads(response)
        except:
            return {"error": "Failed to parse strategy", "raw": response}
    
    async def _generate_creative_content(
        self, 
        strategy: Dict[str, Any], 
        original_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Step 4: Generate creative content based on strategy
        """
        # Extract content requirements
        blog_quota = original_context.get("content_plan", {}).get("blog_posts_quota", 5)
        topics_to_generate = blog_quota + 3  # Generate extra for selection
        
        creative_prompt = f"""
Based on the content strategy, generate {topics_to_generate} creative blog topics:

Strategy:
{json.dumps(strategy, ensure_ascii=False, indent=2)}

Original Requirements:
- Organization: {original_context.get("organization", {}).get("name", "Unknown")}
- Industry: {original_context.get("organization", {}).get("industry", "Unknown")}
- Brief Key Topics: {json.dumps(original_context.get("brief_insights", {}).get("key_topics", []), ensure_ascii=False)}
- Communication Style: {json.dumps(original_context.get("communication_strategy", {}).get("general_style", {}), ensure_ascii=False)}

For each topic, provide:
1. "title": Engaging, SEO-friendly title
2. "description": 2-3 sentence description
3. "pillar": Which content pillar it belongs to
4. "brief_alignment": How it aligns with brief requirements
5. "unique_angle": What makes this topic special
6. "target_keywords": 3-5 SEO keywords
7. "content_type": "educational" | "thought_leadership" | "case_study" | "how_to" | "industry_insights"
8. "priority_score": 1-10 based on brief alignment and strategy

Ensure topics are:
- Diverse across content pillars
- Aligned with brief priorities
- Incorporating research insights
- Suitable for the target audience
- NOT repeating rejected topics

Format as JSON array.
"""
        
        model = self.ai_config._get_cached_model("creative_generation") or "gemini-1.5-pro-latest"
        response = _call_gemini_api(creative_prompt, model)
        
        try:
            topics = json.loads(response)
            return {"topics": topics, "count": len(topics)}
        except:
            return {"error": "Failed to parse creative output", "raw": response}
    
    async def _evaluate_and_refine(
        self, 
        creative_output: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Step 5: Evaluate and refine the generated content
        """
        if "error" in creative_output:
            return creative_output
            
        topics = creative_output.get("topics", [])
        
        evaluation_prompt = f"""
Evaluate and refine the generated topics using these criteria:

Generated Topics:
{json.dumps(topics, ensure_ascii=False, indent=2)}

Evaluation Criteria:
1. Brief Alignment: Do topics address brief requirements?
2. Diversity: Is there good variety across pillars?
3. Audience Appeal: Will these resonate with target audience?
4. Uniqueness: Are topics fresh and not generic?
5. Feasibility: Can quality content be created for each?
6. SEO Potential: Do topics have search potential?

Brief Requirements:
{json.dumps(context.get("brief_insights", {}), ensure_ascii=False, indent=2)}

For each topic:
1. Provide a quality score (1-10)
2. Suggest improvements if needed
3. Flag any concerns

Then provide final refined list with improvements applied.

Format as JSON with "evaluation" and "refined_topics" sections.
"""
        
        model = self.ai_config._get_cached_model("evaluation") or "gemini-1.5-pro-latest"
        response = _call_gemini_api(evaluation_prompt, model)
        
        try:
            evaluation_result = json.loads(response)
            return evaluation_result.get("refined_topics", topics)
        except:
            return topics  # Return original if evaluation fails


class EnhancedBriefAnalyzer:
    """
    Advanced brief analyzer using multi-layered analysis
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.reasoning_engine = DeepReasoningEngine(db)
        
    async def analyze_brief(
        self, 
        brief_text: str, 
        organization_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform deep analysis of content brief
        """
        analysis_prompt = f"""
Perform a comprehensive analysis of this content brief:

Brief Content:
{brief_text[:8000]}

Organization Context:
{json.dumps(organization_context, ensure_ascii=False, indent=2)}

Analyze the following aspects:

1. **Core Topics** (Extract all mentioned topics):
   - Main themes
   - Subtopics
   - Related concepts

2. **Priority Analysis**:
   - Explicitly stated priorities
   - Implied priorities from emphasis
   - Urgency indicators

3. **Requirements Extraction**:
   - Specific content requirements
   - Tone/style requirements
   - Technical requirements
   - Compliance needs

4. **Target Audience Insights**:
   - Primary audience
   - Secondary audiences
   - Audience pain points mentioned

5. **Key Messages**:
   - Core messages to convey
   - Value propositions
   - Calls to action

6. **Content Opportunities**:
   - Content series potential
   - Cross-platform opportunities
   - Evergreen vs. timely content

7. **Strategic Alignment**:
   - Business goals mentioned
   - KPIs or metrics
   - Campaign connections

Provide detailed JSON analysis with confidence scores for each extraction.
"""
        
        model = self.ai_config._get_cached_model("brief_analysis") or "gemini-1.5-pro-latest"
        response = _call_gemini_api(analysis_prompt, model)
        
        try:
            analysis = json.loads(response)
            
            # Enhance with research if key topics found
            if analysis.get("core_topics"):
                research_context = {
                    "brief_analysis": analysis,
                    "organization": organization_context
                }
                enhanced = await self.reasoning_engine.analyze_with_reasoning(
                    research_context, 
                    "enhance_brief"
                )
                analysis["enhanced_insights"] = enhanced.get("result", {})
                
            return analysis
            
        except Exception as e:
            logger.error(f"Brief analysis error: {e}")
            return {
                "error": "Analysis failed",
                "basic_analysis": self._basic_brief_analysis(brief_text)
            }
    
    def _basic_brief_analysis(self, text: str) -> Dict[str, Any]:
        """Fallback basic analysis"""
        words = text.lower().split()
        return {
            "word_count": len(words),
            "estimated_topics": min(len(words) // 100, 10),
            "requires_manual_review": True
        }


class IndustryKnowledgeBase:
    """
    Build and maintain industry-specific knowledge
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.cache = {}
        
    async def analyze_company_website(self, website_url: str) -> Dict[str, Any]:
        """
        Analyze company website to understand the business
        """
        if not website_url:
            return {}
            
        try:
            # Fetch website content
            async with aiohttp.ClientSession() as session:
                async with session.get(website_url, timeout=10) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        
            # Extract and analyze
            analysis_prompt = f"""
Analyze this company website to understand their business:

Website URL: {website_url}
Content Preview: {html_content[:5000]}

Extract:
1. Industry/Sector
2. Main products/services
3. Target market
4. Company values/mission
5. Key differentiators
6. Content tone/style from existing content

Format as JSON.
"""
            
            model = "gemini-1.5-pro-latest"
            response = _call_gemini_api(analysis_prompt, model)
            
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Website analysis error: {e}")
            return {"error": str(e), "url": website_url}
    
    async def get_industry_insights(self, industry: str) -> Dict[str, Any]:
        """
        Get industry-specific insights for content generation
        """
        if industry in self.cache:
            return self.cache[industry]
            
        insights = await self._fetch_industry_insights(industry)
        self.cache[industry] = insights
        return insights
        
    async def _fetch_industry_insights(self, industry: str) -> Dict[str, Any]:
        """
        Fetch comprehensive industry insights
        """
        research_queries = [
            f"{industry} industry trends 2024",
            f"{industry} content marketing examples",
            f"{industry} customer pain points",
            f"{industry} innovation topics",
            f"{industry} thought leadership"
        ]
        
        engine = DeepReasoningEngine(self.db)
        research_results = await engine._tavily_research(research_queries)
        
        # Synthesize insights
        synthesis_prompt = f"""
Synthesize industry insights from research:

Industry: {industry}
Research Data: {json.dumps(research_results, ensure_ascii=False, indent=2)}

Provide:
1. Top content themes in this industry
2. Audience preferences
3. Successful content formats
4. Industry-specific terminology
5. Compliance considerations
6. Seasonal patterns

Format as actionable JSON insights for content generation.
"""
        
        model = "gemini-1.5-pro-latest"
        response = _call_gemini_api(synthesis_prompt, model)
        
        try:
            return json.loads(response)
        except:
            return {"industry": industry, "basic_insights": True}