from app.models.user import User
from .security import hash_password, check_password
from datetime import datetime
import os
from app.config.security import BASE_DIR

def get_users(db):
    users = db.query(User).all()
    return users

def add_user(login: str, password: str, db):
    try:
        password_hash = hash_password(password)
        now = datetime.now()
        new_user = User(login=login, password_hash=password_hash, created_at=now)
        db.add(new_user)
        db.commit()
        dir_path = os.path.join(BASE_DIR, new_user.login)
        os.makedirs(dir_path, exist_ok=True)
        return new_user
    except Exception as e:
        raise e

def auth_user(login: str, password: str, db):
    try:
        user = db.query(User).filter_by(login = login).first()
        real_hash_string = user.password_hash
        return check_password(password, real_hash_string)

    except Exception as e:
        raise e