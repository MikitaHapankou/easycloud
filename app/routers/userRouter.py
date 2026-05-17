from fastapi import APIRouter, HTTPException, Depends, Response, Cookie
from app.schemas.user import userRequest, userOutScheme
from app import dependencies
from app.services import security
from sqlalchemy.orm import Session
from app.services import userService
from app.models.user import User
router = APIRouter(prefix="/users", tags=["users"])

@router.post("/add")
def add_user_route(user: userRequest, db: Session = Depends(dependencies.get_db)):
    try:
        userService.add_user(user.login, user.password, db)
        return {"detail": "Success"}
    except Exception as e:
        print(e)
        if "violates unique constraint" in str(e):
            raise HTTPException(status_code = 409, detail="User with this login already exists")
        else:
            raise HTTPException(status_code = 502, detail="Internal server error")

@router.get("/get-all", response_model = userOutScheme)
def get_all_users(db: Session = Depends(dependencies.get_db)):
    try:
        return {"user_list": userService.get_users(db)}
    except Exception:
        raise HTTPException(status_code = 400, detail="error")

@router.post("/login")
def auth_user(response: Response, user: userRequest, db: Session = Depends(dependencies.get_db)):
    try:
        is_authenticated = userService.auth_user(user.login, user.password, db)
    except Exception as e:
        print(e)
        raise HTTPException(status_code = 500, detail="Internal server error")

    if is_authenticated:
        payload = {"sub": user.login}
        token = security.create_token(payload)
        response.set_cookie(
            key="token",
            value=token,
            httponly=True,
            samesite="lax",
            path="/"
        )
        return {"detail": "Success"}
    else: raise HTTPException(status_code = 400, detail="Wrong login or password")

@router.get("/logout")
def logout(response: Response):
    response.delete_cookie(
        key="token",
    )

### ENDPOINTS FOR TESTS SECTION
def get_current_user(token: str = Cookie(""), db: Session = Depends(dependencies.get_db)):
    if not token:
        raise HTTPException(401)

    user = security.get_current_user(token, db)
    return user

@router.get("/authenticate")
def token(user: User = Depends(get_current_user)):
    return user