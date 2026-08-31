from app.publishers import SocialPublisher
from typing import Dict, Any, Optional
import logging
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
logger = logging.getLogger(__name__)

class DiscordPublisher(SocialPublisher):
    """Real Discord publisher using webhooks"""
    
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        self.platform_name = "discord"
        self._configured = bool(self.webhook_url)
    
    def validate_config(self) -> bool:
        """Validate that Discord webhook URL is configured"""
        if not self._configured:
            logger.warning("Discord webhook URL not configured")
            return False
        return True
    
    def get_platform_name(self) -> str:
        return self.platform_name
    
    def format_content(self, content: str, **kwargs) -> str:
        """Format content for Discord with markdown support"""
        # Discord supports markdown, but we need to ensure it's not too long
        if len(content) > 2000:
            logger.warning(f"Discord content exceeds 2000 characters ({len(content)})")
        return content
    
    def publish(self, content: str, platform: str = "discord", **kwargs) -> Dict[str, Any]:
        """Publish to Discord using webhook"""
        if not self._configured:
            return {
                "success": False,
                "message": "Discord webhook URL not configured",
                "external_id": None,
                "published_at": datetime.now().isoformat()
            }
        
        try:
            # Prepare the payload
            payload = {
                "content": content,
                "username": kwargs.get("username", "Social Media Studio"),
                "avatar_url": kwargs.get("avatar_url", None)
            }
            
            # Remove None values
            payload = {k: v for k, v in payload.items() if v is not None}
            
            # Send to Discord
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 204:
                # Discord returns 204 No Content for successful webhook
                logger.info("Discord post published successfully")
                return {
                    "success": True,
                    "message": "Post published to Discord successfully",
                    "external_id": None,  # Discord webhooks don't return an ID
                    "published_at": datetime.now().isoformat(),
                    "data": {
                        "status_code": response.status_code,
                        "characters": len(content)
                    }
                }
            else:
                error_msg = f"Discord webhook returned {response.status_code}: {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "message": error_msg,
                    "external_id": None,
                    "published_at": datetime.now().isoformat(),
                    "data": {
                        "status_code": response.status_code,
                        "response": response.text
                    }
                }
                
        except requests.RequestException as e:
            error_msg = f"Failed to publish to Discord: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "external_id": None,
                "published_at": datetime.now().isoformat()
            }
        except Exception as e:
            error_msg = f"Unexpected error publishing to Discord: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "external_id": None,
                "published_at": datetime.now().isoformat()
            }
    
    def set_webhook_url(self, webhook_url: str):
        """Set the Discord webhook URL"""
        self.webhook_url = webhook_url
        self._configured = bool(webhook_url)
        logger.info(f"Discord webhook URL set: {'Configured' if self._configured else 'Not configured'}")
