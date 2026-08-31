from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from app.models import PublishAttempt, Variant, Post
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class PublishHistoryService:
    """Service for managing and retrieving publish history"""
    
    @staticmethod
    def get_attempt_by_id(db: Session, attempt_id: int) -> Optional[PublishAttempt]:
        """Get a publish attempt by ID"""
        return db.query(PublishAttempt).filter(PublishAttempt.id == attempt_id).first()
    
    @staticmethod
    def get_attempts_for_variant(db: Session, variant_id: int, limit: int = 50) -> List[PublishAttempt]:
        """Get all publish attempts for a specific variant"""
        return db.query(PublishAttempt).filter(
            PublishAttempt.variant_id == variant_id
        ).order_by(desc(PublishAttempt.attempted_at)).limit(limit).all()
    
    @staticmethod
    def get_attempts_for_platform(db: Session, platform: str, limit: int = 50) -> List[PublishAttempt]:
        """Get all publish attempts for a specific platform"""
        return db.query(PublishAttempt).filter(
            PublishAttempt.platform == platform
        ).order_by(desc(PublishAttempt.attempted_at)).limit(limit).all()
    
    @staticmethod
    def get_recent_attempts(db: Session, days: int = 7, limit: int = 100) -> List[PublishAttempt]:
        """Get recent publish attempts within the last N days"""
        cutoff = datetime.now() - timedelta(days=days)
        return db.query(PublishAttempt).filter(
            PublishAttempt.attempted_at >= cutoff
        ).order_by(desc(PublishAttempt.attempted_at)).limit(limit).all()
    
    @staticmethod
    def get_attempts_by_status(db: Session, status: str, limit: int = 50) -> List[PublishAttempt]:
        """Get publish attempts by status"""
        return db.query(PublishAttempt).filter(
            PublishAttempt.status == status
        ).order_by(desc(PublishAttempt.attempted_at)).limit(limit).all()
    
    @staticmethod
    def get_attempts_with_filters(
        db: Session,
        variant_id: Optional[int] = None,
        platform: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get publish attempts with filters"""
        query = db.query(PublishAttempt)
        
        # Apply filters
        if variant_id:
            query = query.filter(PublishAttempt.variant_id == variant_id)
        
        if platform:
            query = query.filter(PublishAttempt.platform == platform)
        
        if status:
            query = query.filter(PublishAttempt.status == status)
        
        if start_date:
            query = query.filter(PublishAttempt.attempted_at >= start_date)
        
        if end_date:
            query = query.filter(PublishAttempt.attempted_at <= end_date)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination
        attempts = query.order_by(desc(PublishAttempt.attempted_at)).offset(offset).limit(limit).all()
        
        # Get variant info for each attempt
        results = []
        for attempt in attempts:
            variant = db.query(Variant).filter(Variant.id == attempt.variant_id).first()
            post = db.query(Post).filter(Post.id == variant.post_id).first() if variant else None
            
            results.append({
                "attempt": attempt,
                "variant": variant,
                "post": post
            })
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "attempts": results
        }
    
    @staticmethod
    def get_history_stats(db: Session) -> Dict[str, Any]:
        """Get statistics about publish history"""
        total_attempts = db.query(PublishAttempt).count()
        
        # Status counts
        status_counts = {}
        for status in ["success", "failed", "processing", "duplicate_blocked"]:
            count = db.query(PublishAttempt).filter(PublishAttempt.status == status).count()
            if count > 0:
                status_counts[status] = count
        
        # Platform counts
        platform_counts = {}
        platforms = db.query(PublishAttempt.platform).distinct().all()
        for platform in platforms:
            count = db.query(PublishAttempt).filter(PublishAttempt.platform == platform[0]).count()
            platform_counts[platform[0]] = count
        
        # Recent attempts (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        recent_count = db.query(PublishAttempt).filter(PublishAttempt.attempted_at >= yesterday).count()
        
        # Duplicate count
        duplicate_count = db.query(PublishAttempt).filter(PublishAttempt.is_duplicate == True).count()
        
        return {
            "total_attempts": total_attempts,
            "status_counts": status_counts,
            "platform_counts": platform_counts,
            "recent_24h": recent_count,
            "duplicate_blocked": duplicate_count
        }
    
    @staticmethod
    def get_timeline(db: Session, days: int = 30) -> Dict[str, Any]:
        """Get publish activity timeline"""
        cutoff = datetime.now() - timedelta(days=days)
        
        # Get daily counts
        results = db.query(
            func.date(PublishAttempt.attempted_at).label('date'),
            func.count(PublishAttempt.id).label('count')
        ).filter(
            PublishAttempt.attempted_at >= cutoff
        ).group_by(
            func.date(PublishAttempt.attempted_at)
        ).order_by(
            func.date(PublishAttempt.attempted_at)
        ).all()
        
        timeline = {
            "days": days,
            "data": [
                {
                    "date": r.date,
                    "count": r.count
                }
                for r in results
            ]
        }
        
        return timeline
    
    @staticmethod
    def get_attempt_details(db: Session, attempt_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific attempt"""
        attempt = PublishHistoryService.get_attempt_by_id(db, attempt_id)
        if not attempt:
            return None
        
        variant = db.query(Variant).filter(Variant.id == attempt.variant_id).first()
        post = db.query(Post).filter(Post.id == variant.post_id).first() if variant else None
        
        return {
            "attempt": attempt,
            "variant": variant,
            "post": post
        }
    
    @staticmethod
    def format_attempt_response(attempt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format attempt data for API response"""
        attempt = attempt_data["attempt"]
        variant = attempt_data.get("variant")
        post = attempt_data.get("post")
        
        response = {
            "id": attempt.id,
            "variant_id": attempt.variant_id,
            "platform": attempt.platform,
            "status": attempt.status,
            "message": attempt.message,
            "external_id": attempt.external_id,
            "attempted_at": attempt.attempted_at.isoformat(),
            "idempotency_key": attempt.idempotency_key,
            "retry_count": attempt.retry_count,
            "is_duplicate": attempt.is_duplicate
        }
        
        if variant:
            response["variant"] = {
                "id": variant.id,
                "platform": variant.platform,
                "content": variant.content[:200] + "..." if len(variant.content) > 200 else variant.content
            }
        
        if post:
            response["post"] = {
                "id": post.id,
                "title": post.title,
                "source_url": post.source_url
            }
        
        return response
