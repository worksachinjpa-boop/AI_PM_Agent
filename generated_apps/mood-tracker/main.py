from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import auth, api
import os

app = FastAPI(title="Mood Tracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(api.router, prefix="/api", tags=["api"])

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}
