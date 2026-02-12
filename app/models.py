from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1024), default="")
    video_url = Column(String(1024), nullable=False)
    duration = Column(Float, default=0.0)
    status = Column(String(32), default="Draft")
    created_at = Column(DateTime, default=datetime.utcnow)

    segments = relationship("Segment", back_populates="video", cascade="all, delete-orphan")


class Segment(Base):
    __tablename__ = "segments"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"))
    start = Column(Float, nullable=False)
    end = Column(Float, nullable=False)

    video = relationship("Video", back_populates="segments")
