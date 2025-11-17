import os
import psycopg2
import hashlib
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from datetime import datetime, timedelta, timezone

load_dotenv()
fernet = Fernet(os.getenv("KEY"))


def hash_email(email: str) -> str:
    return hashlib.sha256(email.encode()).hexdigest()


class DBManager:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
        )
        self.expiry_minutes = int(os.getenv("TOKEN_EXPIRATION_MINUTES", 60))
        self._create_table()

    def _create_table(self):
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users_info (
                        email_hash TEXT PRIMARY KEY,
                        encrypted_token BYTEA NOT NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
                """)

    def save_token(self, email, token_json: str):
        email_hash = hash_email(email)
        encrypted_token = fernet.encrypt(token_json.encode())
        try:
            with self.conn:
                with self.conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO users_info (email_hash, encrypted_token, created_at)
                        VALUES (%s, %s, CURRENT_TIMESTAMP)
                        ON CONFLICT (email_hash)
                        DO UPDATE SET encrypted_token = EXCLUDED.encrypted_token, created_at = CURRENT_TIMESTAMP;
                    """, (email_hash, encrypted_token))
        except Exception as e:
            print(f"Error saving token for {email}: {e}")

    def load_token(self, email):
        email_hash = hash_email(email)
        with self.conn.cursor() as cur:
            cur.execute("SELECT encrypted_token, created_at FROM users_info WHERE email_hash = %s;", (email_hash,))
            row = cur.fetchone()
            if not row:
                return None
            encrypted_token, created_at = row
            age = datetime.now(timezone.utc) - created_at
            if age > timedelta(minutes=self.expiry_minutes):
                self.delete_token(email)
                return None
            return fernet.decrypt(encrypted_token).decode()

    def delete_token(self, email):
        email_hash = hash_email(email)
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM users_info WHERE email_hash = %s;", (email_hash,))

    def delete_expired_tokens(self):
        expiration_threshold = datetime.now(timezone.utc) - timedelta(minutes=self.expiry_minutes)
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM users_info WHERE created_at < %s;", (expiration_threshold,))

    def __del__(self):
        if self.conn:
            self.conn.close()
