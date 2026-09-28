from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Database configuration from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "stockpulse")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

# Build the PostgreSQL connection URL
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine with connection pooling and pre-ping
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_pre_ping=True,
    pool_recycle=300,  # Recycle connections after 5 minutes
    echo=False  # Set to True for SQL debugging
)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a declarative base for models
Base = declarative_base()

def get_db():
    """
    FastAPI dependency that provides a database session.
    Yields a database session and ensures it's closed afterwards.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_db_connection():
    """
    Verify that the database connection is working.
    Returns True if successful, False otherwise.
    """
    try:
        # Attempt to create a connection
        db = SessionLocal()
        # Execute a simple query to test connectivity
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return False