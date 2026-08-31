from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, engine
from app import models
from app.schemas import PostCreate, PostResponse, PostIngestResponse
from app.service import PostService
import os

print("Starting Social Media Studio API...")
print("Creating tables if they don't exist...")
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Social Media Studio API",
    description="Transform one blog post into a full social campaign",
    version="1.0.0"
)

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

# ===== Module 3: Blog Post Ingestion Endpoints =====

@app.post("/posts/ingest", response_model=PostIngestResponse)
async def ingest_post(post_data: PostCreate, db: Session = Depends(get_db)):
    """
    Ingest a blog post via URL or pasted text.
    
    - If URL is provided: fetches and extracts content
    - If text is provided: stores it directly
    """
    try:
        # Create the post
        db_post, source_type = PostService.create_post(db, post_data)
        
        # Convert to response model
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

@app.get("/posts", response_model=list[PostResponse])
async def list_posts(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """List all ingested posts"""
    posts = db.query(models.Post).offset(skip).limit(limit).all()
    return [PostResponse.model_validate(post) for post in posts]

@app.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get a specific post by ID"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return PostResponse.model_validate(post)

@app.delete("/posts/{post_id}")
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    """Delete a post by ID"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db.delete(post)
    db.commit()
    return {"status": "success", "message": f"Post {post_id} deleted successfully"}
