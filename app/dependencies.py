from app.db.database import LocalSession
from app.config.error_codes import AUTH_ERROR_MAP
from fastapi import HTTPException, Cookie
from app.config import config
from supabase import AuthApiError, create_client, Client
from app.models.user import CurrentUser

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
        supabase: Client = create_client(config.settings.SUPABASE_PROJECT_URL, config.settings.SUPABASE_KEY)
        supabase.auth.set_session(token, "")
        supabase_response = supabase.auth.get_user()
        login = supabase_response.user.email
        return CurrentUser(login = login, token = token)

    except AuthApiError as auth_error:
        raise_auth_error(auth_error)

    except Exception as e:
        print(e)
        raise HTTPException(status_code = 500, detail = "Internal server error")

def get_supabase() -> Client:
    supabase: Client = create_client(config.settings.SUPABASE_PROJECT_URL, config.settings.SUPABASE_KEY)

    return supabase
