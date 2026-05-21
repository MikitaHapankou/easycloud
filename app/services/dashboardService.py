import os
from app.models.user import User
from app.config import config
from fastapi import Depends, HTTPException, File, UploadFile
from app import dependencies
import aiofiles, aiofiles.os

def get_files_recursive(dir):
    files = []
    for content in os.listdir(dir):
        filepath = os.path.join(dir, content)
        print(filepath)
        files.append(content)
        if not os.path.isfile(filepath):
            files += get_files_recursive(filepath)

    return files

def get_user_files(user: User = Depends(dependencies.get_current_user)):
    user_dir = os.path.join(config.BASE_DIR, user.login)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir, exist_ok = True)
        filenames = []
    else:
        filenames = get_files_recursive(user_dir)
    print(get_files_recursive(user_dir))
    return {"username": user.login, "files": filenames}

def get_file_path(filename: str, user: User = Depends(dependencies.get_current_user)):
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(config.BASE_DIR, user.login, safe_filename)

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

async def delete_file(filename: str, user: User = Depends(dependencies.get_current_user)):
    safe_filename = os.path.basename(filename)
    real_file_path = os.path.join(config.BASE_DIR, user.login, safe_filename)

    isfile = await aiofiles.os.path.isfile(real_file_path)
    if not isfile: raise HTTPException(status_code = 404, detail = "File not found")

    await aiofiles.os.remove(real_file_path)

    return "Success"

async def add_directory(dirname: str, user: User = Depends(dependencies.get_current_user)):
    dir_path = os.path.abspath(os.path.join(config.BASE_DIR, user.login))
    new_dir_path = os.path.abspath(os.path.join(dir_path, dirname))

    if not new_dir_path.startswith(dir_path):
        raise HTTPException(status_code = 400, detail = "Invalid directory name")

    if os.path.exists(new_dir_path): raise HTTPException(status_code = 404, detail = "Directory already exists")

    await aiofiles.os.mkdir(new_dir_path)

    return "Success"