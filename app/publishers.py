from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SocialPublisher(ABC):
    """Abstract base class for all social media publishers"""
    
    @abstractmethod
    def publish(self, content: str, platform: str, **kwargs) -> Dict[str, Any]:
        """
        Publish content to a platform
        
        Args:
            content: The content to publish
            platform: The platform name
            **kwargs: Additional platform-specific parameters
        
        Returns:
            Dict containing publish result with at least:
                - success: bool
                - message: str
                - external_id: Optional[str]
                - published_at: str
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate that the publisher is properly configured"""
        pass
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Return the name of the platform this publisher handles"""
        pass
    
    def format_content(self, content: str, **kwargs) -> str:
        """Format content for the specific platform (can be overridden)"""
        return content
    
    def log_publish_attempt(self, content: str, platform: str, result: Dict[str, Any]):
        """Log a publish attempt"""
        logger.info(f"Publish to {platform}: {result.get('message', 'No message')}")
        logger.debug(f"Content: {content[:100]}...")
