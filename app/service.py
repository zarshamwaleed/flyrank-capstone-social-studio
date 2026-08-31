from sqlalchemy.orm import Session
from app.models import Post
from app.schemas import PostCreate
import requests
import httpx
from datetime import datetime
import re

class PostService:
    @staticmethod
    def extract_title_from_html(html_content):
        """Extract title from HTML content"""
        title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip()
        return None
    
    @staticmethod
    def extract_text_from_html(html_content):
        """Extract text from HTML content (basic extraction)"""
        # Remove script and style tags
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html_content)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    @staticmethod
    def fetch_post_from_url(url: str):
        """Fetch blog post content from a URL"""
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            # Extract title and content
            html_content = response.text
            title = PostService.extract_title_from_html(html_content)
            content = PostService.extract_text_from_html(html_content)
            
            if not content or len(content) < 10:
                raise ValueError("Could not extract meaningful content from the URL")
            
            return {
                "title": title or "Untitled Post",
                "content": content,
                "source_url": url
            }
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch URL: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error processing URL: {str(e)}")
    
    @staticmethod
    def create_post(db: Session, post_data: PostCreate):
        """Create a new post in the database"""
        # Determine source type
        source_type = "url" if post_data.source_url else "text"
        
        # If URL is provided and no content, fetch from URL
        if post_data.source_url and not post_data.content:
            try:
                fetched_data = PostService.fetch_post_from_url(str(post_data.source_url))
                post_data.title = fetched_data.get("title", post_data.title)
                post_data.content = fetched_data.get("content", post_data.content)
                source_type = "url"
            except ValueError as e:
                raise ValueError(f"Could not fetch from URL: {str(e)}")
        
        # Validate that we have content
        if not post_data.content:
            raise ValueError("Post content is required")
        
        # Create post
        db_post = Post(
            title=post_data.title,
            content=post_data.content,
            source_url=str(post_data.source_url) if post_data.source_url else None
        )
        
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        
        return db_post, source_type
