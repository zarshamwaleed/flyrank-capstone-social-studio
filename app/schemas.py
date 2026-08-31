from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class PlatformType(str, Enum):
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    DISCORD = "discord"
    MOCK_X = "mock_x"
    MOCK_LINKEDIN = "mock_linkedin"

class VariantStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"

# Post schemas
class PostCreate(BaseModel):
    title: Optional[str] = Field(None, description="Post title")
    content: Optional[str] = Field(None, description="Post content in Markdown")
    source_url: Optional[str] = Field(None, description="URL of the original blog post")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "My Blog Post",
                "content": "# My Blog Post\n\nThis is the content of my blog post.",
                "source_url": "https://example.com/blog/my-post"
            }
        }

class PostResponse(BaseModel):
    id: int
    title: Optional[str]
    content: str
    source_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class PostIngestResponse(BaseModel):
    status: str
    message: str
    post: Optional[PostResponse]
    source_type: str
    
    class Config:
        from_attributes = True

# Variant schemas
class VariantCreate(BaseModel):
    platform: PlatformType
    post_id: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "platform": "twitter",
                "post_id": 1
            }
        }

class VariantResponse(BaseModel):
    id: int
    post_id: int
    platform: str
    content: str
    status: str
    hashtags: Optional[str]
    scheduled_for: Optional[datetime]
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class VariantGenerateResponse(BaseModel):
    status: str
    message: str
    variants: List[VariantResponse]
    platforms_generated: List[str]
    validation_results: Optional[Dict]
    
    class Config:
        from_attributes = True

class ConstraintInfo(BaseModel):
    platform: str
    max_length: int
    max_hashtags: int
    tone: str
    description: str

# Validation schemas
class ValidationRequest(BaseModel):
    platform: str
    content: str
    hashtags: Optional[str] = None

class ValidationResponse(BaseModel):
    valid: bool
    errors: List[str]
    warnings: List[str]
    details: Dict
    constraints: Dict
