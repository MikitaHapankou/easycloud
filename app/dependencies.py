from app.db.database import LocalSession
from app.config.error_codes import AUTH_ERROR_MAP
from fastapi import Cookie, HTTPException, Depends
from app.services import security
from sqlalchemy.orm import Session
from supabase import AuthApiError

def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Cookie(""), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(401)

    user = security.get_current_user(token, db)

    return user

def raise_auth_error(auth_error: AuthApiError):
    status_code, message = AUTH_ERROR_MAP.get(auth_error.code, (500, "Internal server error"))

    raise HTTPException(status_code = status_code, detail = message)