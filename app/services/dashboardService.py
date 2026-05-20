import os
from app.models.user import User
from app.config import config
from fastapi import Depends, HTTPException
from app import dependencies

def get_user_files(user: User = Depends(dependencies.get_current_user)):
    user_dir = os.path.join(config.BASE_DIR, user.login)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir, exist_ok=True)
        filenames = []
    else:
        filenames = os.listdir(user_dir)

    return {"username": user.login, "files": filenames}

def get_file_path(user: User = Depends(dependencies.get_current_user)):
    file_path = os.path.join(config.BASE_DIR, user.login, file)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File doesn't exist")
