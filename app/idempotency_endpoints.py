# ===== Module 11: Idempotency =====

@app.post("/publish/{variant_id}/idempotent")
async def publish_variant_idempotent(
    variant_id: int,
    publisher_name: str = Query("discord", description="Publisher to use"),
    idempotency_key: Optional[str] = Query(None, description="Optional custom idempotency key"),
    db: Session = Depends(get_db)
):
    """
    Publish a variant with idempotency protection.
    The same variant and publisher combination will only publish once.
    """
    try:
        from app.idempotency import IdempotencyService
        
        # Get the variant
        variant = VariantService.get_variant(db, variant_id)
        
        # Check if variant is approved
        if variant.status != "approved":
            raise HTTPException(
                status_code=403,
                detail=f"Cannot publish variant: status is {variant.status}, must be approved"
            )
        
        # Check if already published
        if IdempotencyService.check_duplicate_publish(db, variant_id):
            return {
                "status": "already_published",
                "message": f"Variant {variant_id} has already been published",
                "variant_id": variant_id,
                "platform": variant.platform
            }
        
        # Generate idempotency key if not provided
        if not idempotency_key:
            idempotency_key = IdempotencyService.generate_idempotency_key(
                variant_id, publisher_name
            )
        
        # Check and create attempt
        attempt, is_new = IdempotencyService.check_and_create_attempt(
            db, variant_id, variant.platform, idempotency_key, "processing"
        )
        
        if not is_new:
            # This is a duplicate
            if attempt.status == "success":
                return {
                    "status": "already_published",
                    "message": f"Variant {variant_id} already published successfully",
                    "attempt_id": attempt.id,
                    "idempotency_key": idempotency_key
                }
            elif attempt.status == "processing":
                return {
                    "status": "processing",
                    "message": f"Variant {variant_id} is currently being processed",
                    "attempt_id": attempt.id,
                    "idempotency_key": idempotency_key
                }
            else:
                # Failed attempt, we can retry
                logger.info(f"Retrying previous failed attempt for variant {variant_id}")
                attempt.status = "processing"
                db.commit()
        
        # Get publisher
        publisher = get_publisher(publisher_name)
        if not publisher:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown publisher: {publisher_name}"
            )
        
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
            # Mark as published
            variant.status = "published"
            variant.published_at = datetime.now()
            db.commit()
            db.refresh(variant)
            
            # Update attempt
            IdempotencyService.update_attempt(
                db, 
                idempotency_key, 
                "success", 
                result["message"],
                result.get("external_id")
            )
            
            return {
                "status": "success",
                "message": result["message"],
                "publisher": publisher_name,
                "variant_id": variant_id,
                "platform": variant.platform,
                "idempotency_key": idempotency_key,
                "result": result
            }
        else:
            # Update attempt as failed
            IdempotencyService.update_attempt(
                db, 
                idempotency_key, 
                "failed", 
                result["message"]
            )
            
            raise HTTPException(
                status_code=500,
                detail=f"Publish failed: {result['message']}"
            )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Publish error: {str(e)}")

@app.get("/publish/attempts/{variant_id}")
async def get_publish_attempts(variant_id: int, db: Session = Depends(get_db)):
    """Get all publish attempts for a variant"""
    from app.idempotency import IdempotencyService
    
    attempts = IdempotencyService.get_attempt_history(db, variant_id)
    return {
        "variant_id": variant_id,
        "total_attempts": len(attempts),
        "attempts": [
            {
                "id": a.id,
                "status": a.status,
                "message": a.message,
                "external_id": a.external_id,
                "attempted_at": a.attempted_at.isoformat(),
                "idempotency_key": a.idempotency_key,
                "retry_count": a.retry_count,
                "is_duplicate": a.is_duplicate
            }
            for a in attempts
        ]
    }

@app.get("/publish/attempts/check/{idempotency_key}")
async def check_publish_attempt(idempotency_key: str, db: Session = Depends(get_db)):
    """Check the status of a publish attempt by idempotency key"""
    from app.idempotency import IdempotencyService
    
    attempt = IdempotencyService.get_attempt_by_key(db, idempotency_key)
    if not attempt:
        raise HTTPException(status_code=404, detail=f"Attempt with key {idempotency_key} not found")
    
    return {
        "idempotency_key": idempotency_key,
        "variant_id": attempt.variant_id,
        "platform": attempt.platform,
        "status": attempt.status,
        "message": attempt.message,
        "external_id": attempt.external_id,
        "attempted_at": attempt.attempted_at.isoformat(),
        "retry_count": attempt.retry_count,
        "is_duplicate": attempt.is_duplicate
    }

@app.post("/publish/attempts/retry/{idempotency_key}")
async def retry_publish_attempt(
    idempotency_key: str,
    publisher_name: str = Query("discord", description="Publisher to use"),
    db: Session = Depends(get_db)
):
    """Retry a failed publish attempt"""
    from app.idempotency import IdempotencyService
    
    attempt = IdempotencyService.get_attempt_by_key(db, idempotency_key)
    if not attempt:
        raise HTTPException(status_code=404, detail=f"Attempt with key {idempotency_key} not found")
    
    if attempt.status == "success":
        raise HTTPException(status_code=400, detail="Attempt already succeeded")
    
    if attempt.status == "processing":
        raise HTTPException(status_code=400, detail="Attempt is currently being processed")
    
    # Retry the publish
    return await publish_variant_idempotent(
        attempt.variant_id, 
        publisher_name, 
        idempotency_key, 
        db
    )
