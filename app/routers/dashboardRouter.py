from fastapi import APIRouter, HTTPException, Depends, Request, Cookie
from app.config.templates import templates
from app.services import security
from app import dependencies
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from app.config.security import BASE_DIR
import os
from app.models.user import User
from app.schemas.dashboard import dashboardFileList
router = APIRouter(prefix="/dashboard", tags=["dashboard"])

def get_current_user(token: str = Cookie(""), db: Session = Depends(dependencies.get_db)):
    if not token:
        raise HTTPException(401)

    user = security.get_current_user(token, db)

    return user

@router.get("/")
def get_dashboard(request: Request):

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
        }
    )

@router.get("/my", response_model=dashboardFileList)
def get_files(user: User = Depends(get_current_user)):
    user_dir = os.path.join(BASE_DIR, user.login)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir, exist_ok=True)
        filenames = []
    else:
        filenames = os.listdir(user_dir)

    return {"username": user.login, "files": filenames}

@router.get("/download/{file}")
def get_dashboard(file: str, user: User = Depends(get_current_user)):
    file_path = os.path.join(BASE_DIR, user.login, file)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File doesn't exist")

    return FileResponse(file_path, filename=file)
