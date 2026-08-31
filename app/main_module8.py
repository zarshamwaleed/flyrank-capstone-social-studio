# ===== Module 8: Mock Publishers Testing =====

# IMPORTANT: /all/history MUST come BEFORE {publisher_name}/history

@app.get("/mock/publishers/all/history")
async def get_all_mock_publishers_history():
    """Get the history of published posts for all mock publishers"""
    publishers = ["mock_x", "mock_linkedin", "mock_discord"]
    all_history = {}
    total_posts = 0
    
    for publisher_name in publishers:
        history = PublisherFactory.get_mock_publisher_history(publisher_name)
        if history is not None:
            all_history[publisher_name] = {
                "total_posts": len(history),
                "history": history
            }
            total_posts += len(history)
        else:
            all_history[publisher_name] = {
                "total_posts": 0,
                "history": []
            }
    
    return {
        "status": "success",
        "total_posts": total_posts,
        "publishers": all_history
    }

@app.get("/mock/publishers/{publisher_name}/history")
async def get_mock_publisher_history(publisher_name: str):
    """Get the history of published posts for a mock publisher"""
    if publisher_name not in ["mock_x", "mock_linkedin", "mock_discord"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid publisher. Must be one of: mock_x, mock_linkedin, mock_discord"
        )
    
    history = PublisherFactory.get_mock_publisher_history(publisher_name)
    if history is None:
        raise HTTPException(
            status_code=404,
            detail=f"Publisher {publisher_name} not found or has no history"
        )
    
    return {
        "status": "success",
        "publisher": publisher_name,
        "total_posts": len(history),
        "history": history
    }

@app.delete("/mock/publishers/{publisher_name}/history")
async def clear_mock_publisher_history(publisher_name: str):
    """Clear the history of published posts for a mock publisher"""
    if publisher_name not in ["mock_x", "mock_linkedin", "mock_discord"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid publisher. Must be one of: mock_x, mock_linkedin, mock_discord"
        )
    
    count = PublisherFactory.clear_mock_publisher_history(publisher_name)
    if count is None:
        raise HTTPException(
            status_code=404,
            detail=f"Publisher {publisher_name} not found"
        )
    
    return {
        "status": "success",
        "message": f"Cleared {count} posts from {publisher_name} history",
        "cleared_count": count
    }

@app.get("/mock/publishers/{publisher_name}/stats")
async def get_mock_publisher_stats(publisher_name: str):
    """Get statistics for a mock publisher"""
    if publisher_name not in ["mock_x", "mock_linkedin", "mock_discord"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid publisher. Must be one of: mock_x, mock_linkedin, mock_discord"
        )
    
    stats = PublisherFactory.get_mock_publisher_stats(publisher_name)
    if stats is None:
        raise HTTPException(
            status_code=404,
            detail=f"Publisher {publisher_name} not found"
        )
    
    return {
        "status": "success",
        "stats": stats
    }
