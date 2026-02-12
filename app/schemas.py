from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class SegmentCreate(BaseModel):
    start: float
    end: float


class SegmentOut(SegmentCreate):
    id: int

    class Config:
        orm_mode = True


class VideoCreate(BaseModel):
    title: str = Field(...)
    description: Optional[str] = ""
    video_url: str = Field(...)
    duration: Optional[float] = 0.0


class VideoUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    status: Optional[str]


class VideoOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    video_url: str
    duration: float
    status: str
    created_at: datetime
    segments: List[SegmentOut] = []

    class Config:
        orm_mode = True
