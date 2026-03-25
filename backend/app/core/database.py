import psycopg2
import psycopg2.extras
import os
import sys
from app.core.config import settings

def get_db():
    if not settings.database_url:
        print("CRITICAL: DATABASE_URL is not set in .env")
        sys.exit(1)
    try:
        conn = psycopg2.connect(settings.database_url)
        return conn
    except Exception as e:
        print(f"CRITICAL: Failed to connect to DB: {e}")
        sys.exit(1)

def get_db_cursor(conn):
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

def init_db():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                hashed_password BYTEA NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS user_progress (
                email TEXT PRIMARY KEY,
                progress_json TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
    except Exception as e:
        print(f"Warning: DB Init failed (normal if tables exist): {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
