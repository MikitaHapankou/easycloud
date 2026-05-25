import os
from app.models.user import User
from app.config import config
from fastapi import Depends, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from app import dependencies
import aiofiles, aiofiles.os
import uuid

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

def get_user_files(user: User = Depends(dependencies.get_current_user)):
    if user.role == config.Role.USER.name:
        user_dir = os.path.join(config.BASE_DIR, user.login)

        if not os.path.exists(user_dir):
            filenames = []
            os.makedirs(user_dir, exist_ok = True)
        else:
            filenames = get_files_recursive(user_dir, "filesContainer", user.login)
    else:
        user_dir = config.BASE_DIR
        filenames = get_files_recursive(user_dir, "filesContainer")

    return {"username": user.login, "files": filenames}

def get_file_path(filename: str, user: User = Depends(dependencies.get_current_user)):
    safe_path = os.path.join(config.BASE_DIR, filename)
    file_path = os.path.abspath(safe_path)

    if user.role != config.Role.ADMIN.name:
        if not file_path.startswith(os.path.join(config.BASE_DIR, user.login)):
            raise HTTPException(status_code=400, detail="Bad filename")

    if not file_path.startswith(config.BASE_DIR):
        raise HTTPException(status_code = 400, detail = "Bad filename")

    if not os.path.isfile(file_path):
        raise HTTPException(status_code = 404, detail = "File doesn't exist")

    return FileResponse(file_path, filename = os.path.basename(filename))

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