from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime

class PostCreate(BaseModel):
    """Schema for creating a new post"""
    title: Optional[str] = Field(None, description="Post title")
    content: Optional[str] = Field(None, description="Post content in Markdown")
    source_url: Optional[HttpUrl] = Field(None, description="URL of the original blog post")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "My Blog Post",
                "content": "# My Blog Post\n\nThis is the content of my blog post.",
                "source_url": "https://example.com/blog/my-post"
            }
        }

class PostResponse(BaseModel):
    """Schema for post response"""
    id: int
    title: Optional[str]
    content: str
    source_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class PostIngestResponse(BaseModel):
    """Schema for post ingestion response"""
    status: str
    message: str
    post: Optional[PostResponse]
    source_type: str  # 'url' or 'text'
    
    class Config:
        from_attributes = True
