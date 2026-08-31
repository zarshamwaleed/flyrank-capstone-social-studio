# ===== Module 12: Publish History =====

from app.publish_history import PublishHistoryService

@app.get("/history")
async def get_publish_history(
    variant_id: Optional[int] = Query(None, description="Filter by variant ID"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    status: Optional[str] = Query(None, description="Filter by status (success, failed, processing, duplicate_blocked)"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    limit: int = Query(100, description="Results per page", ge=1, le=1000),
    offset: int = Query(0, description="Offset for pagination", ge=0),
    db: Session = Depends(get_db)
):
    \"\"\"Get publish history with filters\"\"\"
    try:
        # Parse dates if provided
        start_dt = None
        end_dt = None
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use ISO format.")
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use ISO format.")
        
        # Get history
        result = PublishHistoryService.get_attempts_with_filters(
            db,
            variant_id=variant_id,
            platform=platform,
            status=status,
            start_date=start_dt,
            end_date=end_dt,
            limit=limit,
            offset=offset
        )
        
        return {
            "status": "success",
            "total": result["total"],
            "limit": result["limit"],
            "offset": result["offset"],
            "attempts": [
                PublishHistoryService.format_attempt_response(a)
                for a in result["attempts"]
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")

@app.get("/history/stats")
async def get_history_stats(db: Session = Depends(get_db)):
    \"\"\"Get publish history statistics\"\"\"
    try:
        stats = PublishHistoryService.get_history_stats(db)
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")

@app.get("/history/timeline")
async def get_history_timeline(
    days: int = Query(30, description="Number of days to include", ge=1, le=365),
    db: Session = Depends(get_db)
):
    \"\"\"Get publish activity timeline\"\"\"
    try:
        timeline = PublishHistoryService.get_timeline(db, days)
        return {
            "status": "success",
            "timeline": timeline
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching timeline: {str(e)}")

@app.get("/history/attempt/{attempt_id}")
async def get_attempt_details(attempt_id: int, db: Session = Depends(get_db)):
    \"\"\"Get detailed information about a specific publish attempt\"\"\"
    try:
        attempt_data = PublishHistoryService.get_attempt_details(db, attempt_id)
        if not attempt_data:
            raise HTTPException(status_code=404, detail=f"Attempt {attempt_id} not found")
        
        return {
            "status": "success",
            "attempt": PublishHistoryService.format_attempt_response(attempt_data)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching attempt: {str(e)}")

@app.get("/history/variant/{variant_id}")
async def get_variant_history(
    variant_id: int,
    limit: int = Query(50, description="Number of attempts to return", ge=1, le=200),
    db: Session = Depends(get_db)
):
    \"\"\"Get publish history for a specific variant\"\"\"
    try:
        attempts = PublishHistoryService.get_attempts_for_variant(db, variant_id, limit)
        
        # Get variant info
        variant = db.query(Variant).filter(Variant.id == variant_id).first()
        if not variant:
            raise HTTPException(status_code=404, detail=f"Variant {variant_id} not found")
        
        return {
            "status": "success",
            "variant_id": variant_id,
            "variant_platform": variant.platform,
            "total_attempts": len(attempts),
            "attempts": [
                {
                    "id": a.id,
                    "status": a.status,
                    "message": a.message,
                    "attempted_at": a.attempted_at.isoformat(),
                    "is_duplicate": a.is_duplicate,
                    "retry_count": a.retry_count
                }
                for a in attempts
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching variant history: {str(e)}")

@app.get("/history/platform/{platform}")
async def get_platform_history(
    platform: str,
    limit: int = Query(50, description="Number of attempts to return", ge=1, le=200),
    db: Session = Depends(get_db)
):
    \"\"\"Get publish history for a specific platform\"\"\"
    try:
        attempts = PublishHistoryService.get_attempts_for_platform(db, platform, limit)
        
        return {
            "status": "success",
            "platform": platform,
            "total_attempts": len(attempts),
            "attempts": [
                {
                    "id": a.id,
                    "variant_id": a.variant_id,
                    "status": a.status,
                    "message": a.message,
                    "attempted_at": a.attempted_at.isoformat(),
                    "is_duplicate": a.is_duplicate
                }
                for a in attempts
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching platform history: {str(e)}")

@app.get("/history/recent")
async def get_recent_history(
    days: int = Query(7, description="Number of days to look back", ge=1, le=30),
    limit: int = Query(100, description="Number of attempts to return", ge=1, le=500),
    db: Session = Depends(get_db)
):
    \"\"\"Get recent publish history\"\"\"
    try:
        attempts = PublishHistoryService.get_recent_attempts(db, days, limit)
        
        return {
            "status": "success",
            "days": days,
            "total_attempts": len(attempts),
            "attempts": [
                {
                    "id": a.id,
                    "variant_id": a.variant_id,
                    "platform": a.platform,
                    "status": a.status,
                    "message": a.message,
                    "attempted_at": a.attempted_at.isoformat(),
                    "is_duplicate": a.is_duplicate
                }
                for a in attempts
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recent history: {str(e)}")

@app.get("/history/status/{status}")
async def get_history_by_status(
    status: str,
    limit: int = Query(50, description="Number of attempts to return", ge=1, le=200),
    db: Session = Depends(get_db)
):
    \"\"\"Get publish history by status\"\"\"
    valid_statuses = ["success", "failed", "processing", "duplicate_blocked"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    try:
        attempts = PublishHistoryService.get_attempts_by_status(db, status, limit)
        
        return {
            "status": "success",
            "filter_status": status,
            "total_attempts": len(attempts),
            "attempts": [
                {
                    "id": a.id,
                    "variant_id": a.variant_id,
                    "platform": a.platform,
                    "message": a.message,
                    "attempted_at": a.attempted_at.isoformat(),
                    "retry_count": a.retry_count
                }
                for a in attempts
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history by status: {str(e)}")
