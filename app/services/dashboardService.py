import os
from app.models.user import CurrentUser
from app.config import config
from fastapi import Depends, HTTPException, File, UploadFile
from app import dependencies
import aiofiles, aiofiles.os
import uuid

def check_path_safety(filename: str, user_login: str):
    safe_path = os.path.join(config.BASE_DIR, filename)
    file_path = os.path.abspath(safe_path)

    if not file_path.startswith(os.path.join(config.BASE_DIR, user_login)):
        raise HTTPException(status_code=400, detail="Bad filename")

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File doesn't exist")

    return file_path

def get_files_recursive(directory, parent_id: str, name = ""):
    files = []
    for content in os.listdir(directory):
        filepath = os.path.join(directory, content)
        if name: path = name + "/" + content
        else: path = content
        content_dict = {"id": str(uuid.uuid4()), "name": content, "parent_id": parent_id, "type": "file", "path": path}

        if not os.path.isfile(filepath):
            content_dict["type"] = "dir"
            files += get_files_recursive(filepath, content_dict["id"], path)

        files.append(content_dict)

    return files

def get_user_files(user: CurrentUser = Depends(dependencies.get_current_user)):
    user_dir = os.path.join(config.BASE_DIR, user.login)
    filenames = get_files_recursive(user_dir, "filesContainer", user.login)

    return {"username": user.login, "files": filenames}

def get_file_path(filename: str, user: CurrentUser = Depends(dependencies.get_current_user)):
    safe_path = check_path_safety(filename, user.login)

    return safe_path

async def add_new_file(uploaded_file: UploadFile = File(...), user: CurrentUser = Depends(dependencies.get_current_user)):
    safe_filename = os.path.basename(uploaded_file.filename)
    real_file_path = os.path.join(config.BASE_DIR, user.login, safe_filename)

    try:
        if await aiofiles.os.path.exists(real_file_path):
            raise HTTPException(status_code=404, detail="File already exists")

        if uploaded_file.size > 500 * (10 ** 6):
            raise HTTPException(status_code=400, detail="File is too big")

        async with aiofiles.open(real_file_path, 'wb') as real_file:
            while chunk := await uploaded_file.read(1024 * 64):
                await real_file.write(chunk)

        return "Success"

    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Couldn't save file")

async def delete_file(filename: str, user: CurrentUser = Depends(dependencies.get_current_user)):
    safe_path = check_path_safety(filename, user.login)
    await aiofiles.os.remove(safe_path)

async def add_directory(dirname: str, user: CurrentUser = Depends(dependencies.get_current_user)):
    dir_path = os.path.abspath(os.path.join(config.BASE_DIR, user.login))
    new_dir_path = os.path.abspath(os.path.join(dir_path, dirname))

    if not new_dir_path.startswith(dir_path):
        raise HTTPException(status_code = 400, detail = "Invalid directory name")

    if os.path.exists(new_dir_path): raise HTTPException(status_code = 404, detail = "Directory already exists")

    await aiofiles.os.mkdir(new_dir_path)