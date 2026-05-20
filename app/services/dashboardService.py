import os
from app.models.user import User
from app.config import config
from fastapi import Depends, HTTPException, File, UploadFile
from app import dependencies
import aiofiles, aiofiles.os

def get_user_files(user: User = Depends(dependencies.get_current_user)):
    user_dir = os.path.join(config.BASE_DIR, user.login)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir, exist_ok = True)
        filenames = []
    else:
        filenames = os.listdir(user_dir)

    return {"username": user.login, "files": filenames}

def get_file_path(file: str, user: User = Depends(dependencies.get_current_user)):
    file_path = os.path.join(config.BASE_DIR, user.login, file)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code = 404, detail = "File doesn't exist")

    return file_path

async def add_new_file(uploaded_file: UploadFile = File(...), user: User = Depends(dependencies.get_current_user)):
    safe_filename = os.path.basename(uploaded_file.filename)
    real_file_path = os.path.join(config.BASE_DIR, user.login, safe_filename)

    try:
        async with aiofiles.open(real_file_path, 'wb') as real_file:
            while chunk := await uploaded_file.read(1024 * 64):
                await real_file.write(chunk)

        return "Success"

    except Exception:
        raise HTTPException(status_code = 500, detail = "Couldn't save file")