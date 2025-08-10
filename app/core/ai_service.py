"""
AI Service module for Gemini AI integration
"""
import os
import logging
from typing import Optional
import google.generativeai as genai

logger = logging.getLogger(__name__)


class GeminiAI:
    """
    Gemini AI service for content generation and analysis
    """
    
    def __init__(self):
        """Initialize Gemini AI with API key"""
        self.api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_AI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key not configured")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("GeminiAI service initialized")
    
    async def generate_content(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate content using Gemini AI
        
        Args:
            prompt: The prompt to send to the AI
            temperature: Temperature for generation (0.0-1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated content as string
        """
        try:
            # Configure generation settings
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens or 2000,
            )
            
            # Generate content
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Return the generated text
            if response and response.text:
                return response.text
            else:
                logger.error("Empty response from Gemini AI")
                return ""
                
        except Exception as e:
            logger.error(f"Error generating content with Gemini: {e}")
            raise
    
    def generate_content_sync(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Synchronous version of generate_content for use in sync contexts
        
        Args:
            prompt: The prompt to send to the AI
            temperature: Temperature for generation (0.0-1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated content as string
        """
        try:
            # Configure generation settings
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens or 2000,
            )
            
            # Generate content
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Return the generated text
            if response and response.text:
                return response.text
            else:
                logger.error("Empty response from Gemini AI")
                return ""
                
        except Exception as e:
            logger.error(f"Error generating content with Gemini: {e}")
            raise