import psycopg2
import psycopg2.extras
import os
import sys
from app.core.config import settings

from fastapi import HTTPException

def get_db():
    url = settings.database_url
    if not url:
        raise HTTPException(status_code=500, detail="DATABASE_URL is not set. Please configure it in your environment.")
    try:
        conn = psycopg2.connect(url)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed. Please check your DATABASE_URL. Error: {str(e)}")

def get_db_cursor(conn):
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

def init_db():
    """Create tables if they don't exist. Logs errors but doesn't crash the server."""
    url = settings.database_url
    if not url:
        print("WARNING: DATABASE_URL not set — skipping DB init. Auth/Progress endpoints will fail.")
        return
    try:
        conn = psycopg2.connect(url)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                hashed_password BYTEA NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_progress (
                email TEXT PRIMARY KEY,
                progress_json TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        print("DB init complete.")
    except Exception as e:
        print(f"WARNING: DB Init failed: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass
