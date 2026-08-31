from app.service import VariantService
from app.publisher_factory import get_publisher
from app.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

def publish_scheduled_variant(variant_id: int, publisher_name: str = "discord"):
    """
    Job to publish a scheduled variant
    
    This function is called by APScheduler to publish a variant
    at its scheduled time.
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting scheduled publish for variant {variant_id}")
        
        # Get the variant
        variant = VariantService.get_variant(db, variant_id)
        
        # Check if variant is approved and scheduled
        if variant.status != "approved":
            logger.warning(f"Variant {variant_id} is not approved (status: {variant.status})")
            return
        
        if not variant.scheduled_for:
            logger.warning(f"Variant {variant_id} has no scheduled time")
            return
        
        # Get publisher
        publisher = get_publisher(publisher_name)
        if not publisher:
            logger.error(f"Publisher {publisher_name} not found")
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
            logger.info(f"Successfully published variant {variant_id} to {publisher_name}")
        else:
            logger.error(f"Failed to publish variant {variant_id}: {result['message']}")
            
    except Exception as e:
        logger.error(f"Error publishing variant {variant_id}: {str(e)}")
    finally:
        db.close()
