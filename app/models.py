from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    source_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    variants = relationship("Variant", back_populates="post", cascade="all, delete-orphan")

class Variant(Base):
    __tablename__ = "variants"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    platform = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(50), default="draft")
    hashtags = Column(String(500), nullable=True)
    scheduled_for = Column(DateTime(timezone=True), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    post = relationship("Post", back_populates="variants")
    publish_attempts = relationship("PublishAttempt", back_populates="variant", cascade="all, delete-orphan")

class PublishAttempt(Base):
    __tablename__ = "publish_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    variant_id = Column(Integer, ForeignKey("variants.id"), nullable=False)
    platform = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)  # success, failed, retry, duplicate_blocked
    message = Column(Text, nullable=True)
    external_id = Column(String(255), nullable=True)
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())
    idempotency_key = Column(String(255), nullable=False, unique=True)
    retry_count = Column(Integer, default=0)
    is_duplicate = Column(Boolean, default=False)
    
    variant = relationship("Variant", back_populates="publish_attempts")
    
    __table_args__ = (
        Index('idx_publish_attempts_idempotency_key', 'idempotency_key'),
        Index('idx_publish_attempts_variant_id', 'variant_id'),
    )
