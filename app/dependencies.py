from app.db.database import LocalSession
from app.config.error_codes import AUTH_ERROR_MAP
from fastapi import HTTPException, Cookie
from app.config import config
from supabase import AuthApiError
from app.models.user import CurrentUser
import os

def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()

def raise_auth_error(auth_error: AuthApiError):
    status_code, message = AUTH_ERROR_MAP.get(auth_error.code, (500, "Internal server error"))

    raise HTTPException(status_code = status_code, detail = message)

def get_current_user(token = Cookie(None)) -> CurrentUser:
    if not token:
        raise HTTPException(status_code = 401, detail = "No token")

    try:
        response = config.supabase.auth.get_claims(jwt=token)
        claims_dict = response["claims"]
        login = claims_dict["email"]

        return CurrentUser(login = login)

    except AuthApiError as auth_error:
        raise_auth_error(auth_error)

    except Exception as e:
        raise HTTPException(status_code = 500, detail = "Internal server error")
