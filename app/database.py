import os

from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

# Project ke root folder mein rakhi .env file load karega.
load_dotenv()


# ============================================================
# DATABASE SETTINGS
# ============================================================

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")


# ============================================================
# CHECK REQUIRED DATABASE SETTINGS
# ============================================================

# ============================================================
# DATABASE URL
# ============================================================

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
    elif DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

else:
    if not DB_USER:
        raise RuntimeError("DB_USER or DATABASE_URL is missing in environment")
    if not DB_PASSWORD:
        raise RuntimeError("DB_PASSWORD is missing in environment")
    if not DB_NAME:
        raise RuntimeError("DB_NAME is missing in environment")

    DATABASE_URL = (
        f"postgresql+pg8000://"
        f"{DB_USER}:{DB_PASSWORD}@"
        f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )



# ============================================================
# SQLALCHEMY ENGINE
# ============================================================

engine = create_engine(
    DATABASE_URL
)


# ============================================================
# DATABASE SESSION
# ============================================================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


# ============================================================
# BASE MODEL
# ============================================================

class Base(DeclarativeBase):
    pass


# ============================================================
# DATABASE DEPENDENCY
# ============================================================

def get_db():
    """
    Har API request ke liye database session provide karta hai.

    Request complete hone ke baad session automatically close
    ho jayega.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()