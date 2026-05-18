from fastapi import APIRouter, HTTPException, Depends, Request, File, UploadFile
from app.config.templates import templates
from fastapi.responses import FileResponse
from app.config.security import BASE_DIR
import os
from app.models.user import User
from app.schemas.dashboard import dashboardFileList
from app import dependencies
import aiofiles, aiofiles.os
router = APIRouter(prefix = "/dashboard", tags = ["dashboard"])

@router.get("/")
def get_dashboard(request: Request):

    return templates.TemplateResponse(
        request = request,
        name = "dashboard.html"
    )

@router.get("/my", response_model = dashboardFileList)
def get_files(user: User = Depends(dependencies.get_current_user)):
    user_dir = os.path.join(BASE_DIR, user.login)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir, exist_ok = True)
        filenames = []
    else:
        filenames = os.listdir(user_dir)

    return {"username": user.login, "files": filenames}

@router.get("/download/{file}")
def get_dashboard(file: str, user: User = Depends(dependencies.get_current_user)):
    file_path = os.path.join(BASE_DIR, user.login, file)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code = 404, detail = "File doesn't exist")

    return FileResponse(file_path, filename = file)

@router.post("/add-file")
async def add_file(uploaded_file: UploadFile = File(...), user: User = Depends(dependencies.get_current_user)):
    real_file_path = os.path.join(BASE_DIR, user.login, uploaded_file.filename)

    async with aiofiles.open(real_file_path, 'wb') as real_file:
        while chunk := await uploaded_file.read(1024 * 64):
            await real_file.write(chunk)

    return "Success"

@router.get("/delete-file/{filename}")
async def delete_file(filename: str, user: User = Depends(dependencies.get_current_user)):
    real_file_path = os.path.join(BASE_DIR, user.login, filename)

    isfile = await aiofiles.os.path.isfile(real_file_path)
    if not isfile: raise HTTPException(status_code = 404, detail = "File not found")

    await aiofiles.os.remove(real_file_path)

    return "Success"
@router.get("/add-folder/{dirname}")
async def add_directory(dirname: str, user: User = Depends(dependencies.get_current_user)):
    dir_path = os.path.join(BASE_DIR, user.login, dirname)

    if os.path.exists(dir_path): raise HTTPException(status_code = 404, detail = "Directory already exists")

    await aiofiles.os.mkdir(dir_path)

    return "Success"
