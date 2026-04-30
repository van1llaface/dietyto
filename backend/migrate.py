"""
Auto-migration script — adds missing columns and tables to an existing SQLite database.
Safe to run multiple times (checks before adding).
"""
import sqlite3
import os

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "longevity.db"))


def get_columns(cursor, table):
    cursor.execute(f"PRAGMA table_info({table})")
    return {row[1] for row in cursor.fetchall()}


def table_exists(cursor, table):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cursor.fetchone() is not None


def migrate():
    if not os.path.exists(DB_PATH):
        print(f"[migrate] No database at {DB_PATH}, skipping (will be created by app)")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- users table migrations ---
    if table_exists(cursor, "users"):
        cols = get_columns(cursor, "users")

        if "role" not in cols:
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
            print("[migrate] Added 'role' column to users")

        if "household_id" not in cols:
            cursor.execute("ALTER TABLE users ADD COLUMN household_id INTEGER DEFAULT NULL")
            print("[migrate] Added 'household_id' column to users")

        if "token_created_at" not in cols:
            cursor.execute("ALTER TABLE users ADD COLUMN token_created_at TEXT DEFAULT NULL")
            print("[migrate] Added 'token_created_at' column to users")

    # --- households table ---
    if not table_exists(cursor, "households"):
        cursor.execute("""
            CREATE TABLE households (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                invite_code TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        print("[migrate] Created 'households' table")

    # --- weight_logs table ---
    if not table_exists(cursor, "weight_logs"):
        cursor.execute("""
            CREATE TABLE weight_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                weight_kg REAL NOT NULL,
                recorded_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("[migrate] Created 'weight_logs' table")

    # --- meal_ratings table ---
    if not table_exists(cursor, "meal_ratings"):
        cursor.execute("""
            CREATE TABLE meal_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                recipe_id INTEGER NOT NULL,
                rating INTEGER NOT NULL,
                rated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (recipe_id) REFERENCES recipes(id)
            )
        """)
        print("[migrate] Created 'meal_ratings' table")

    # --- meal_plans: add user_id if missing ---
    if table_exists(cursor, "meal_plans"):
        cols = get_columns(cursor, "meal_plans")
        if "user_id" not in cols:
            cursor.execute("ALTER TABLE meal_plans ADD COLUMN user_id INTEGER DEFAULT NULL")
            print("[migrate] Added 'user_id' column to meal_plans")

    # --- recipes: add author if missing ---
    if table_exists(cursor, "recipes"):
        cols = get_columns(cursor, "recipes")
        if "author" not in cols:
            cursor.execute("ALTER TABLE recipes ADD COLUMN author TEXT DEFAULT ''")
            print("[migrate] Added 'author' column to recipes")
        if "image_url" not in cols:
            cursor.execute("ALTER TABLE recipes ADD COLUMN image_url TEXT DEFAULT ''")
            print("[migrate] Added 'image_url' column to recipes")

    # --- user_profiles table ---
    if not table_exists(cursor, "user_profiles"):
        cursor.execute("""
            CREATE TABLE user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                age INTEGER,
                weight_kg REAL,
                height_cm REAL,
                gender TEXT,
                activity_level TEXT,
                goal TEXT,
                target_weight_kg REAL,
                target_calories INTEGER,
                target_protein_g REAL,
                target_carbs_g REAL,
                target_fat_g REAL,
                target_fiber_g REAL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("[migrate] Created 'user_profiles' table")

    # --- Set first user as admin if no admin exists ---
    cursor.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
    if not cursor.fetchone():
        cursor.execute("UPDATE users SET role = 'admin' WHERE id = (SELECT MIN(id) FROM users)")
        print("[migrate] Set first user as admin")

    conn.commit()
    conn.close()
    print("[migrate] Done.")


if __name__ == "__main__":
    migrate()
