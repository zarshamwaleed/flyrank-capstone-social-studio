from typing import Dict, Type, Optional
from app.publishers import SocialPublisher
from app.mock_publishers import MockXPublisher, MockLinkedInPublisher, MockDiscordPublisher
from app.discord_publisher import DiscordPublisher
import logging

logger = logging.getLogger(__name__)

class PublisherFactory:
    """Factory for creating publisher instances"""
    
    _publishers: Dict[str, Type[SocialPublisher]] = {
        "mock_x": MockXPublisher,
        "mock_linkedin": MockLinkedInPublisher,
        "mock_discord": MockDiscordPublisher,
        "discord": DiscordPublisher
    }
    
    _instances: Dict[str, SocialPublisher] = {}
    
    @classmethod
    def register_publisher(cls, name: str, publisher_class: Type[SocialPublisher]):
        """Register a new publisher type"""
        cls._publishers[name] = publisher_class
        cls._instances.pop(name, None)  # Clear cached instance
        logger.info(f"Registered publisher: {name}")
    
    @classmethod
    def get_publisher(cls, name: str) -> Optional[SocialPublisher]:
        """Get a publisher instance by name (singleton per type)"""
        if name not in cls._publishers:
            logger.error(f"Unknown publisher: {name}")
            return None
        
        # Return cached instance if available
        if name in cls._instances:
            return cls._instances[name]
        
        # Create new instance
        try:
            publisher = cls._publishers[name]()
            cls._instances[name] = publisher
            logger.info(f"Created publisher instance: {name}")
            return publisher
        except Exception as e:
            logger.error(f"Failed to create publisher {name}: {str(e)}")
            return None
    
    @classmethod
    def get_available_publishers(cls) -> Dict[str, bool]:
        """Get all registered publishers and their configuration status"""
        available = {}
        for name in cls._publishers.keys():
            publisher = cls.get_publisher(name)
            if publisher:
                available[name] = publisher.validate_config()
            else:
                available[name] = False
        return available
    
    @classmethod
    def get_publisher_names(cls) -> list:
        """Get list of all registered publisher names"""
        return list(cls._publishers.keys())
    
    @classmethod
    def clear_instances(cls):
        """Clear all cached instances (useful for testing)"""
        cls._instances.clear()
        logger.info("Cleared all publisher instances")

# Create a convenience function for getting publishers
def get_publisher(name: str) -> Optional[SocialPublisher]:
    """Convenience function to get a publisher"""
    return PublisherFactory.get_publisher(name)
