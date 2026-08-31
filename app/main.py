from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db, engine
from app import models
from app.schemas import (
    PostCreate, PostResponse, PostIngestResponse,
    VariantResponse, VariantGenerateResponse,
    ValidationRequest, ValidationResponse
)
from app.service import PostService, VariantService
from app.generators import PlatformGenerator
from app.validators import ConstraintValidator
from app.publisher_factory import PublisherFactory, get_publisher
from app.discord_publisher import DiscordPublisher
from app.mock_publishers import MockXPublisher, MockLinkedInPublisher, MockDiscordPublisher
import os
from typing import List, Optional
from datetime import datetime

print("Starting Social Media Studio API...")
print("Creating tables if they don't exist...")
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Social Media Studio API",
    description="Transform one blog post into a full social campaign",
    version="1.0.0"
)

# ===== Module 1 & 2: Basic Endpoints =====

@app.get("/")
async def root():
    return {"message": "Social Media Studio API is running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Social Media Studio API",
        "database": "SQLite"
    }

@app.get("/db-test")
async def test_db(db: Session = Depends(get_db)):
    try:
        result = db.execute("SELECT sqlite_version()")
        version = result.scalar()
        return {
            "status": "success",
            "message": "Database connection successful",
            "database_type": "SQLite",
            "version": version
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/tables")
async def list_tables(db: Session = Depends(get_db)):
    try:
        result = db.execute("""
            SELECT name 
            FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name
        """)
        tables = [row[0] for row in result.fetchall()]
        return {
            "status": "success",
            "tables": tables
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# ===== Module 3: Blog Post Ingestion =====

@app.post("/posts/ingest", response_model=PostIngestResponse)
async def ingest_post(post_data: PostCreate, db: Session = Depends(get_db)):
    try:
        db_post, source_type = PostService.create_post(db, post_data)
        post_response = PostResponse.model_validate(db_post)
        return PostIngestResponse(
            status="success",
            message="Post ingested successfully",
            post=post_response,
            source_type=source_type
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/posts", response_model=List[PostResponse])
async def list_posts(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    posts = db.query(models.Post).offset(skip).limit(limit).all()
    return [PostResponse.model_validate(post) for post in posts]

@app.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return PostResponse.model_validate(post)

@app.delete("/posts/{post_id}")
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()
    return {"status": "success", "message": f"Post {post_id} deleted successfully"}

# ===== Module 4: Variant Generation =====

@app.post("/posts/{post_id}/variants/generate", response_model=VariantGenerateResponse)
async def generate_variants(
    post_id: int, 
    platforms: Optional[List[str]] = None,
    validate: bool = True,
    db: Session = Depends(get_db)
):
    try:
        if platforms:
            valid_platforms = ["twitter", "linkedin", "discord"]
            for p in platforms:
                if p not in valid_platforms:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid platform: {p}. Must be one of {valid_platforms}"
                    )
        
        variants, validation_results = VariantService.generate_variants_for_post(
            db, post_id, platforms, validate
        )
        variant_responses = [VariantResponse.model_validate(v) for v in variants]
        platforms_generated = [v.platform for v in variants]
        
        return VariantGenerateResponse(
            status="success",
            message=f"Generated {len(variants)} variants for post {post_id}",
            variants=variant_responses,
            platforms_generated=platforms_generated,
            validation_results=validation_results if validate else None
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/posts/{post_id}/variants", response_model=List[VariantResponse])
async def get_variants(post_id: int, db: Session = Depends(get_db)):
    variants = VariantService.get_variants_for_post(db, post_id)
    return [VariantResponse.model_validate(v) for v in variants]

@app.get("/variants/{variant_id}", response_model=VariantResponse)
async def get_variant(variant_id: int, db: Session = Depends(get_db)):
    try:
        variant = VariantService.get_variant(db, variant_id)
        return VariantResponse.model_validate(variant)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/variants/{variant_id}")
async def delete_variant(variant_id: int, db: Session = Depends(get_db)):
    try:
        VariantService.delete_variant(db, variant_id)
        return {"status": "success", "message": f"Variant {variant_id} deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/platforms/constraints")
async def get_platform_constraints():
    constraints = PlatformGenerator.CONSTRAINTS
    return {
        "status": "success",
        "constraints": constraints
    }

# ===== Module 5: Constraint Validation =====

@app.post("/validate", response_model=ValidationResponse)
async def validate_content(request: ValidationRequest):
    result = ConstraintValidator.validate_variant(
        request.platform, request.content, request.hashtags
    )
    
    return ValidationResponse(
        valid=result["valid"],
        errors=result["errors"],
        warnings=result["warnings"],
        details=result["details"],
        constraints=result["constraints"]
    )

@app.get("/validate/variant/{variant_id}")
async def validate_existing_variant(variant_id: int, db: Session = Depends(get_db)):
    try:
        variant = VariantService.get_variant(db, variant_id)
        result = ConstraintValidator.validate_variant(
            variant.platform, variant.content, variant.hashtags
        )
        
        return {
            "variant_id": variant_id,
            "platform": variant.platform,
            "valid": result["valid"],
            "errors": result["errors"],
            "warnings": result["warnings"],
            "details": result["details"],
            "constraints": result["constraints"]
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/validate/post/{post_id}")
async def validate_post_variants(post_id: int, db: Session = Depends(get_db)):
    try:
        variants = VariantService.get_variants_for_post(db, post_id)
        if not variants:
            raise HTTPException(status_code=404, detail=f"No variants found for post {post_id}")
        
        results = {}
        all_valid = True
        
        for variant in variants:
            result = ConstraintValidator.validate_variant(
                variant.platform, variant.content, variant.hashtags
            )
            results[variant.platform] = {
                "variant_id": variant.id,
                "valid": result["valid"],
                "errors": result["errors"],
                "warnings": result["warnings"]
            }
            if not result["valid"]:
                all_valid = False
        
        return {
            "post_id": post_id,
            "all_valid": all_valid,
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/constraints/summary")
async def get_constraints_summary():
    summary = ConstraintValidator.get_constraints_summary()
    return {
        "status": "success",
        "constraints": summary
    }

# ===== Module 6: Review Workflow =====

@app.post("/variants/{variant_id}/approve")
async def approve_variant(variant_id: int, db: Session = Depends(get_db)):
    try:
        variant = VariantService.approve_variant(db, variant_id)
        return {
            "status": "success",
            "message": f"Variant {variant_id} approved",
            "variant": VariantResponse.model_validate(variant)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/variants/{variant_id}/reject")
async def reject_variant(
    variant_id: int, 
    reason: Optional[str] = Query(None, description="Reason for rejection"),
    db: Session = Depends(get_db)
):
    try:
        variant = VariantService.reject_variant(db, variant_id, reason)
        return {
            "status": "success",
            "message": f"Variant {variant_id} rejected",
            "reason": reason,
            "variant": VariantResponse.model_validate(variant)
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/variants/{variant_id}/edit")
async def edit_variant(
    variant_id: int,
    content: str,
    hashtags: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        variant = VariantService.edit_variant(db, variant_id, content, hashtags)
        return {
            "status": "success",
            "message": f"Variant {variant_id} edited",
            "variant": VariantResponse.model_validate(variant)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/variants/review/stats")
async def get_review_stats(db: Session = Depends(get_db)):
    stats = VariantService.get_review_stats(db)
    return {
        "status": "success",
        "stats": stats
    }

@app.post("/variants/{variant_id}/schedule")
async def schedule_variant(
    variant_id: int,
    scheduled_time: str,
    db: Session = Depends(get_db)
):
    try:
        try:
            scheduled_dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail="Invalid datetime format. Use ISO format (e.g., 2024-12-31T15:00:00)"
            )
        
        variant = VariantService.schedule_variant(db, variant_id, scheduled_dt)
        return {
            "status": "success",
            "message": f"Variant {variant_id} scheduled for {scheduled_time}",
            "variant": VariantResponse.model_validate(variant)
        }
    except ValueError as e:
        if "must be approved" in str(e):
            raise HTTPException(status_code=403, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/variants/{variant_id}/can-schedule")
async def check_can_schedule(variant_id: int, db: Session = Depends(get_db)):
    try:
        can_schedule, message = VariantService.can_schedule_variant(db, variant_id)
        return {
            "variant_id": variant_id,
            "can_schedule": can_schedule,
            "message": message
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ===== Module 7: Publisher Adapter Architecture =====

@app.post("/publish/{variant_id}")
async def publish_variant(
    variant_id: int,
    publisher_name: str = Query("mock_x", description="Publisher to use (mock_x, mock_linkedin, mock_discord, discord)"),
    db: Session = Depends(get_db)
):
    """Publish a variant using the specified publisher"""
    try:
        # Get the variant
        variant = VariantService.get_variant(db, variant_id)
        
        # Check if variant is approved
        if variant.status != "approved":
            raise HTTPException(
                status_code=403,
                detail=f"Cannot publish variant: status is {variant.status}, must be approved"
            )
        
        # Get the publisher
        publisher = get_publisher(publisher_name)
        if not publisher:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown publisher: {publisher_name}. Available: {PublisherFactory.get_publisher_names()}"
            )
        
        # Validate publisher configuration
        if not publisher.validate_config():
            raise HTTPException(
                status_code=400,
                detail=f"Publisher {publisher_name} is not properly configured"
            )
        
        # Prepare content
        content = variant.content
        if variant.hashtags:
            content = f"{content}\n\n{variant.hashtags}"
        
        # Publish
        result = publisher.publish(content, variant.platform)
        
        if result["success"]:
            # Update variant status to published
            variant.status = "published"
            variant.published_at = datetime.now()
            db.commit()
            db.refresh(variant)
        
        return {
            "status": "success" if result["success"] else "error",
            "message": result["message"],
            "publisher": publisher_name,
            "variant_id": variant_id,
            "platform": variant.platform,
            "result": result
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Publish error: {str(e)}")

@app.get("/publishers")
async def list_publishers():
    """List all available publishers and their status"""
    available = PublisherFactory.get_available_publishers()
    names = PublisherFactory.get_publisher_names()
    
    return {
        "status": "success",
        "publishers": names,
        "statuses": available
    }

@app.post("/publishers/{publisher_name}/configure")
async def configure_publisher(
    publisher_name: str,
    config: dict,
    db: Session = Depends(get_db)
):
    """Configure a publisher (e.g., set webhook URL)"""
    try:
        if publisher_name == "discord":
            webhook_url = config.get("webhook_url")
            if not webhook_url:
                raise HTTPException(
                    status_code=400,
                    detail="webhook_url is required for Discord publisher"
                )
            
            # Get or create publisher instance
            publisher = get_publisher("discord")
            if not publisher:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to get Discord publisher"
                )
            
            # Set webhook URL
            publisher.set_webhook_url(webhook_url)
            
            return {
                "status": "success",
                "message": f"Discord publisher configured",
                "webhook_url": webhook_url[:20] + "..." if webhook_url else "Not set"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Configuration not supported for {publisher_name} (mock publishers don't need configuration)"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")

@app.post("/publish/mock/preview")
async def preview_mock_publish(
    variant_id: int = Query(..., description="Variant ID to preview"),
    publisher_name: str = Query("mock_x", description="Mock publisher to preview"),
    db: Session = Depends(get_db)
):
    """Preview a mock publish without actually publishing"""
    try:
        variant = VariantService.get_variant(db, variant_id)
        
        publisher = get_publisher(publisher_name)
        if not publisher:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown publisher: {publisher_name}"
            )
        
        # Format content for preview
        content = variant.content
        if variant.hashtags:
            content = f"{content}\n\n{variant.hashtags}"
        
        formatted_content = publisher.format_content(content)
        
        # For mock publishers, we can show what would be published
        if hasattr(publisher, 'published_posts'):
            # Simulate a preview
            preview = {
                "variant_id": variant_id,
                "publisher": publisher_name,
                "platform": variant.platform,
                "content": formatted_content,
                "characters": len(formatted_content),
                "hashtags": variant.hashtags or "None",
                "would_be_published_at": datetime.now().isoformat(),
                "status": variant.status
            }
            
            return {
                "status": "success",
                "message": f"Preview for {publisher_name}",
                "preview": preview
            }
        else:
            return {
                "status": "success",
                "message": f"Preview for {publisher_name}",
                "content": formatted_content,
                "characters": len(formatted_content)
            }
            
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview error: {str(e)}")
