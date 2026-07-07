import os
from app.config import config
from fastapi import HTTPException, Response
from app.models.user import userRequest
from app.dependencies import raise_auth_error
from supabase import AuthApiError

def add_user(response: Response, user_data: userRequest):
    login = user_data.login
    password = user_data.password
    try:
        supabase_response = config.supabase.auth.sign_up(
            {
                "email": login,
                "password": password,
            }
        )

        dir_path = os.path.join(config.BASE_DIR, login)
        os.makedirs(dir_path, exist_ok = True)

        token = supabase_response.session.access_token
        response.set_cookie(
            key="token",
            value=token,
            httponly=True,
            samesite="lax",
            path="/"
        )

    except AuthApiError as auth_error:
        raise_auth_error(auth_error)

    except Exception as e:
        raise HTTPException(status_code = 500, detail = "Internal server error")

def auth_user(response: Response, user_data: userRequest):
    login: str = user_data.login
    password: str = user_data.password
    try:
        supabase_response = config.supabase.auth.sign_in_with_password(
            {
                "email": login,
                "password": password,
            }
        )

        token = supabase_response.session.access_token
        response.set_cookie(
            key = "token",
            value = token,
            httponly = True,
            samesite = "lax",
            path = "/"
        )

    except AuthApiError as auth_error:
        raise_auth_error(auth_error)

    except Exception as e:
        raise HTTPException(status_code = 500, detail = "Internal server error")
