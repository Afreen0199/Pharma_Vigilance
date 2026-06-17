import os
import time
import uuid
import sqlite3
import logging
import json
import base64
import hmac
import hashlib
from typing import Optional, Dict, Any
from app.services.database_service import db_service

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("JWT_SECRET", "pharmacovigilance_copilot_secret_key_123456")
DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "auth.db")

def init_local_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE,
        password_hash TEXT,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

init_local_db()

def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def base64url_decode(data: str) -> bytes:
    padding = '=' * (4 - (len(data) % 4))
    return base64.urlsafe_b64decode(data + padding)

def generate_jwt(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = base64url_encode(json.dumps(header).encode('utf-8'))
    payload_b64 = base64url_encode(json.dumps(payload).encode('utf-8'))
    
    signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
    signature = hmac.new(SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
    signature_b64 = base64url_encode(signature)
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def verify_jwt(token: str) -> Optional[dict]:
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        header_b64, payload_b64, signature_b64 = parts
        
        signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
        expected_signature = hmac.new(SECRET_KEY.encode('utf-8'), signing_input, hashlib.sha256).digest()
        expected_signature_b64 = base64url_encode(expected_signature)
        
        if not hmac.compare_digest(signature_b64, expected_signature_b64):
            return None
            
        payload = json.loads(base64url_decode(payload_b64).decode('utf-8'))
        if "exp" in payload and payload["exp"] < time.time():
            return None
        return payload
    except Exception:
        return None

def hash_password(password: str) -> str:
    salt = uuid.uuid4().hex
    hashed = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return f"{salt}:{hashed}"

def verify_password(password: str, password_hash: str) -> bool:
    try:
        salt, hashed = password_hash.split(':')
        test_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
        return test_hash == hashed
    except Exception:
        return False

class AuthService:
    def __init__(self):
        self.use_supabase = False
        self._check_supabase_table()

    def _check_supabase_table(self):
        if not db_service.client:
            return
        try:
            db_service.client.table("users").select("*").limit(1).execute()
            self.use_supabase = True
            logger.info("AuthService: Verified 'users' table in Supabase. Using Supabase for Auth.")
        except Exception:
            self.use_supabase = False

    def register_user(self, email: str, password: str) -> bool:
        user_id = str(uuid.uuid4())
        pwd_hash = hash_password(password)
        created_at = time.strftime("%Y-%m-%d %H:%M:%S")

        self._check_supabase_table()

        if self.use_supabase:
            try:
                payload = {
                    "id": user_id,
                    "email": email,
                    "password_hash": pwd_hash,
                    "created_at": created_at
                }
                db_service.client.table("users").insert(payload).execute()
                return True
            except Exception as e:
                logger.error(f"Supabase registration error: {e}")
                return False
        else:
            try:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (id, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                    (user_id, email, pwd_hash, created_at)
                )
                conn.commit()
                conn.close()
                return True
            except sqlite3.IntegrityError:
                logger.warning(f"Email {email} already registered locally.")
                return False
            except Exception as e:
                logger.error(f"Local registration error: {e}")
                return False

    def login_user(self, email: str, password: str) -> Optional[str]:
        self._check_supabase_table()

        user_data = None
        if self.use_supabase:
            try:
                res = db_service.client.table("users").select("*").eq("email", email).execute()
                if res.data and len(res.data) > 0:
                    user_data = res.data[0]
            except Exception as e:
                logger.error(f"Supabase login lookup error: {e}")
        else:
            try:
                conn = sqlite3.connect(DB_FILE)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
                row = cursor.fetchone()
                if row:
                    user_data = dict(row)
                conn.close()
            except Exception as e:
                logger.error(f"Local login lookup error: {e}")

        if not user_data:
            return None

        if verify_password(password, user_data["password_hash"]):
            payload = {
                "sub": user_data["id"],
                "email": user_data["email"],
                "exp": time.time() + 86400
            }
            return generate_jwt(payload)
        return None

auth_service = AuthService()
