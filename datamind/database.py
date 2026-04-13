"""
SQLite Database wrapper for DataMind Auto-ML Platform.
Handles: User Auth, Data Set References.
"""

import sqlite3
import os
import hashlib
import binascii

_DB_PATH = os.path.join(os.path.dirname(__file__), "data", "datamind.db")

def _get_conn():
    return sqlite3.connect(_DB_PATH)

def init_db():
    with _get_conn() as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                file_name TEXT,
                file_path TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_name TEXT,
                lesson_type TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

# --- Password Hashing ---
def _hash_password(password: str, salt: bytes = None) -> tuple[str, str]:
    if salt is None:
        salt = os.urandom(32)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return binascii.hexlify(pwd_hash).decode('ascii'), binascii.hexlify(salt).decode('ascii')

def _verify_password(password: str, pwd_hash_hex: str, salt_hex: str) -> bool:
    salt = binascii.unhexlify(salt_hex)
    pwd_hash, _ = _hash_password(password, salt)
    return pwd_hash == pwd_hash_hex

# --- Auth ---
def register_user(username: str, password: str) -> bool:
    pwd_hash, salt = _hash_password(password)
    try:
        with _get_conn() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)", 
                      (username, pwd_hash, salt))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False

def authenticate(username: str, password: str) -> int | None:
    with _get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT id, password_hash, salt FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        if row:
            user_id, pwd_hash, salt = row
            if _verify_password(password, pwd_hash, salt):
                return user_id
    return None

def get_username(user_id: int) -> str | None:
    with _get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
        return row[0] if row else None

# --- Intelligence Persistence ---
def save_lesson(dataset_name: str, lesson_type: str, content: str) -> None:
    """Save a learning outcome for the current dataset or global context."""
    with _get_conn() as conn:
        c = conn.cursor()
        # Prevent duplicates
        c.execute("SELECT id FROM lessons WHERE dataset_name = ? AND content = ?", (dataset_name, content))
        if c.fetchone() is None:
            c.execute("INSERT INTO lessons (dataset_name, lesson_type, content) VALUES (?, ?, ?)",
                      (dataset_name, lesson_type, content))
            conn.commit()

def get_lessons(dataset_name: str, limit: int = 20) -> list[str]:
    """Retrieve the most recent relevant lessons associated with a dataset name or global context."""
    with _get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT content FROM lessons WHERE dataset_name = ? ORDER BY created_at DESC LIMIT ?", 
                  (dataset_name, limit))
        # Reverse to maintain chronological order in the prompt [Oldest -> Newest]
        return [row[0] for row in c.fetchall()][::-1]

def clear_lessons(dataset_name: str) -> None:
    """Clear all lessons for a specific dataset."""
    with _get_conn() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM lessons WHERE dataset_name = ?", (dataset_name,))
        conn.commit()
