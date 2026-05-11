from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request
from app.config.templates import templates
from app.services.security import get_current_user
from app.schemas.dashboard import DashboardFileResponse
from app.dependencies import get_db
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config.security import bearer

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/")
def get_dashboard(request: Request):

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
        }
    )

@router.get("/my")
def get_files(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    filenames = ["first", "second", "third"]

    try:
        sent_token = credentials.credentials
        user = get_current_user(sent_token, db)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Wypierdalaj")

    resData = {"username": user.login, "files": filenames}
    print(resData)
    return resData
