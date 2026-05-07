from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
import os

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"

class UserCreate(BaseModel):
    email: str
    name: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

def create_token(user_id: str):
    expire = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode({"sub": user_id, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = pwd_context.hash(user.password)
    db_user = User(email=user.email, name=user.name, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    return {"token": create_token(db_user.id), "user": {"id": db_user.id, "email": db_user.email}}

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": create_token(db_user.id), "user": {"id": db_user.id, "email": db_user.email}}
