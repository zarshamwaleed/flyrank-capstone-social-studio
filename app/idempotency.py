from sqlalchemy.orm import Session
from app.models import PublishAttempt, Variant
from datetime import datetime
import hashlib
import uuid
import logging

logger = logging.getLogger(__name__)

class IdempotencyService:
    """Service for handling idempotency and duplicate prevention"""
    
    @staticmethod
    def generate_idempotency_key(variant_id: int, publisher_name: str, scheduled_for: datetime = None) -> str:
        """Generate a unique idempotency key for a publish operation"""
        # Create a deterministic key based on variant_id and publisher
        base_string = f"{variant_id}:{publisher_name}"
        if scheduled_for:
            # Include scheduled time for scheduled publishes
            base_string += f":{scheduled_for.isoformat()}"
        
        # Add a random component for uniqueness
        unique_part = uuid.uuid4().hex[:8]
        combined = f"{base_string}:{unique_part}"
        
        # Hash the combined string
        return hashlib.sha256(combined.encode()).hexdigest()[:32]
    
    @staticmethod
    def check_and_create_attempt(
        db: Session, 
        variant_id: int, 
        platform: str, 
        idempotency_key: str,
        status: str = "pending",
        message: str = "Publish attempt started"
    ) -> tuple:
        """
        Check if a publish has already been attempted with this idempotency key.
        If not, create a new attempt record.
        
        Returns: (PublishAttempt, is_new)
        """
        # Check for existing attempt
        existing = db.query(PublishAttempt).filter(
            PublishAttempt.idempotency_key == idempotency_key
        ).first()
        
        if existing:
            logger.info(f"Duplicate publish attempt detected: {idempotency_key}")
            return existing, False
        
        # Create new attempt
        attempt = PublishAttempt(
            variant_id=variant_id,
            platform=platform,
            status=status,
            message=message,
            idempotency_key=idempotency_key,
            retry_count=0,
            is_duplicate=False
        )
        
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
        
        logger.info(f"Created publish attempt: {idempotency_key} for variant {variant_id}")
        return attempt, True
    
    @staticmethod
    def update_attempt(
        db: Session, 
        idempotency_key: str, 
        status: str, 
        message: str = None,
        external_id: str = None,
        is_duplicate: bool = False
    ) -> PublishAttempt:
        """Update a publish attempt"""
        attempt = db.query(PublishAttempt).filter(
            PublishAttempt.idempotency_key == idempotency_key
        ).first()
        
        if not attempt:
            raise ValueError(f"Attempt with key {idempotency_key} not found")
        
        attempt.status = status
        if message:
            attempt.message = message
        if external_id:
            attempt.external_id = external_id
        if is_duplicate:
            attempt.is_duplicate = True
        attempt.retry_count += 1
        
        db.commit()
        db.refresh(attempt)
        
        logger.info(f"Updated attempt {idempotency_key} to status {status}")
        return attempt
    
    @staticmethod
    def check_duplicate_publish(db: Session, variant_id: int) -> bool:
        """Check if a variant has already been successfully published"""
        # Check if variant status is published
        variant = db.query(Variant).filter(Variant.id == variant_id).first()
        if variant and variant.status == "published":
            return True
        
        # Check if there's a successful publish attempt
        attempt = db.query(PublishAttempt).filter(
            PublishAttempt.variant_id == variant_id,
            PublishAttempt.status == "success"
        ).first()
        
        return attempt is not None
    
    @staticmethod
    def get_attempt_history(db: Session, variant_id: int) -> list:
        """Get all publish attempts for a variant"""
        return db.query(PublishAttempt).filter(
            PublishAttempt.variant_id == variant_id
        ).order_by(PublishAttempt.attempted_at.desc()).all()
    
    @staticmethod
    def get_attempt_by_key(db: Session, idempotency_key: str) -> PublishAttempt:
        """Get a publish attempt by idempotency key"""
        return db.query(PublishAttempt).filter(
            PublishAttempt.idempotency_key == idempotency_key
        ).first()
    
    @staticmethod
    def mark_as_duplicate(db: Session, idempotency_key: str) -> PublishAttempt:
        """Mark an attempt as a duplicate"""
        attempt = db.query(PublishAttempt).filter(
            PublishAttempt.idempotency_key == idempotency_key
        ).first()
        
        if attempt:
            attempt.is_duplicate = True
            attempt.status = "duplicate_blocked"
            db.commit()
            db.refresh(attempt)
            logger.info(f"Marked attempt {idempotency_key} as duplicate")
        
        return attempt
