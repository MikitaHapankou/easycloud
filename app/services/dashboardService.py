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


def share_directory(
        dirname: str,
        target_login: str,
        action: str = "read",
        db: Session = Depends(dependencies.get_db),
        current_user: User = Depends(dependencies.get_current_user)
):
    target_user = db.query(User).filter_by(login=target_login).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    if target_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Can't share to yourself")

    user_dir_path = os.path.abspath(os.path.join(config.BASE_DIR, current_user.login))
    target_dir_path = os.path.abspath(os.path.join(user_dir_path, dirname))

    if not target_dir_path.startswith(user_dir_path):
        raise HTTPException(status_code=400, detail="Invalid directory name")

    if not os.path.exists(target_dir_path):
        raise HTTPException(status_code=404, detail="File or directory does not exist on disk")

    unique_dirname = f"{current_user.login}/{dirname}"

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
        path = name + content
        content_dict = {"id": str(uuid.uuid4()), "name": content, "parent_id": parent_id, "type": "file", "path": path}

        if not os.path.isfile(filepath):
            content_dict["type"] = "dir"
            files += get_files_recursive(filepath, content_dict["id"], path + "/")

        files.append(content_dict)

    return files


def get_user_files(db: Session = Depends(dependencies.get_db), user: User = Depends(dependencies.get_current_user)):
    user_dir = os.path.join(config.BASE_DIR, user.login)

    if not os.path.exists(user_dir):
        filenames = []
        os.makedirs(user_dir, exist_ok=True)
    else:
        filenames = get_files_recursive(user_dir, "filesContainer")

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

    return {"username": user.login, "files": filenames}


def get_file_path(filename: str, db: Session, user: User):
    user_prefix = user.login + "/"
    if filename.startswith(user_prefix):
        relative_filename = filename[len(user_prefix):]
    else:
        relative_filename = filename

    own_base_dir = os.path.abspath(os.path.join(config.BASE_DIR, user.login))
    own_file_path = os.path.abspath(os.path.join(own_base_dir, relative_filename))

    if own_file_path.startswith(own_base_dir) and os.path.exists(own_file_path) and os.path.isfile(own_file_path):
        return FileResponse(
            path=own_file_path,
            filename=os.path.basename(own_file_path),
            content_disposition_type="attachment"
        )

    shared_permissions = db.query(Permission).join(acl_records).filter(
        acl_records.c.user_id == user.id,
        acl_records.c.action == "read"
    ).all()

    for perm in shared_permissions:
        if filename == perm.dirname or filename.startswith(perm.dirname + "/"):
            shared_file_path = os.path.abspath(os.path.join(config.BASE_DIR, filename))
            allowed_base_dir = os.path.abspath(os.path.join(config.BASE_DIR, perm.dirname))

            if shared_file_path.startswith(allowed_base_dir) and os.path.exists(shared_file_path) and os.path.isfile(shared_file_path):
                return FileResponse(
                    path=shared_file_path,
                    filename=os.path.basename(shared_file_path),
                    content_disposition_type="attachment"
                )

    raise HTTPException(status_code=403, detail="Access denied or file not found")

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