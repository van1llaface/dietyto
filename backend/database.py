"""
database.py — Connects your app to a database.

WHY DO WE NEED THIS?
--------------------
Before: recipes lived in a Python list → gone when server restarts.
Now: recipes live in a SQLite file (longevity.db) → survives restarts.

KEY CONCEPTS:
- Engine: the connection to the database (like a phone line)
- Session: a conversation with the database (you open it, do stuff, close it)
- Base: the parent class for all your database tables

SQLite is a file-based database — no server needed.
The file `longevity.db` will appear in your backend folder.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# The database URL — "sqlite:///longevity.db" means:
# - sqlite = use SQLite (file-based, no install needed)
# - longevity.db = the filename (created automatically)
DATABASE_URL = "sqlite:///longevity.db"

# Engine = the connection to the database
# connect_args is SQLite-specific (allows multiple threads)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Session = how you talk to the database
# Each request gets its own session (open → query → close)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base = parent class for all table models
class Base(DeclarativeBase):
    pass


def get_db():
    """
    Creates a database session for each request.

    This is a "dependency" — FastAPI calls it automatically
    before your endpoint runs, and closes it after.

    Think of it like:
    1. Open a notebook (session)
    2. Write/read what you need
    3. Close the notebook when done

    The `yield` keyword makes this a generator —
    everything before yield runs BEFORE the request,
    everything after yield runs AFTER the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
