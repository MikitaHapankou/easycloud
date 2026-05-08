from fastapi import FastAPI, APIRouter
from app.schemas.user import userScheme, userOutScheme
from app.dependencies import get_db
from sqlalchemy.orm import Session
from app.services.userService import add_users, get_users
from fastapi import HTTPException, Depends
app = FastAPI()
router = APIRouter(prefix="/users", tags=["users"])

@router.post("/add")
def add_user(user: userScheme, db: Session = Depends(get_db)):
    try:
        return add_users(user.name, user.surname, db)
    except Exception:
        raise HTTPException(status_code = 400, detail="error")

@router.get("/get-all", response_model = list[userOutScheme])
def get_all_users(db: Session = Depends(get_db)):
    try:
        return get_users(db)
    except Exception:
        raise HTTPException(status_code = 400, detail="error")
