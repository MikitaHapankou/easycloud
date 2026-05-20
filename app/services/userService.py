from app.models.user import User
from .import security
from datetime import datetime
import os
from app.config import config
import aiofiles, aiofiles.os
from fastapi import HTTPException, Depends, Response
from app.schemas.user import userRequest
from app import dependencies
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

def get_users(db):
    users = db.query(User).all()
    return users

def add_user(user_data: userRequest, db: Session = Depends(dependencies.get_db)):
    login = user_data.login
    password = user_data.password
    try:
        password_hash = security.hash_password(password)
        now = datetime.now()
        new_user = User(login = login, password_hash = password_hash, created_at = now)
        db.add(new_user)

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        dir_path = os.path.join(config.BASE_DIR, new_user.login)
        os.makedirs(dir_path, exist_ok = True)

        return "Success"

    except IntegrityError:
        raise HTTPException(status_code=409, detail="User already exists")

    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

def auth_user(response: Response, user_data: userRequest, db: Session = Depends(dependencies.get_db)):
    login: str = user_data.login
    password: str = user_data.password

    user = db.query(User).filter_by(login = login).first()

    if not user: raise HTTPException(status_code = 404, detail = "User doesn't exist")

    is_authenticated = security.check_password(password, user.password_hash)

    if is_authenticated:
        payload = {"sub": user_data.login}
        token = security.create_token(payload)
        response.set_cookie(
            key = "token",
            value = token,
            httponly = True,
            samesite = "lax",
            path = "/"
        )
        return {"detail": "Success"}

    else: raise HTTPException(status_code = 401, detail = "Invalid credentials")
