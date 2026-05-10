import bcrypt
from datetime import datetime, timedelta, timezone
import os
import jwt
from app.models.user import User

JWT_EXPIRE_MINUTES = float(os.getenv("JWT_EXPIRE_MINUTES"))
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGO = os.getenv("JWT_ALGO")

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    password_bytes = password.encode('utf-8')
    password_hash = bcrypt.hashpw(password_bytes, salt)
    hash_string = password_hash.decode('utf-8')

    return hash_string

def check_password(password: str, real_hash_string: str) -> bool:
    provided_bytes = password.encode('utf-8')
    real_bytes = real_hash_string.encode('utf-8')

    if bcrypt.checkpw(provided_bytes, real_bytes):
        return True
    else: return False

def create_token(data: dict):
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=JWT_EXPIRE_MINUTES)

    to_encode.update({"exp": expires, "nbf": now})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGO)

    return encoded_jwt

def get_current_user(token, db):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        login = str(payload.get("sub"))
        user = db.query(User).filter_by(login=login).first()
        return user
    except Exception as e:
        raise e
