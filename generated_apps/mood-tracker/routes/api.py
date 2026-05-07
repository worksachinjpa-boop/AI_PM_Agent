from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, MoodCheckin
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

router = APIRouter()

class CheckinCreate(BaseModel):
    score: int
    note: Optional[str] = None

@router.post("/checkins")
def create_checkin(checkin: CheckinCreate, db: Session = Depends(get_db)):
    if not 1 <= checkin.score <= 5:
        raise HTTPException(status_code=400, detail="Score must be between 1 and 5")
    db_checkin = MoodCheckin(user_id="current-user", score=checkin.score, note=checkin.note)
    db.add(db_checkin)
    db.commit()
    return {"id": db_checkin.id, "score": db_checkin.score, "created_at": str(db_checkin.created_at)}

@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    checkins = db.query(MoodCheckin).all()
    if not checkins:
        return {"team_average": 0, "total_checkins": 0, "members": []}
    avg = sum(c.score for c in checkins) / len(checkins)
    return {"team_average": round(avg, 1), "total_checkins": len(checkins)}

@router.get("/checkins/history")
def get_history(db: Session = Depends(get_db)):
    checkins = db.query(MoodCheckin).order_by(MoodCheckin.created_at.desc()).limit(30).all()
    return [{"score": c.score, "note": c.note, "date": str(c.created_at.date())} for c in checkins]
