from fastapi import APIRouter, HTTPException, Depends, Request
from app.config import config
from fastapi.responses import FileResponse
import os
from app.models.user import User
from app.schemas.dashboard import dashboardFileList
from app import dependencies
import aiofiles, aiofiles.os
from app.services import dashboardService
router = APIRouter(prefix = "/dashboard", tags = ["dashboard"])

@router.get("/")
def get_dashboard(request: Request):
    return config.templates.TemplateResponse(
        request = request,
        name = "dashboard.html"
    )

@router.get("/my", response_model = dashboardFileList)
def get_files(user_files: dict = Depends(dashboardService.get_user_files)):
    return user_files

@router.get("/download/{file}")
def get_dashboard(file: str, file_path: str = Depends(dashboardService.get_file_path)):
    return FileResponse(file_path, filename = file)

@router.post("/add-file")
async def add_file(result = Depends(dashboardService.add_new_file)):
    return result

@router.get("/delete-file/{filename}")
async def delete_file(filename: str, user: User = Depends(dependencies.get_current_user)):
    real_file_path = os.path.join(config.BASE_DIR, user.login, filename)

    isfile = await aiofiles.os.path.isfile(real_file_path)
    if not isfile: raise HTTPException(status_code = 404, detail = "File not found")

    await aiofiles.os.remove(real_file_path)

    return "Success"
@router.get("/add-folder/{dirname}")
async def add_directory(dirname: str, user: User = Depends(dependencies.get_current_user)):
    dir_path = os.path.join(config.BASE_DIR, user.login, dirname)

    if os.path.exists(dir_path): raise HTTPException(status_code = 404, detail = "Directory already exists")

    await aiofiles.os.mkdir(dir_path)

    return "Success"
