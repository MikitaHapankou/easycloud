from fastapi import APIRouter, HTTPException, Depends, Response, Cookie
from app.schemas.user import userRequest, userORM
from app import dependencies
from app.services import security
from sqlalchemy.orm import Session
from app.services import userService
from app.models.user import User
from sqlalchemy.exc import IntegrityError
router = APIRouter(prefix = "/users", tags = ["users"])

@router.post("/add")
def add_user_route(user: userRequest, db: Session = Depends(dependencies.get_db)):
    try:
        userService.add_user(user.login, user.password, db)
        return {"detail": "Success"}
    except IntegrityError:
        raise HTTPException(status_code = 409, detail = "User already exists")
    except Exception:
        raise HTTPException(status_code = 500, detail = "Internal server error")
@router.post("/login")
def auth_user(response: Response, user: userRequest, db: Session = Depends(dependencies.get_db)):
    is_authenticated = userService.auth_user(user.login, user.password, db)

    if is_authenticated:
        payload = {"sub": user.login}
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

@router.get("/logout")
def logout(response: Response):
    response.delete_cookie(
        key="token",
    )

### ENDPOINTS FOR TESTS SECTION
@router.get("/authenticate", tags = ["tests"])
def token(user: User = Depends(dependencies.get_current_user)):
    return user

@router.get("/get-all", response_model = list[userORM], tags = ["tests"])
def get_all_users(db: Session = Depends(dependencies.get_db)):
    try:
        return userService.get_users(db)
    except Exception:
        raise HTTPException(status_code = 400, detail = "error")
