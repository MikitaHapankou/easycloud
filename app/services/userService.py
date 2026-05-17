from app.models.user import User
from .import security
from datetime import datetime
import os
from app.config.security import BASE_DIR
from fastapi import HTTPException

def get_users(db):
    users = db.query(User).all()
    return users

def add_user(login: str, password: str, db):
    password_hash = security.hash_password(password)
    now = datetime.now()
    new_user = User(login = login, password_hash = password_hash, created_at = now)
    db.add(new_user)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    dir_path = os.path.join(BASE_DIR, new_user.login)
    os.makedirs(dir_path, exist_ok = True)

    return new_user

def auth_user(login: str, password: str, db):
    user = db.query(User).filter_by(login = login).first()

    if not user: raise HTTPException(status_code = 404, detail = "User doesn't exist")

    return security.check_password(password, user.password_hash)
