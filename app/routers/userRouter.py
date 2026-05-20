from fastapi import APIRouter, HTTPException, Depends, Response, Cookie
from app.schemas.user import userRequest, userORM
from app import dependencies
from app.services import security
from sqlalchemy.orm import Session
from app.services import userService
from app.models.user import User
router = APIRouter(prefix = "/users", tags = ["users"])

@router.post("/add")
def add_user_route(result = Depends(userService.add_user)):
    return result
@router.post("/login")
def auth_user(result = Depends(userService.auth_user)):
    return result

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
