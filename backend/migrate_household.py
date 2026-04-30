"""Add households table and household_id to users table."""
from database import engine, SessionLocal
from sqlalchemy import text

db = SessionLocal()

# Create households table if not exists
db.execute(text("""
    CREATE TABLE IF NOT EXISTS households (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invite_code VARCHAR UNIQUE NOT NULL,
        created_at VARCHAR
    )
"""))

# Add household_id column to users if not exists
try:
    db.execute(text("ALTER TABLE users ADD COLUMN household_id INTEGER REFERENCES households(id)"))
    print("Added household_id column to users table")
except Exception as e:
    if "duplicate column" in str(e).lower():
        print("household_id column already exists")
    else:
        print(f"Note: {e}")

db.commit()
db.close()
print("Migration complete!")
