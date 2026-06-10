import os
from app.models.user import User
from app.config import config
from fastapi import Depends, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from app import dependencies
import aiofiles, aiofiles.os
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from app.models.permission import Permission
from app.models.acl import acl_records

def share_directory(dirname: str, target_login: str, action: str = "read", db: Session = Depends(dependencies.get_db), current_user: User = Depends(dependencies.get_current_user)):
    target_user = db.query(User).filter_by(login=target_login).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    if target_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Can't share to yourself")

    user_dir_path = os.path.abspath(os.path.join(config.BASE_DIR, current_user.login))
    target_dir_path = os.path.abspath(os.path.join(config.BASE_DIR, dirname))

    if not target_dir_path.startswith(user_dir_path):
        raise HTTPException(status_code=400, detail="Invalid user")

    if not os.path.exists(target_dir_path):
        raise HTTPException(status_code=404, detail="File or directory does not exist on disk")

    unique_dirname = dirname

    permission = db.query(Permission).filter_by(dirname=unique_dirname).first()
    if not permission:
        permission = Permission(dirname=unique_dirname)
        db.add(permission)
        db.commit()
        db.refresh(permission)

    try:
        stmt = insert(acl_records).values(
            user_id=target_user.id,
            permission_id=permission.id,
            action=action
        )
        db.execute(stmt)
        db.commit()
        return {"detail": f"Access to folder '{dirname}' successfully granted to {target_login}"}

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="This user already has access to this folder")


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

def get_user_files(db: Session = Depends(dependencies.get_db), user: User = Depends(dependencies.get_current_user)):
    if user.role == config.Role.USER.name:
        user_dir = os.path.join(config.BASE_DIR, user.login)

        if not os.path.exists(user_dir):
            filenames = []
            os.makedirs(user_dir, exist_ok = True)
        else:
            filenames = get_files_recursive(user_dir, "filesContainer", user.login)

        shared_permissions = db.query(Permission).join(acl_records).filter(
            acl_records.c.user_id == user.id,
            acl_records.c.action == "read"
        ).all()

        for perm in shared_permissions:
            phys_path = os.path.join(config.BASE_DIR, perm.dirname)

            if os.path.exists(phys_path):
                parts = perm.dirname.strip('/').split('/')
                owner_login = parts[0]
                resource_name = parts[-1]

                shared_id = f"shared_{perm.id}"

                if os.path.isdir(phys_path):
                    filenames.append({
                        "id": shared_id,
                        "name": f"shared {resource_name} (from {owner_login})",
                        "parent_id": "filesContainer",
                        "type": "dir",
                        "path": perm.dirname + "/"
                    })
                    shared_files = get_files_recursive(phys_path, shared_id, perm.dirname + "/")
                    filenames += shared_files
                elif os.path.isfile(phys_path):
                    filenames.append({
                        "id": shared_id,
                        "name": f"shared {resource_name} (from {owner_login})",
                        "parent_id": "filesContainer",
                        "type": "file",
                        "path": perm.dirname
                    })
    else:
        user_dir = config.BASE_DIR
        filenames = get_files_recursive(user_dir, "filesContainer")

    print(filenames)
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

async def delete_file(filename: str, user: User = Depends(dependencies.get_current_user)):
    file_path = os.path.join(config.BASE_DIR, filename)
    real_file_path = os.path.abspath(file_path)

    user_path = os.path.join(config.BASE_DIR, user.login)
    if not real_file_path.startswith(user_path) and user.role != "ADMIN":
        raise HTTPException(status_code = 400, detail = "Invalid filename")

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