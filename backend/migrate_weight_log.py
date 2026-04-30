"""Create weight_logs table."""
from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS weight_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            weight_kg REAL NOT NULL,
            recorded_at TEXT NOT NULL
        )
    """))
    conn.commit()
    print("weight_logs table created.")
