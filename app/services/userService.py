import os
from app.config import config
from fastapi import HTTPException, Response, Depends
from app.models.user import userRequest, CurrentUser
from app.dependencies import raise_auth_error, get_supabase, get_current_user
from supabase import AuthApiError

def add_user(response: Response, user_data: userRequest, supabase = Depends(get_supabase)):
    login = user_data.login
    password = user_data.password
    try:
        supabase_response = supabase.auth.sign_up(
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

def logout_user(response: Response, user: CurrentUser = Depends(get_current_user), supabase = Depends(get_supabase)):
    response.delete_cookie(
        key="token",
    )

def auth_user(response: Response, user_data: userRequest, supabase = Depends(get_supabase)):
    login: str = user_data.login
    password: str = user_data.password
    try:

        supabase_response = supabase.auth.sign_in_with_password(
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
