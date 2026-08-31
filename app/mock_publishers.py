from app.publishers import SocialPublisher
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class MockXPublisher(SocialPublisher):
    """Mock publisher for Twitter/X that records posts in a local store"""
    
    def __init__(self):
        self.published_posts = []
        self.platform_name = "mock_x"
    
    def validate_config(self) -> bool:
        """Mock publisher is always configured"""
        return True
    
    def get_platform_name(self) -> str:
        return self.platform_name
    
    def publish(self, content: str, platform: str = "mock_x", **kwargs) -> Dict[str, Any]:
        """Publish to mock X by recording the post"""
        post_id = f"mock_x_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now().isoformat()
        
        # Create post record
        post_record = {
            "id": post_id,
            "content": content,
            "platform": platform,
            "published_at": timestamp,
            "type": "mock_x",
            "characters": len(content),
            "hashtags": self._extract_hashtags(content),
            "truncated": len(content) > 280,
            "status": "success"
        }
        
        self.published_posts.append(post_record)
        logger.info(f"Mock X post created: {post_id}")
        
        return {
            "success": True,
            "message": "Post published to Mock X successfully",
            "external_id": post_id,
            "published_at": timestamp,
            "data": {
                "characters": len(content),
                "hashtags": post_record["hashtags"],
                "truncated": post_record["truncated"]
            }
        }
    
    def _extract_hashtags(self, content: str) -> list:
        """Extract hashtags from content"""
        import re
        return re.findall(r'#\w+', content)
    
    def get_published_posts(self) -> list:
        """Get all published posts (for testing)"""
        return self.published_posts


class MockLinkedInPublisher(SocialPublisher):
    """Mock publisher for LinkedIn that records posts in a local store"""
    
    def __init__(self):
        self.published_posts = []
        self.platform_name = "mock_linkedin"
    
    def validate_config(self) -> bool:
        """Mock publisher is always configured"""
        return True
    
    def get_platform_name(self) -> str:
        return self.platform_name
    
    def publish(self, content: str, platform: str = "mock_linkedin", **kwargs) -> Dict[str, Any]:
        """Publish to mock LinkedIn by recording the post"""
        post_id = f"mock_li_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now().isoformat()
        
        # Create post record
        post_record = {
            "id": post_id,
            "content": content,
            "platform": platform,
            "published_at": timestamp,
            "type": "mock_linkedin",
            "characters": len(content),
            "hashtags": self._extract_hashtags(content),
            "status": "success"
        }
        
        self.published_posts.append(post_record)
        logger.info(f"Mock LinkedIn post created: {post_id}")
        
        return {
            "success": True,
            "message": "Post published to Mock LinkedIn successfully",
            "external_id": post_id,
            "published_at": timestamp,
            "data": {
                "characters": len(content),
                "hashtags": post_record["hashtags"]
            }
        }
    
    def _extract_hashtags(self, content: str) -> list:
        """Extract hashtags from content"""
        import re
        return re.findall(r'#\w+', content)
    
    def get_published_posts(self) -> list:
        """Get all published posts (for testing)"""
        return self.published_posts


class MockDiscordPublisher(SocialPublisher):
    """Mock publisher for Discord (fallback when real Discord is not available)"""
    
    def __init__(self):
        self.published_posts = []
        self.platform_name = "mock_discord"
    
    def validate_config(self) -> bool:
        """Mock publisher is always configured"""
        return True
    
    def get_platform_name(self) -> str:
        return self.platform_name
    
    def publish(self, content: str, platform: str = "mock_discord", **kwargs) -> Dict[str, Any]:
        """Publish to mock Discord by recording the post"""
        post_id = f"mock_dc_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now().isoformat()
        
        # Create post record
        post_record = {
            "id": post_id,
            "content": content,
            "platform": platform,
            "published_at": timestamp,
            "type": "mock_discord",
            "characters": len(content),
            "status": "success"
        }
        
        self.published_posts.append(post_record)
        logger.info(f"Mock Discord post created: {post_id}")
        
        return {
            "success": True,
            "message": "Post published to Mock Discord successfully",
            "external_id": post_id,
            "published_at": timestamp,
            "data": {
                "characters": len(content)
            }
        }
    
    def get_published_posts(self) -> list:
        """Get all published posts (for testing)"""
        return self.published_posts
