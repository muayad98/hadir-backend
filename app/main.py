from fastapi import FastAPI
from app.routes import business, service, bookings
from app.db import db
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Hadir API",
    description="AI-powered WhatsApp receptionist system for small businesses",
    version="1.0.0"
)

# Include routers
app.include_router(business.router, prefix="/business", tags=["business"])
app.include_router(service.router, prefix="/services", tags=["services"])
app.include_router(bookings.router, prefix="/bookings", tags=["bookings"])

@app.on_event("startup")
async def startup_db_client():
    mongodb_url = os.getenv("MONGODB_URL", "mongodb+srv://muayad:muayad123@cluster0.aqxgxmj.mongodb.net/?retryWrites=true&w=majority")
    await db.connect_db(mongodb_url)

@app.on_event("shutdown")
async def shutdown_db_client():
    await db.close_db()

@app.get("/")
async def root():
    return {"message": "Welcome to Hadir API"}
