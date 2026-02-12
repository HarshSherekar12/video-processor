from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional


def create_video(db: Session, video_in: schemas.VideoCreate) -> models.Video:
    v = models.Video(
        title=video_in.title,
        description=video_in.description or "",
        video_url=video_in.video_url,
        duration=video_in.duration or 0.0,
        status="Draft",
    )
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


def get_video(db: Session, video_id: int) -> Optional[models.Video]:
    return db.query(models.Video).filter(models.Video.id == video_id).first()


def list_videos(db: Session, skip: int = 0, limit: int = 20, q: Optional[str] = None, status: Optional[str] = None) -> List[models.Video]:
    query = db.query(models.Video)
    if q:
        query = query.filter(models.Video.title.ilike(f"%{q}%"))
    if status:
        query = query.filter(models.Video.status == status)
    return query.order_by(models.Video.created_at.desc()).offset(skip).limit(limit).all()


def update_video(db: Session, video: models.Video, patch: schemas.VideoUpdate) -> models.Video:
    if patch.title is not None:
        video.title = patch.title
    if patch.description is not None:
        video.description = patch.description
    if patch.status is not None:
        video.status = patch.status
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


def create_segments(db: Session, video: models.Video, segments: List[schemas.SegmentCreate]):
    db.query(models.Segment).filter(models.Segment.video_id == video.id).delete()
    objs = []
    for s in segments:
        obj = models.Segment(video_id=video.id, start=s.start, end=s.end)
        db.add(obj)
        objs.append(obj)
    db.commit()
    for o in objs:
        db.refresh(o)
    return objs
