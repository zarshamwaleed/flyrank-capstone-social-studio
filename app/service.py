from sqlalchemy.orm import Session
from app.models import Post, Variant
from app.generators import PlatformGenerator
from app.validators import ConstraintValidator
from typing import List, Dict, Optional, Tuple
import requests
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PostService:
    """Service for handling blog posts"""
    
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
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', html_content)
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
    def create_post(db: Session, post_data):
        """Create a new post in the database"""
        source_type = "url" if post_data.source_url else "text"
        
        if post_data.source_url and not post_data.content:
            try:
                fetched_data = PostService.fetch_post_from_url(str(post_data.source_url))
                post_data.title = fetched_data.get("title", post_data.title)
                post_data.content = fetched_data.get("content", post_data.content)
                source_type = "url"
            except ValueError as e:
                raise ValueError(f"Could not fetch from URL: {str(e)}")
        
        if not post_data.content:
            raise ValueError("Post content is required")
        
        db_post = Post(
            title=post_data.title,
            content=post_data.content,
            source_url=str(post_data.source_url) if post_data.source_url else None
        )
        
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        
        return db_post, source_type


class VariantService:
    """Service for handling variants with review workflow and scheduling"""
    
    @staticmethod
    def generate_variants_for_post(db: Session, post_id: int, platforms: List[str] = None, validate: bool = True) -> Tuple[List[Variant], Dict]:
        """Generate variants for a post on specified platforms with optional validation"""
        
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise ValueError(f"Post with id {post_id} not found")
        
        if not platforms:
            platforms = ["twitter", "linkedin", "discord"]
        
        generated_variants = []
        validation_results = {}
        all_valid = True
        
        for platform in platforms:
            existing = db.query(Variant).filter(
                Variant.post_id == post_id,
                Variant.platform == platform
            ).first()
            
            if existing:
                logger.info(f"Variant for platform {platform} already exists for post {post_id}")
                generated_variants.append(existing)
                if validate:
                    result = ConstraintValidator.validate_variant(
                        platform, existing.content, existing.hashtags
                    )
                    validation_results[platform] = result
                    if not result["valid"]:
                        all_valid = False
                continue
            
            variant_data = PlatformGenerator.generate_variant(platform, post.title or "Untitled", post.content)
            
            if not variant_data:
                logger.warning(f"Could not generate variant for platform {platform}")
                continue
            
            if validate:
                result = ConstraintValidator.validate_variant(
                    platform, 
                    variant_data.get("content", ""), 
                    variant_data.get("hashtags", "")
                )
                validation_results[platform] = result
                if not result["valid"]:
                    all_valid = False
                    logger.warning(f"Variant for {platform} failed validation: {result['errors']}")
            
            db_variant = Variant(
                post_id=post_id,
                platform=platform,
                content=variant_data.get("content", ""),
                status="draft",
                hashtags=variant_data.get("hashtags", "")
            )
            
            db.add(db_variant)
            db.commit()
            db.refresh(db_variant)
            
            generated_variants.append(db_variant)
            logger.info(f"Generated variant for platform {platform} on post {post_id}")
        
        return generated_variants, {
            "all_valid": all_valid,
            "results": validation_results
        }
    
    @staticmethod
    def get_variants_for_post(db: Session, post_id: int) -> List[Variant]:
        """Get all variants for a post"""
        return db.query(Variant).filter(Variant.post_id == post_id).all()
    
    @staticmethod
    def get_variant(db: Session, variant_id: int) -> Variant:
        """Get a specific variant by ID"""
        variant = db.query(Variant).filter(Variant.id == variant_id).first()
        if not variant:
            raise ValueError(f"Variant with id {variant_id} not found")
        return variant
    
    @staticmethod
    def update_variant_status(db: Session, variant_id: int, status: str) -> Variant:
        """Update a variant's status"""
        variant = VariantService.get_variant(db, variant_id)
        variant.status = status
        db.commit()
        db.refresh(variant)
        return variant
    
    @staticmethod
    def update_variant_content(db: Session, variant_id: int, content: str) -> Variant:
        """Update a variant's content with validation"""
        variant = VariantService.get_variant(db, variant_id)
        
        result = ConstraintValidator.validate_variant(
            variant.platform, content, variant.hashtags
        )
        
        if not result["valid"]:
            raise ValueError(f"Content validation failed: {', '.join(result['errors'])}")
        
        variant.content = content
        db.commit()
        db.refresh(variant)
        return variant
    
    @staticmethod
    def delete_variant(db: Session, variant_id: int) -> bool:
        """Delete a variant"""
        variant = VariantService.get_variant(db, variant_id)
        db.delete(variant)
        db.commit()
        return True
    
    @staticmethod
    def get_platform_constraints() -> Dict:
        """Get platform constraints"""
        return PlatformGenerator.CONSTRAINTS
    
    @staticmethod
    def validate_variant_content(platform: str, content: str, hashtags: Optional[str] = None) -> Dict:
        """Validate variant content against platform constraints"""
        return ConstraintValidator.validate_variant(platform, content, hashtags)
    
    # ===== Module 6: Review Workflow Methods =====
    
    @staticmethod
    def approve_variant(db: Session, variant_id: int) -> Variant:
        """Approve a variant"""
        variant = VariantService.get_variant(db, variant_id)
        
        result = ConstraintValidator.validate_variant(
            variant.platform, variant.content, variant.hashtags
        )
        
        if not result["valid"]:
            raise ValueError(f"Cannot approve variant: {', '.join(result['errors'])}")
        
        variant.status = "approved"
        db.commit()
        db.refresh(variant)
        logger.info(f"Variant {variant_id} approved")
        return variant
    
    @staticmethod
    def reject_variant(db: Session, variant_id: int, reason: Optional[str] = None) -> Variant:
        """Reject a variant with optional reason"""
        variant = VariantService.get_variant(db, variant_id)
        variant.status = "rejected"
        db.commit()
        db.refresh(variant)
        logger.info(f"Variant {variant_id} rejected: {reason}")
        return variant
    
    @staticmethod
    def edit_variant(db: Session, variant_id: int, content: str, hashtags: Optional[str] = None) -> Variant:
        """Edit a variant's content and hashtags"""
        variant = VariantService.get_variant(db, variant_id)
        
        result = ConstraintValidator.validate_variant(
            variant.platform, content, hashtags or ""
        )
        
        if not result["valid"]:
            raise ValueError(f"Edit validation failed: {', '.join(result['errors'])}")
        
        variant.content = content
        if hashtags is not None:
            variant.hashtags = hashtags
        if variant.status == "rejected":
            variant.status = "draft"
        
        db.commit()
        db.refresh(variant)
        logger.info(f"Variant {variant_id} edited")
        return variant
    
    @staticmethod
    def can_schedule_variant(db: Session, variant_id: int) -> Tuple[bool, str]:
        """Check if a variant can be scheduled"""
        variant = VariantService.get_variant(db, variant_id)
        
        if variant.status != "approved":
            return False, f"Variant is {variant.status}, must be approved to schedule"
        
        return True, "Variant can be scheduled"
    
    @staticmethod
    def get_review_stats(db: Session) -> Dict:
        """Get review statistics"""
        variants = db.query(Variant).all()
        
        stats = {
            "total": len(variants),
            "draft": 0,
            "approved": 0,
            "rejected": 0,
            "published": 0,
            "by_platform": {}
        }
        
        for variant in variants:
            stats[variant.status] = stats.get(variant.status, 0) + 1
            
            if variant.platform not in stats["by_platform"]:
                stats["by_platform"][variant.platform] = {
                    "total": 0,
                    "draft": 0,
                    "approved": 0,
                    "rejected": 0,
                    "published": 0
                }
            
            stats["by_platform"][variant.platform]["total"] += 1
            stats["by_platform"][variant.platform][variant.status] = stats["by_platform"][variant.platform].get(variant.status, 0) + 1
        
        return stats
    
    # ===== Module 10: Scheduling Methods =====
    
    @staticmethod
    def schedule_variant(db: Session, variant_id: int, scheduled_time: datetime) -> Variant:
        """Schedule a variant for publishing"""
        # Check if variant can be scheduled
        can_schedule, message = VariantService.can_schedule_variant(db, variant_id)
        if not can_schedule:
            raise ValueError(message)
        
        variant = VariantService.get_variant(db, variant_id)
        variant.scheduled_for = scheduled_time
        db.commit()
        db.refresh(variant)
        logger.info(f"Variant {variant_id} scheduled for {scheduled_time}")
        return variant
    
    @staticmethod
    def get_scheduled_variants(db: Session) -> List[Variant]:
        """Get all scheduled variants"""
        return db.query(Variant).filter(Variant.scheduled_for.isnot(None)).all()
    
    @staticmethod
    def get_due_variants(db: Session) -> List[Variant]:
        """Get all variants that are due for publishing"""
        now = datetime.now()
        return db.query(Variant).filter(
            Variant.scheduled_for <= now,
            Variant.status == "approved"
        ).all()
    
    @staticmethod
    def mark_as_published(db: Session, variant_id: int) -> Variant:
        """Mark a variant as published"""
        variant = VariantService.get_variant(db, variant_id)
        variant.status = "published"
        variant.published_at = datetime.now()
        db.commit()
        db.refresh(variant)
        logger.info(f"Variant {variant_id} marked as published")
        return variant
