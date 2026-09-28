from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from .database import check_db_connection, engine
import logging
from .models import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI(title="StockPulse - AI Inventory & Dynamic Pricing Engine")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and register routers
from .routers import products, suggestions
app.include_router(products.router)
app.include_router(suggestions.router)

@app.on_event("startup")
async def startup_event():
    """Verify database connection on startup and create tables"""
    logger.info("Attempting to connect to database...")
    if check_db_connection():
        logger.info("Database connection successful")
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    else:
        logger.warning("Database connection failed - continuing anyway")
        # We don't want to crash the whole application if DB is not available
        # This allows the health check endpoint to still work

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)