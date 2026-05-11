from fastapi import APIRouter, HTTPException, Depends, Response, Cookie
from app.schemas.user import userRequest, userOutScheme
from app.dependencies import get_db
from app.services.security import create_token, get_current_user
from sqlalchemy.orm import Session
from app.services.userService import add_user, get_users, auth
router = APIRouter(prefix="/users", tags=["users"])

@router.post("/add")
def add_user_route(user: userRequest, db: Session = Depends(get_db)):
    try:
        add_user(user.login, user.password, db)
        return {"detail": "Success"}
    except Exception as e:
        print(e)
        if "violates unique constraint" in str(e):
            raise HTTPException(status_code = 409, detail="User with this login already exists")
        else:
            raise HTTPException(status_code = 502, detail="Internal server error")

@router.get("/get-all", response_model = list[userOutScheme])
def get_all_users(db: Session = Depends(get_db)):
    try:
        return get_users(db)
    except Exception:
        raise HTTPException(status_code = 400, detail="error")

@router.post("/login")
def auth_user(response: Response, user: userRequest, db: Session = Depends(get_db)):
    try:
        is_authenticated = auth(user.login, user.password, db)
    except Exception as e:
        print(e)
        raise HTTPException(status_code = 500, detail="Internal server error")

    if is_authenticated:
        payload = {"sub": user.login}
        token = create_token(payload)
        response.set_cookie(
            key="token",
            value=token,
            httponly=True,
            samesite="lax",
            path="/"
        )
        return {"detail": "Success"}
    else: raise HTTPException(status_code = 400, detail="Wrong login or password")

@router.get("/authenticate")
def token(token: str =  Cookie(None), db: Session = Depends(get_db)):
    try:
        print(token)
        user = get_current_user(token, db)
        return user
    except Exception as e:
        print(e)
        raise HTTPException(status_code = 400, detail="Wypierdalaj")

@router.get("/logout")
def logout(response: Response):
    response.delete_cookie(
        key="token",

    )