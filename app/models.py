from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class VariantStatus(str, enum.Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"

class Platform(str, enum.Enum):
    DISCORD = "discord"
    TELEGRAM = "telegram"
    MASTODON = "mastodon"
    MOCK_X = "mock_x"
    MOCK_LINKEDIN = "mock_linkedin"

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    source_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    variants = relationship("Variant", back_populates="post", cascade="all, delete-orphan")

class Variant(Base):
    __tablename__ = "variants"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    platform = Column(Enum(Platform), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(Enum(VariantStatus), default=VariantStatus.DRAFT)
    hashtags = Column(String(500), nullable=True)
    scheduled_for = Column(DateTime(timezone=True), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    post = relationship("Post", back_populates="variants")
    publish_attempts = relationship("PublishAttempt", back_populates="variant", cascade="all, delete-orphan")

class PublishAttempt(Base):
    __tablename__ = "publish_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    variant_id = Column(Integer, ForeignKey("variants.id"), nullable=False)
    platform = Column(Enum(Platform), nullable=False)
    status = Column(String(50), nullable=False)  # success, failed, retry
    message = Column(Text, nullable=True)
    external_id = Column(String(255), nullable=True)  # ID from platform
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())
    idempotency_key = Column(String(255), nullable=False, unique=True)
    
    # Relationships
    variant = relationship("Variant", back_populates="publish_attempts")
