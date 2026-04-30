"""Create meal_ratings table."""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "longevity.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS meal_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    recipe_id INTEGER NOT NULL REFERENCES recipes(id),
    rating INTEGER NOT NULL,
    rated_at TEXT NOT NULL
)
""")

conn.commit()
conn.close()
print("meal_ratings table created.")
