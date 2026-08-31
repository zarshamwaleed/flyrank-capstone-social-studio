from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, engine
from app import models
from app.schemas import (
    PostCreate, PostResponse, PostIngestResponse,
    VariantCreate, VariantResponse, VariantGenerateResponse,
    ConstraintInfo, ValidationRequest, ValidationResponse
)
from app.service import PostService, VariantService
from app.generators import PlatformGenerator
from app.validators import ConstraintValidator
import os
from typing import List, Optional

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
    """
    Generate variants for a post on specified platforms.
    
    - If platforms is not provided, generates for all platforms
    - Platforms: twitter, linkedin, discord
    - validate: If True, validates variants against platform constraints
    """
    try:
        # Validate platforms
        if platforms:
            valid_platforms = ["twitter", "linkedin", "discord"]
            for p in platforms:
                if p not in valid_platforms:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid platform: {p}. Must be one of {valid_platforms}"
                    )
        
        # Generate variants with validation
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
    """Get all variants for a post"""
    variants = VariantService.get_variants_for_post(db, post_id)
    return [VariantResponse.model_validate(v) for v in variants]

@app.get("/variants/{variant_id}", response_model=VariantResponse)
async def get_variant(variant_id: int, db: Session = Depends(get_db)):
    """Get a specific variant by ID"""
    try:
        variant = VariantService.get_variant(db, variant_id)
        return VariantResponse.model_validate(variant)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.patch("/variants/{variant_id}/status")
async def update_variant_status(
    variant_id: int, 
    status: str,
    db: Session = Depends(get_db)
):
    """Update a variant's status (draft, approved, rejected, published)"""
    valid_statuses = ["draft", "approved", "rejected", "published"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of {valid_statuses}"
        )
    
    try:
        variant = VariantService.update_variant_status(db, variant_id, status)
        return {
            "status": "success",
            "message": f"Variant {variant_id} status updated to {status}",
            "variant": VariantResponse.model_validate(variant)
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.patch("/variants/{variant_id}/content")
async def update_variant_content(
    variant_id: int,
    content: str,
    db: Session = Depends(get_db)
):
    """Update a variant's content with validation"""
    try:
        variant = VariantService.update_variant_content(db, variant_id, content)
        return {
            "status": "success",
            "message": f"Variant {variant_id} content updated",
            "variant": VariantResponse.model_validate(variant)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/variants/{variant_id}")
async def delete_variant(variant_id: int, db: Session = Depends(get_db)):
    """Delete a variant"""
    try:
        VariantService.delete_variant(db, variant_id)
        return {"status": "success", "message": f"Variant {variant_id} deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/platforms/constraints")
async def get_platform_constraints():
    """Get constraints for all platforms"""
    constraints = PlatformGenerator.CONSTRAINTS
    return {
        "status": "success",
        "constraints": constraints
    }

# ===== Module 5: Constraint Validation =====

@app.post("/validate", response_model=ValidationResponse)
async def validate_content(request: ValidationRequest):
    """
    Validate content against platform constraints
    
    - platform: twitter, linkedin, discord
    - content: The content to validate
    - hashtags: Optional hashtags to validate
    """
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
    """Validate an existing variant against platform constraints"""
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
    """Validate all variants for a post"""
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
    """Get a summary of all platform constraints"""
    summary = ConstraintValidator.get_constraints_summary()
    return {
        "status": "success",
        "constraints": summary
    }
