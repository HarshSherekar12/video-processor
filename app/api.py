from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List
from . import schemas, crud, models
from .database import SessionLocal, init_db

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.on_event("startup")
def startup():
    init_db()


@router.post("/videos", response_model=schemas.VideoOut)
def create_video(v: schemas.VideoCreate, db: Session = Depends(get_db)):
    return crud.create_video(db, v)


@router.get("/videos", response_model=List[schemas.VideoOut])
def list_videos(
    skip: int = 0,
    limit: int = 20,
    q: str = Query(None, description="search title"),
    status: str = Query(None, description="filter status"),
    db: Session = Depends(get_db),
):
    return crud.list_videos(db, skip=skip, limit=limit, q=q, status=status)


@router.get("/videos/{video_id}", response_model=schemas.VideoOut)
def get_video(video_id: int, db: Session = Depends(get_db)):
    v = crud.get_video(db, video_id)
    if not v:
        raise HTTPException(status_code=404, detail="Video not found")
    return v


@router.patch("/videos/{video_id}", response_model=schemas.VideoOut)
def patch_video(video_id: int, patch: schemas.VideoUpdate, db: Session = Depends(get_db)):
    v = crud.get_video(db, video_id)
    if not v:
        raise HTTPException(status_code=404, detail="Video not found")
    return crud.update_video(db, v, patch)


def _process_video_segments(db_session_maker, video_id: int):
    db = db_session_maker()
    try:
        v = db.query(models.Video).filter(models.Video.id == video_id).first()
        if not v:
            return
        # Simulate processing: if there are segments and times valid -> Ready else Failed
        segs = db.query(models.Segment).filter(models.Segment.video_id == video_id).all()
        if segs:
            v.status = "Ready"
        else:
            v.status = "Failed"
        db.add(v)
        db.commit()
    finally:
        db.close()


@router.post("/videos/{video_id}/split", response_model=List[schemas.SegmentOut])
def split_video(video_id: int, payload: dict, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    v = crud.get_video(db, video_id)
    if not v:
        raise HTTPException(status_code=404, detail="Video not found")
    segments_in = []
    if "segments" not in payload:
        raise HTTPException(status_code=400, detail="segments required")
    for s in payload["segments"]:
        if s.get("start") is None or s.get("end") is None:
            raise HTTPException(status_code=400, detail="start/end required for each segment")
        start = float(s["start"])
        end = float(s["end"])
        if start < 0 or end <= start or end > v.duration + 1e-6:
            raise HTTPException(status_code=400, detail=f"invalid segment {s}")
        segments_in.append(schemas.SegmentCreate(start=start, end=end))

    # mark processing
    v.status = "Processing"
    db.add(v)
    db.commit()

    created = crud.create_segments(db, v, segments_in)

    # background finalize
    background_tasks.add_task(_process_video_segments, SessionLocal, v.id)

    return created
