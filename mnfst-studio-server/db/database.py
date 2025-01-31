from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get environment variables with defaults
DB_USER = os.getenv("DEV_DB_USER", "admin")
DB_PASSWORD = os.getenv("DEV_DB_PASSWORD", "admin")
DB_NAME = os.getenv("DEV_DB_NAME", "mnfst_studio_dev")
DB_HOST = os.getenv("DEV_DB_HOST", "157.245.0.147")  # Remote PostgreSQL server
DB_PORT = os.getenv("DEV_DB_PORT", "5436")  # Using dev database port from docker-compose

# PostgreSQL database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
