"""
Platform mapping and filtering utilities
"""

from typing import List, Dict, Set
from enum import Enum

class ContentType(Enum):
    BLOG = "blog"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    NEWSLETTER = "newsletter"

# Platform type mappings
PLATFORM_TYPE_MAPPING = {
    # Blog platforms
    "blog": ContentType.BLOG,
    "wordpress": ContentType.BLOG,
    "medium": ContentType.BLOG,
    "blogger": ContentType.BLOG,
    "ghost": ContentType.BLOG,
    "substack": ContentType.BLOG,
    
    # Social media platforms
    "facebook": ContentType.SOCIAL_MEDIA,
    "instagram": ContentType.SOCIAL_MEDIA,
    "twitter": ContentType.SOCIAL_MEDIA,
    "x": ContentType.SOCIAL_MEDIA,
    "linkedin": ContentType.SOCIAL_MEDIA,
    "tiktok": ContentType.SOCIAL_MEDIA,
    "youtube": ContentType.SOCIAL_MEDIA,
    "pinterest": ContentType.SOCIAL_MEDIA,
    "threads": ContentType.SOCIAL_MEDIA,
    
    # Email/Newsletter platforms
    "email": ContentType.EMAIL,
    "newsletter": ContentType.NEWSLETTER,
    "mailchimp": ContentType.EMAIL,
    "sendinblue": ContentType.EMAIL,
}

def get_platform_type(platform_name: str) -> ContentType:
    """Get the content type for a platform"""
    platform_lower = platform_name.lower().strip()
    return PLATFORM_TYPE_MAPPING.get(platform_lower, ContentType.SOCIAL_MEDIA)

def filter_platforms_by_content_type(
    platforms: List[str], 
    content_types: List[ContentType]
) -> List[str]:
    """Filter platforms by allowed content types"""
    allowed_types = set(content_types)
    return [
        platform for platform in platforms
        if get_platform_type(platform) in allowed_types
    ]

def get_platforms_for_topic_category(category: str) -> List[ContentType]:
    """Get appropriate platform types for a topic category"""
    category_lower = category.lower()
    
    if category_lower in ["blog", "article", "post"]:
        return [ContentType.BLOG]
    elif category_lower in ["social_media", "social", "sm"]:
        return [ContentType.SOCIAL_MEDIA]
    elif category_lower == "email":
        return [ContentType.EMAIL]
    elif category_lower == "newsletter":
        return [ContentType.NEWSLETTER]
    else:
        # Default: all types
        return list(ContentType)

def should_generate_for_platform(
    platform_name: str,
    topic_category: str
) -> bool:
    """Check if content should be generated for a platform based on topic category"""
    allowed_types = get_platforms_for_topic_category(topic_category)
    platform_type = get_platform_type(platform_name)
    return platform_type in allowed_types