from fastapi import APIRouter, Cookie, Depends, Response
from app import dependencies
from app.services import userService
from app.models.user import CurrentUser
router = APIRouter(prefix = "/users", tags = ["users"])

@router.post("/add")
def add_user_route(result = Depends(userService.add_user)):
    return result
@router.post("/login")
def auth_user(result = Depends(userService.auth_user)):
    return result

@router.get("/logout")
def logout(result = Depends(userService.logout_user)):
    return result

### ENDPOINTS FOR TESTS SECTION
@router.get("/authenticate", tags = ["tests"])
def token(user: CurrentUser = Depends(dependencies.get_current_user)):
    return user