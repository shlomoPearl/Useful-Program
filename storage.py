from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from model import User, SessionToken
from crypto import encrypt_bytes, decrypt_bytes
import json
import os
import uuid
from dotenv import load_dotenv

load_dotenv()
TOKEN_TTL_DAYS = int(os.getenv("TOKEN_TTL_DAYS", "1"))
SESSION_EXPIRE_HOURS = int(os.getenv("SESSION_EXPIRE_HOURS", "24"))


def save_user_token(db: Session, user_id: str, email: str, token_dict: dict):
    token_bytes = json.dumps(token_dict).encode()
    enc = encrypt_bytes(token_bytes)
    expires_at = datetime.now(timezone.utc) + timedelta(days=TOKEN_TTL_DAYS)
    existing = db.query(User).filter(User.g_id == user_id).one_or_none()
    if existing:
        existing.token = enc
        existing.expires_at = expires_at
        existing.email = email
        existing.last_accessed = datetime.now(timezone.utc)
    else:
        user = User(
            g_id=user_id,
            email=email,
            token=enc,
            expires_at=expires_at
        )
        db.add(user)
    db.commit()


def load_user_token(db: Session, user_id: str) -> dict | None:
    row = db.query(User).filter(
        User.g_id == user_id,
        User.is_active is True,
        User.expires_at > datetime.now(timezone.utc)
    ).one_or_none()
    if not row:
        return None
    try:
        row.last_accessed = datetime.now(timezone.utc)
        db.commit()
        raw = decrypt_bytes(row.token)
        return json.loads(raw.decode())
    except Exception as e:
        print(f"Token decryption error: {e}")
        return None


def create_session(db: Session, user_id: str) -> str:
    session_id = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(hours=SESSION_EXPIRE_HOURS)
    session = SessionToken(
        session_id=session_id,
        g_id=user_id,
        expires_at=expires_at
    )
    db.add(session)
    db.commit()
    return session_id


def validate_session(db: Session, session_id: str) -> str | None:
    session = db.query(SessionToken).filter(
        SessionToken.session_id == session_id,
        SessionToken.is_active is True,
        SessionToken.expires_at > datetime.now(timezone.utc)
    ).one_or_none()
    return session.g_id if session else None


def invalidate_session(db: Session, session_id: str):
    session = db.query(SessionToken).filter(
        SessionToken.session_id == session_id
    ).one_or_none()
    if session:
        session.is_active = False
        db.commit()


def cleanup_expired_sessions(db: Session):
    db.query(SessionToken).filter(
        SessionToken.expires_at < datetime.now(timezone.utc)
    ).delete()
    db.commit()


def cleanup_expired_tokens(db: Session):
    db.query(User).filter(
        User.expires_at < datetime.now(timezone.utc)
    ).delete()
    db.commit()
