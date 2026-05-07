from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import uuid

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="member")
    team_id = Column(String, ForeignKey("teams.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    checkins = relationship("MoodCheckin", back_populates="user")

class Team(Base):
    __tablename__ = "teams"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class MoodCheckin(Base):
    __tablename__ = "mood_checkins"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    score = Column(Integer, nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="checkins")
