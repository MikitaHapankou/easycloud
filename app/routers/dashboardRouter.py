from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, Cookie
from app.config.templates import templates
from app.services.security import get_current_user
from app.dependencies import get_db
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from app.config.security import BASE_DIR
import os

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
def get_files(token = Cookie(None), db: Session = Depends(get_db)):
    try:
        print("Token: ", token)
        user = get_current_user(token, db)
        user_dir = os.path.join(BASE_DIR, user.login)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir, exist_ok=True)
            filenames = []
        else:
            filenames = os.listdir(user_dir)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Wypierdalaj")

    resData = {"username": user.login, "files": filenames}
    print(resData)
    return resData

@router.get("/download/{file}")
def get_dashboard(file: str, token = Cookie(None), db: Session = Depends(get_db)):
    try:
        user = get_current_user(token, db)
        file_path = os.path.join(BASE_DIR, user.login, file)
        return FileResponse(file_path, filename=file)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Wypierdalaj")
