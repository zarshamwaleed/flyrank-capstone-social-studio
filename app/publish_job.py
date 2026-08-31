from app.service import VariantService
from app.publisher_factory import get_publisher
from app.idempotency import IdempotencyService
from app.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

def publish_scheduled_variant(variant_id: int, publisher_name: str = "discord"):
    """
    Job to publish a scheduled variant with idempotency
    
    This function is called by APScheduler to publish a variant
    at its scheduled time. It uses idempotency to prevent duplicate
    publishes.
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting scheduled publish for variant {variant_id}")
        
        # Check if variant already published
        if IdempotencyService.check_duplicate_publish(db, variant_id):
            logger.info(f"Variant {variant_id} already published, skipping")
            return
        
        # Get the variant
        variant = VariantService.get_variant(db, variant_id)
        
        # Check if variant is approved and scheduled
        if variant.status != "approved":
            logger.warning(f"Variant {variant_id} is not approved (status: {variant.status})")
            return
        
        if not variant.scheduled_for:
            logger.warning(f"Variant {variant_id} has no scheduled time")
            return
        
        # Generate idempotency key
        idempotency_key = IdempotencyService.generate_idempotency_key(
            variant_id, publisher_name, variant.scheduled_for
        )
        
        # Check and create attempt
        attempt, is_new = IdempotencyService.check_and_create_attempt(
            db, variant_id, "discord", idempotency_key, "processing"
        )
        
        if not is_new:
            # This is a duplicate attempt
            logger.info(f"Duplicate publish attempt for variant {variant_id}, status: {attempt.status}")
            
            if attempt.status == "success":
                # Already published successfully
                logger.info(f"Variant {variant_id} already published successfully")
                return
            elif attempt.status == "processing":
                # Currently being processed, wait
                logger.info(f"Variant {variant_id} is currently being processed")
                return
            else:
                # Failed or other status, we can retry
                logger.info(f"Retrying previous failed attempt for variant {variant_id}")
        
        # Get publisher
        publisher = get_publisher(publisher_name)
        if not publisher:
            error_msg = f"Publisher {publisher_name} not found"
            logger.error(error_msg)
            IdempotencyService.update_attempt(
                db, idempotency_key, "failed", error_msg
            )
            return
        
        # Prepare content
        content = variant.content
        if variant.hashtags:
            content = f"{content}\n\n{variant.hashtags}"
        
        # Publish
        result = publisher.publish(content, variant.platform)
        
        if result["success"]:
            # Mark as published
            VariantService.mark_as_published(db, variant_id)
            
            # Update attempt
            IdempotencyService.update_attempt(
                db, 
                idempotency_key, 
                "success", 
                result["message"],
                result.get("external_id")
            )
            
            logger.info(f"Successfully published variant {variant_id} to {publisher_name}")
        else:
            # Update attempt as failed
            IdempotencyService.update_attempt(
                db, 
                idempotency_key, 
                "failed", 
                result["message"]
            )
            logger.error(f"Failed to publish variant {variant_id}: {result['message']}")
            
    except Exception as e:
        logger.error(f"Error publishing variant {variant_id}: {str(e)}")
        try:
            # Attempt to update the attempt status
            if 'idempotency_key' in locals():
                IdempotencyService.update_attempt(
                    db, idempotency_key, "failed", str(e)
                )
        except:
            pass
    finally:
        db.close()
