# storage.py
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from model import GmailUser
from crypto import encrypt_bytes, decrypt_bytes
import json
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN_TTL_DAYS = int(os.getenv("TOKEN_TTL_DAYS", "3"))


def save_token(db: Session, user_id: str, token_dict: dict):
    token_bytes = json.dumps(token_dict).encode()
    enc = encrypt_bytes(token_bytes)
    expires_at = datetime.utcnow() + timedelta(days=TOKEN_TTL_DAYS)
    obj = GmailUser(
        id=user_id,
        token=enc,
        expires_at=expires_at
    )
    existing = db.query(GmailUser).filter(GmailUser.id == user_id).one_or_none()
    if existing:
        existing.token = enc
        existing.expires_at = expires_at
    else:
        db.add(obj)
    db.commit()


def load_token(db: Session, user_id: str) -> dict | None:
    row = db.query(GmailUser).filter(
        GmailUser.id == user_id,
        GmailUser.expires_at > datetime.utcnow()
    ).one_or_none()
    if not row:
        return None
    try:
        raw = decrypt_bytes(row.encrypted_token)
        return json.loads(raw.decode())
    except Exception:
        return None


def delete_token(db: Session, user_id: str):
    db.query(GmailUser).filter(GmailUser.id == user_id).delete()
    db.commit()


def delete_expired(db: Session):
    db.query(GmailUser).filter(GmailUser.expires_at < datetime.utcnow()).delete()
    db.commit()
