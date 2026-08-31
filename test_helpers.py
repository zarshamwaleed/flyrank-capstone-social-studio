import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:8000"

class TestHelper:
    """Helper functions for testing the Social Media Studio API"""
    
    @staticmethod
    def create_post(title: str = "Test Post", content: str = None) -> Optional[int]:
        """Create a test post"""
        if not content:
            content = """
# Test Post

This is a test post for the Social Media Studio API.

## Key Points
- Test point 1
- Test point 2
- Test point 3
            """.strip()
        
        post_data = {
            "title": title,
            "content": content
        }
        
        response = requests.post(f"{BASE_URL}/posts/ingest", json=post_data)
        if response.status_code == 200:
            return response.json()['post']['id']
        return None
    
    @staticmethod
    def create_variant(post_id: int, platform: str = "discord") -> Optional[int]:
        """Create a variant for a post"""
        response = requests.post(f"{BASE_URL}/posts/{post_id}/variants/generate")
        if response.status_code != 200:
            return None
        
        variants = response.json()['variants']
        for variant in variants:
            if variant['platform'] == platform:
                return variant['id']
        return None
    
    @staticmethod
    def approve_variant(variant_id: int) -> bool:
        """Approve a variant"""
        response = requests.post(f"{BASE_URL}/variants/{variant_id}/approve")
        return response.status_code == 200
    
    @staticmethod
    def publish_variant(variant_id: int, publisher: str = "discord") -> Dict:
        """Publish a variant"""
        response = requests.post(f"{BASE_URL}/publish/{variant_id}/idempotent?publisher_name={publisher}")
        return response.json()
    
    @staticmethod
    def get_variant_status(variant_id: int) -> Optional[str]:
        """Get variant status"""
        response = requests.get(f"{BASE_URL}/variants/{variant_id}")
        if response.status_code == 200:
            return response.json()['status']
        return None
    
    @staticmethod
    def create_and_approve_variant(title: str = "Test Post") -> Optional[int]:
        """Create a post, generate variant, and approve it"""
        post_id = TestHelper.create_post(title)
        if not post_id:
            return None
        
        variant_id = TestHelper.create_variant(post_id)
        if not variant_id:
            return None
        
        if not TestHelper.approve_variant(variant_id):
            return None
        
        return variant_id
    
    @staticmethod
    def wait_for_job_completion(variant_id: int, max_wait: int = 30) -> bool:
        """Wait for a scheduled job to complete"""
        start_time = time.time()
        while time.time() - start_time < max_wait:
            status = TestHelper.get_variant_status(variant_id)
            if status == "published":
                return True
            time.sleep(2)
        return False
