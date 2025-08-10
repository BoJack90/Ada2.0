"""
External Service Integrations for Content Generation

Provides unified interface for Tavily, RAGFlow, and other external services.
"""

import os
import json
import logging
import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from tavily import TavilyClient

logger = logging.getLogger(__name__)


class TavilyIntegration:
    """
    Enhanced Tavily integration for research and content insights
    """
    
    def __init__(self):
        self.api_key = os.getenv('TAVILY_API_KEY')
        self.client = TavilyClient(api_key=self.api_key) if self.api_key else None
        self.cache = {}
        self.cache_ttl = timedelta(hours=24)
        
    async def check_tavily_status(self) -> Dict[str, Any]:
        """
        Check if Tavily API is working and has available quota
        
        Returns:
            Dict with status or error information
        """
        if not self.client:
            return {"error": "Tavily API key not configured"}
        
        try:
            # Try a minimal search to check API status
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.search(
                    "test",
                    search_depth="basic",
                    max_results=1
                )
            )
            return {"status": "ok"}
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Tavily status check failed: {error_msg}")
            return {"error": error_msg}
    
    async def search(
        self, 
        query: str, 
        search_depth: str = "advanced",
        max_results: int = 5,
        include_domains: List[str] = None,
        exclude_domains: List[str] = None
    ) -> Dict[str, Any]:
        """
        Perform advanced search using Tavily API
        """
        if not self.client:
            logger.warning("Tavily API key not configured")
            return {"error": "API key not configured"}
        
        # Check cache
        cache_key = f"{query}_{search_depth}_{max_results}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                logger.info(f"Using cached Tavily results for: {query}")
                return cached_data
        
        try:
            # Use the official Tavily client in a thread pool
            loop = asyncio.get_event_loop()
            
            # Run the sync method in executor
            response = await loop.run_in_executor(
                None,
                lambda: self.client.search(
                    query,
                    search_depth=search_depth,
                    max_results=max_results,
                    include_answer=True,
                    include_raw_content=False,
                    include_images=True,
                    include_domains=include_domains,
                    exclude_domains=exclude_domains
                )
            )
            
            # Process and enhance results
            enhanced_data = self._enhance_search_results(response)
            
            # Cache results
            self.cache[cache_key] = (enhanced_data, datetime.now())
            
            return enhanced_data
                        
        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            return {"error": str(e)}
    
    async def get_news(
        self,
        topic: str,
        days: int = 7,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Get recent news about a topic
        """
        query = f"{topic} news {datetime.now().year}"
        
        results = await self.search(
            query=query,
            search_depth="advanced",
            max_results=max_results
        )
        
        if "error" not in results:
            # Filter for recent content
            results["filtered_news"] = self._filter_recent_content(
                results.get("results", []), 
                days
            )
        
        return results
    
    async def analyze_competitors(
        self,
        company_name: str,
        industry: str,
        aspects: List[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze competitor content and strategies
        """
        if not aspects:
            aspects = ["content marketing", "blog topics", "social media"]
        
        competitor_insights = {}
        
        for aspect in aspects:
            query = f"{industry} {aspect} best practices examples -site:{company_name}.com"
            
            results = await self.search(
                query=query,
                search_depth="advanced",
                max_results=10
            )
            
            if "error" not in results:
                competitor_insights[aspect] = {
                    "key_insights": results.get("answer", ""),
                    "examples": [
                        {
                            "title": r.get("title", ""),
                            "url": r.get("url", ""),
                            "snippet": r.get("content", "")[:200]
                        }
                        for r in results.get("results", [])[:5]
                    ]
                }
        
        return competitor_insights
    
    async def analyze_website(
        self,
        website_url: str,
        organization_name: str = None
    ) -> Dict[str, Any]:
        """
        Comprehensive website analysis using Tavily search
        
        Args:
            website_url: URL of the website to analyze
            organization_name: Optional organization name for better context
            
        Returns:
            Dict with comprehensive website analysis
        """
        if not self.client:
            logger.warning("Tavily API key not configured")
            return {"error": "API key not configured"}
        
        try:
            # Normalize URL
            if not website_url.startswith(('http://', 'https://')):
                website_url = f"https://{website_url}"
            
            # Extract domain for targeted search
            from urllib.parse import urlparse
            parsed_url = urlparse(website_url)
            domain = parsed_url.netloc.replace('www.', '')
            
            analysis_results = {}
            
            # Check Tavily API status first
            test_result = await self.check_tavily_status()
            if "error" in test_result:
                error_msg = test_result["error"]
                if "usage limit" in error_msg.lower():
                    return {
                        "error": "Tavily API limit exceeded. Please check your Tavily API key or upgrade your plan at tavily.com",
                        "website_url": website_url,
                        "tavily_error": error_msg
                    }
                else:
                    return {
                        "error": f"Tavily API error: {error_msg}",
                        "website_url": website_url
                    }
            
            # 1. Search for company overview and services
            company_query = f"site:{domain} about services products offer"
            if organization_name:
                company_query = f"{organization_name} {company_query}"
            
            company_results = await self.search(
                query=company_query,
                search_depth="advanced",
                max_results=10,
                include_domains=[domain]
            )
            
            # 2. Search for industry and market position
            industry_query = f"site:{domain} industry sector market solutions"
            industry_results = await self.search(
                query=industry_query,
                search_depth="basic",
                max_results=5,
                include_domains=[domain]
            )
            
            # 3. Search for company values and mission
            values_query = f"site:{domain} mission values vision culture team"
            values_results = await self.search(
                query=values_query,
                search_depth="basic",
                max_results=5,
                include_domains=[domain]
            )
            
            # 4. Analyze content and blog if exists
            content_query = f"site:{domain} blog news articles insights"
            content_results = await self.search(
                query=content_query,
                search_depth="basic",
                max_results=10,
                include_domains=[domain]
            )
            
            # Collect all raw data for AI processing
            raw_data = {
                "company_results": company_results,
                "industry_results": industry_results,
                "values_results": values_results,
                "content_results": content_results,
                "website_url": website_url,
                "domain": domain,
                "organization_name": organization_name
            }
            
            # Process with AI for deep analysis
            ai_analysis = await self._process_with_ai(raw_data)
            
            # Combine AI analysis with basic extraction
            analysis_results = {
                "website_url": website_url,
                "domain": domain,
                "analysis_timestamp": datetime.now().isoformat(),
                
                # AI-enhanced analysis
                "company_overview": ai_analysis.get("company_overview", company_results.get("answer", "")),
                "services_detected": ai_analysis.get("services", self._extract_services(company_results)),
                "industry_detected": ai_analysis.get("industry", self._detect_industry(company_results, industry_results)),
                "company_values": ai_analysis.get("values", self._extract_values(values_results)),
                "target_audience": ai_analysis.get("target_audience", self._analyze_target_audience(company_results, content_results)),
                "key_topics": ai_analysis.get("key_topics", self._extract_key_topics(content_results)),
                "competitors_mentioned": ai_analysis.get("competitors", self._find_competitor_mentions(company_results, industry_results)),
                
                # Additional AI insights
                "unique_selling_points": ai_analysis.get("unique_selling_points", []),
                "content_strategy_insights": ai_analysis.get("content_strategy_insights", ""),
                "recommended_content_topics": ai_analysis.get("recommended_content_topics", []),
                "brand_personality": ai_analysis.get("brand_personality", ""),
                "key_differentiators": ai_analysis.get("key_differentiators", []),
                
                # Raw search results for reference
                "raw_results": {
                    "company_search": company_results.get("results", [])[:3],
                    "content_samples": content_results.get("results", [])[:3]
                }
            }
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Website analysis error: {e}")
            return {
                "error": str(e),
                "website_url": website_url
            }
    
    def _extract_services(self, search_results: Dict[str, Any]) -> List[str]:
        """Extract services/products from search results"""
        services = []
        
        # From AI answer
        answer = search_results.get("answer", "")
        if "service" in answer.lower() or "product" in answer.lower():
            # Simple extraction - can be enhanced with NLP
            lines = answer.split('.')
            for line in lines:
                if any(word in line.lower() for word in ["service", "offer", "provide", "solution"]):
                    services.append(line.strip())
        
        # From search results
        for result in search_results.get("results", [])[:5]:
            content = result.get("content", "")
            if "service" in content.lower() or "product" in content.lower():
                # Extract sentences mentioning services
                sentences = content.split('.')[:3]
                for sentence in sentences:
                    if any(word in sentence.lower() for word in ["service", "product", "solution"]):
                        services.append(sentence.strip())
        
        # Deduplicate and limit
        return list(set(services))[:10]
    
    def _detect_industry(self, company_results: Dict, industry_results: Dict) -> str:
        """Detect industry from search results"""
        industry_keywords = {}
        
        # Common industry indicators
        industries = {
            "technology": ["software", "IT", "tech", "digital", "cloud", "SaaS"],
            "elektryka": ["elektryczne", "elektryka", "instalacje", "electrical", "automation"],
            "marketing": ["marketing", "advertising", "brand", "media"],
            "finance": ["financial", "banking", "investment", "fintech"],
            "healthcare": ["health", "medical", "healthcare", "pharma"],
            "education": ["education", "learning", "training", "academic"],
            "retail": ["retail", "store", "shopping", "commerce"],
            "manufacturing": ["manufacturing", "production", "factory", "industrial"]
        }
        
        # Analyze all text
        all_text = (company_results.get("answer", "") + " " + 
                   industry_results.get("answer", "")).lower()
        
        for industry, keywords in industries.items():
            count = sum(1 for keyword in keywords if keyword in all_text)
            if count > 0:
                industry_keywords[industry] = count
        
        # Return most mentioned industry
        if industry_keywords:
            return max(industry_keywords, key=industry_keywords.get)
        
        return "business"
    
    def _extract_values(self, values_results: Dict) -> List[str]:
        """Extract company values from search results"""
        values = []
        
        answer = values_results.get("answer", "")
        if answer:
            # Look for value-related keywords
            value_keywords = ["mission", "vision", "value", "believe", "commitment", "dedicated"]
            sentences = answer.split('.')
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in value_keywords):
                    values.append(sentence.strip())
        
        return values[:5]
    
    def _analyze_target_audience(self, company_results: Dict, content_results: Dict) -> List[str]:
        """Analyze target audience from content"""
        audiences = []
        
        # Audience indicators
        audience_keywords = {
            "B2B": ["enterprise", "business", "company", "organization", "corporate"],
            "B2C": ["consumer", "customer", "individual", "personal", "user"],
            "SME": ["small business", "SME", "startup", "entrepreneur"],
            "Enterprise": ["enterprise", "large organization", "corporation"]
        }
        
        all_text = (company_results.get("answer", "") + " " + 
                   content_results.get("answer", "")).lower()
        
        for audience_type, keywords in audience_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                audiences.append(audience_type)
        
        return audiences
    
    
    def _extract_key_topics(self, content_results: Dict) -> List[str]:
        """Extract key topics from content"""
        topics = []
        
        # Extract from search results titles
        for result in content_results.get("results", [])[:10]:
            title = result.get("title", "")
            if title and len(title) > 10:
                topics.append(title)
        
        return topics[:10]
    
    def _find_competitor_mentions(self, company_results: Dict, industry_results: Dict) -> List[str]:
        """Find mentions of competitors"""
        competitors = []
        
        # Look for comparison keywords
        comparison_keywords = ["vs", "versus", "compared to", "alternative", "competitor"]
        
        all_text = (company_results.get("answer", "") + " " + 
                   industry_results.get("answer", ""))
        
        sentences = all_text.split('.')
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in comparison_keywords):
                # Extract potential competitor names (simple approach)
                words = sentence.split()
                for i, word in enumerate(words):
                    if word.lower() in comparison_keywords and i > 0:
                        potential_competitor = words[i-1]
                        if len(potential_competitor) > 2 and potential_competitor[0].isupper():
                            competitors.append(potential_competitor)
        
        return list(set(competitors))[:5]
    
    async def _process_with_ai(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw Tavily search results with AI for deep analysis
        
        Args:
            raw_data: Raw data from Tavily searches including company, industry, values, and content results
            
        Returns:
            Dict with AI-enhanced analysis
        """
        try:
            # Import Gemini AI module
            from app.core.ai_service import GeminiAI
            
            # Initialize AI service
            ai_service = GeminiAI()
            
            # Prepare context from raw data
            company_info = raw_data.get("company_results", {})
            industry_info = raw_data.get("industry_results", {})
            values_info = raw_data.get("values_results", {})
            content_info = raw_data.get("content_results", {})
            
            # Combine all search results into a comprehensive text
            combined_text = f"""
            COMPANY INFORMATION:
            {company_info.get('answer', '')}
            
            SEARCH RESULTS:
            {' '.join([r.get('content', '')[:500] for r in company_info.get('results', [])[:5]])}
            
            INDUSTRY CONTEXT:
            {industry_info.get('answer', '')}
            
            VALUES AND MISSION:
            {values_info.get('answer', '')}
            
            CONTENT SAMPLES:
            {' '.join([r.get('title', '') + ': ' + r.get('content', '')[:300] for r in content_info.get('results', [])[:5]])}
            """
            
            # Create detailed prompt for AI analysis
            analysis_prompt = f"""
            You are an expert business analyst specializing in company analysis and content strategy. 
            Analyze the following information about the company and provide a comprehensive, detailed analysis.
            
            Company Website: {raw_data.get('website_url', '')}
            Company Name: {raw_data.get('organization_name', 'Unknown')}
            
            {combined_text}
            
            Based on this information, provide a DETAILED and SPECIFIC analysis in JSON format with the following structure:
            
            {{
                "company_overview": "Comprehensive 2-3 sentence overview of what the company does, their main value proposition, and market position",
                
                "industry": "Specific industry classification (be precise - e.g., 'B2B SaaS for HR Management' not just 'technology' or 'business')",
                
                "services": [
                    "List of specific services/products offered (be detailed, e.g., 'Cloud-based employee onboarding platform' not just 'software')",
                    "Include at least 3-5 specific services if available"
                ],
                
                "values": [
                    "Core company values and principles (extract from mission/vision statements)",
                    "Include specific values mentioned on the website"
                ],
                
                "target_audience": [
                    "Primary target audience segments (be specific, e.g., 'Mid-size tech companies with 50-500 employees')",
                    "Include multiple segments if applicable"
                ],
                
                
                "key_topics": [
                    "Main content topics and themes the company focuses on",
                    "Include specific topics from their blog/content if available"
                ],
                
                "unique_selling_points": [
                    "What makes this company unique compared to competitors",
                    "Specific differentiators and competitive advantages"
                ],
                
                "content_strategy_insights": "Analysis of their current content strategy - what types of content they create, how often, what channels they use, what seems to work well",
                
                "recommended_content_topics": [
                    "Suggested content topics that would resonate with their audience",
                    "Based on industry trends and gaps in their current content"
                ],
                
                "brand_personality": "Detailed description of the brand's personality traits (e.g., 'Innovative, trustworthy, customer-centric, data-driven')",
                
                "key_differentiators": [
                    "Specific features or approaches that differentiate them from competitors",
                    "Include technological, service, or business model differentiators"
                ],
                
                "competitors": [
                    "List of potential competitors mentioned or implied"
                ],
                
                "market_positioning": "How the company positions itself in the market (leader, challenger, niche player, etc.)",
                
                "customer_pain_points": [
                    "Key problems the company solves for customers",
                    "Pain points addressed by their solutions"
                ],
                
                "technology_stack": [
                    "Technologies or platforms mentioned (if applicable)"
                ],
                
                "partnership_ecosystem": [
                    "Key partners, integrations, or ecosystem relationships mentioned"
                ]
            }}
            
            IMPORTANT INSTRUCTIONS:
            1. Be SPECIFIC and DETAILED - avoid generic terms like "business", "informative", "professional"
            2. Extract real information from the provided text, don't make assumptions
            3. If information is not available for a field, use null or empty array
            4. Focus on actionable insights that would help generate targeted content
            5. Ensure the analysis is relevant for content generation and marketing purposes
            6. Return ONLY valid JSON, no additional text or explanations
            """
            
            # Get AI analysis
            response = await ai_service.generate_content(
                analysis_prompt,
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=2000
            )
            
            # Parse AI response
            import json
            import re
            
            # Extract JSON from response (in case AI adds extra text)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    ai_analysis = json.loads(json_match.group())
                    
                    # Validate and clean the analysis
                    cleaned_analysis = {
                        "company_overview": ai_analysis.get("company_overview", ""),
                        "industry": ai_analysis.get("industry", "Unknown"),
                        "services": ai_analysis.get("services", [])[:10],
                        "values": ai_analysis.get("values", [])[:10],
                        "target_audience": ai_analysis.get("target_audience", [])[:5],
                        "content_tone": ai_analysis.get("content_tone", "Professional"),
                        "key_topics": ai_analysis.get("key_topics", [])[:15],
                        "unique_selling_points": ai_analysis.get("unique_selling_points", [])[:10],
                        "content_strategy_insights": ai_analysis.get("content_strategy_insights", ""),
                        "recommended_content_topics": ai_analysis.get("recommended_content_topics", [])[:10],
                        "brand_personality": ai_analysis.get("brand_personality", ""),
                        "key_differentiators": ai_analysis.get("key_differentiators", [])[:10],
                        "competitors": ai_analysis.get("competitors", [])[:10],
                        "market_positioning": ai_analysis.get("market_positioning", ""),
                        "customer_pain_points": ai_analysis.get("customer_pain_points", [])[:10],
                        "technology_stack": ai_analysis.get("technology_stack", [])[:10],
                        "partnership_ecosystem": ai_analysis.get("partnership_ecosystem", [])[:10]
                    }
                    
                    logger.info(f"AI analysis completed successfully for {raw_data.get('website_url', 'unknown')}")
                    return cleaned_analysis
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse AI response as JSON: {e}")
                    logger.debug(f"AI response: {response}")
            else:
                logger.error("No JSON found in AI response")
                logger.debug(f"AI response: {response}")
            
            # Return empty analysis if AI processing fails
            return {}
            
        except Exception as e:
            logger.error(f"Error in AI processing: {e}")
            # Return empty dict on error - fallback to basic analysis
            return {}
    
    def _enhance_search_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance search results with additional processing
        """
        if "results" not in data:
            return data
        
        # Extract key themes
        all_content = " ".join([
            r.get("content", "") for r in data["results"]
        ])
        
        themes = self._extract_themes(all_content)
        
        # Categorize results
        categorized = self._categorize_results(data["results"])
        
        return {
            **data,
            "themes": themes,
            "categorized_results": categorized,
            "summary": data.get("answer", ""),
            "total_results": len(data["results"])
        }
    
    def _extract_themes(self, content: str) -> List[str]:
        """
        Extract main themes from content
        """
        # Simple theme extraction - in production, use NLP
        words = content.lower().split()
        word_freq = {}
        
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
        
        for word in words:
            if len(word) > 4 and word not in stopwords:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top themes
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        themes = [word[0] for word in sorted_words[:10]]
        
        return themes
    
    def _categorize_results(self, results: List[Dict]) -> Dict[str, List]:
        """
        Categorize search results by type
        """
        categories = {
            "articles": [],
            "news": [],
            "guides": [],
            "research": [],
            "other": []
        }
        
        for result in results:
            title = result.get("title", "").lower()
            url = result.get("url", "").lower()
            
            if any(word in title for word in ["news", "breaking", "update"]):
                categories["news"].append(result)
            elif any(word in title for word in ["guide", "how to", "tutorial"]):
                categories["guides"].append(result)
            elif any(word in title for word in ["research", "study", "report"]):
                categories["research"].append(result)
            elif any(word in url for word in ["blog", "article"]):
                categories["articles"].append(result)
            else:
                categories["other"].append(result)
        
        return categories
    
    def _filter_recent_content(self, results: List[Dict], days: int) -> List[Dict]:
        """
        Filter results for recent content
        """
        recent = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for result in results:
            # Try to parse date from result
            published_date = result.get("published_date")
            if published_date:
                try:
                    pub_date = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                    if pub_date > cutoff_date:
                        recent.append(result)
                except:
                    pass
        
        return recent


class RAGFlowIntegration:
    """
    RAGFlow integration for knowledge base and content retrieval
    """
    
    def __init__(self):
        self.base_url = os.getenv('RAGFLOW_API_URL', 'http://localhost:9380')
        self.api_key = os.getenv('RAGFLOW_API_KEY')
        self.knowledge_base_id = os.getenv('RAGFLOW_KB_ID')
        
    async def search_knowledge_base(
        self,
        query: str,
        top_k: int = 5,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Search the RAGFlow knowledge base
        """
        if not self.api_key:
            logger.warning("RAGFlow not configured")
            return {"error": "RAGFlow not configured"}
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "query": query,
                "top_k": top_k,
                "kb_id": self.knowledge_base_id
            }
            
            if filters:
                payload["filters"] = filters
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v1/search",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._process_rag_results(data)
                    else:
                        logger.error(f"RAGFlow API error: {response.status}")
                        return {"error": f"API error: {response.status}"}
                        
        except Exception as e:
            logger.error(f"RAGFlow search error: {e}")
            return {"error": str(e)}
    
    async def add_to_knowledge_base(
        self,
        content: str,
        metadata: Dict[str, Any],
        document_type: str = "content_brief"
    ) -> Dict[str, Any]:
        """
        Add content to RAGFlow knowledge base
        """
        if not self.api_key:
            return {"error": "RAGFlow not configured"}
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "kb_id": self.knowledge_base_id,
                "content": content,
                "metadata": {
                    **metadata,
                    "document_type": document_type,
                    "indexed_at": datetime.now().isoformat()
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v1/documents",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status in [200, 201]:
                        data = await response.json()
                        return {"success": True, "document_id": data.get("id")}
                    else:
                        return {"error": f"Failed to add document: {response.status}"}
                        
        except Exception as e:
            logger.error(f"RAGFlow add document error: {e}")
            return {"error": str(e)}
    
    async def get_similar_content(
        self,
        content: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar content in knowledge base
        """
        results = await self.search_knowledge_base(
            query=content,
            top_k=limit
        )
        
        if "error" in results:
            return []
        
        return results.get("documents", [])
    
    def _process_rag_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and enhance RAG results
        """
        documents = data.get("documents", [])
        
        # Group by document type
        grouped = {}
        for doc in documents:
            doc_type = doc.get("metadata", {}).get("document_type", "unknown")
            if doc_type not in grouped:
                grouped[doc_type] = []
            grouped[doc_type].append({
                "content": doc.get("content", ""),
                "score": doc.get("score", 0),
                "metadata": doc.get("metadata", {})
            })
        
        return {
            "total_results": len(documents),
            "grouped_results": grouped,
            "top_result": documents[0] if documents else None
        }


class ContentResearchOrchestrator:
    """
    Orchestrates multiple research sources for comprehensive insights
    """
    
    def __init__(self):
        self.tavily = TavilyIntegration()
        self.ragflow = RAGFlowIntegration()
        
    async def comprehensive_research(
        self,
        topic: str,
        organization_context: Dict[str, Any],
        research_depth: str = "deep"
    ) -> Dict[str, Any]:
        """
        Perform comprehensive research using all available sources
        """
        research_tasks = []
        
        # Tavily research
        research_tasks.append(
            self.tavily.search(
                f"{topic} {organization_context.get('industry', '')}",
                search_depth="advanced"
            )
        )
        
        # Industry news
        research_tasks.append(
            self.tavily.get_news(
                topic,
                days=30
            )
        )
        
        # Competitor analysis
        if organization_context.get("name"):
            research_tasks.append(
                self.tavily.analyze_competitors(
                    organization_context["name"],
                    organization_context.get("industry", "business")
                )
            )
        
        # RAGFlow knowledge base
        research_tasks.append(
            self.ragflow.search_knowledge_base(
                topic,
                top_k=10
            )
        )
        
        # Execute all research in parallel
        results = await asyncio.gather(*research_tasks, return_exceptions=True)
        
        # Process results
        combined_insights = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "sources": {
                "web_search": results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])},
                "recent_news": results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])},
                "competitor_insights": results[2] if len(results) > 2 and not isinstance(results[2], Exception) else {},
                "knowledge_base": results[3] if len(results) > 3 and not isinstance(results[3], Exception) else {}
            }
        }
        
        # Synthesize insights
        synthesis = await self._synthesize_research(combined_insights)
        combined_insights["synthesis"] = synthesis
        
        return combined_insights
    
    async def _synthesize_research(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize research findings into actionable insights
        """
        synthesis = {
            "key_findings": [],
            "content_opportunities": [],
            "trending_angles": [],
            "recommended_topics": []
        }
        
        # Extract key findings from web search
        web_data = research_data["sources"].get("web_search", {})
        if "themes" in web_data:
            synthesis["key_findings"].extend(web_data["themes"][:5])
        
        # Extract trending topics from news
        news_data = research_data["sources"].get("recent_news", {})
        if "filtered_news" in news_data:
            for news in news_data["filtered_news"][:3]:
                synthesis["trending_angles"].append(news.get("title", ""))
        
        # Extract competitor strategies
        competitor_data = research_data["sources"].get("competitor_insights", {})
        for aspect, insights in competitor_data.items():
            if isinstance(insights, dict) and "examples" in insights:
                for example in insights["examples"][:2]:
                    synthesis["content_opportunities"].append({
                        "aspect": aspect,
                        "inspiration": example.get("title", ""),
                        "url": example.get("url", "")
                    })
        
        # Knowledge base insights
        kb_data = research_data["sources"].get("knowledge_base", {})
        if "top_result" in kb_data and kb_data["top_result"]:
            synthesis["recommended_topics"].append({
                "source": "knowledge_base",
                "content": kb_data["top_result"].get("content", "")[:200]
            })
        
        return synthesis
    
    async def research_topic(
        self,
        topic: str,
        context: Dict[str, Any],
        num_queries: int = 3
    ) -> Dict[str, Any]:
        """
        Research a specific topic using Tavily
        
        Args:
            topic: The topic to research
            context: Additional context (organization, industry, etc.)
            num_queries: Number of search queries to perform
            
        Returns:
            Research results dictionary
        """
        try:
            # Extract context information
            organization_name = context.get("organization_name", "")
            industry = context.get("industry", "")
            
            # Perform basic search
            search_query = f"{topic} {industry} {datetime.now().year}"
            results = await self.tavily.search(
                query=search_query,
                search_depth="advanced",
                max_results=10
            )
            
            # Get recent news about the topic
            news_results = await self.tavily.get_news(
                topic=topic,
                days=30,
                max_results=5
            )
            
            # Combine results
            combined_results = {
                "topic": topic,
                "search_results": results,
                "news_results": news_results,
                "timestamp": datetime.now().isoformat(),
                "context": {
                    "organization": organization_name,
                    "industry": industry
                }
            }
            
            # Synthesize findings
            synthesis = await self._synthesize_research({
                "sources": {
                    "web_search": results,
                    "recent_news": news_results
                }
            })
            
            combined_results["synthesis"] = synthesis
            
            return combined_results
            
        except Exception as e:
            logger.error(f"Error researching topic {topic}: {e}")
            return {
                "error": str(e),
                "topic": topic
            }


# MCP Server Integration (if using MCP protocol)
class MCPIntegration:
    """
    Integration with MCP servers for Tavily and RAGFlow
    """
    
    def __init__(self):
        self.mcp_enabled = os.getenv('MCP_ENABLED', 'false').lower() == 'true'
        self.mcp_tavily_url = os.getenv('MCP_TAVILY_SERVER_URL')
        self.mcp_ragflow_url = os.getenv('MCP_RAGFLOW_SERVER_URL')
        
    async def call_mcp_tool(
        self,
        server_url: str,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call MCP server tool
        """
        if not self.mcp_enabled:
            return {"error": "MCP not enabled"}
        
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": parameters
                },
                "id": 1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    server_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("result", {})
                    else:
                        return {"error": f"MCP call failed: {response.status}"}
                        
        except Exception as e:
            logger.error(f"MCP call error: {e}")
            return {"error": str(e)}