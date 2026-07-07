from fastapi import APIRouter, Depends, Request
from app.config import config
from fastapi.responses import FileResponse
from app.models.dashboard import dashboardFileList
from app.services import dashboardService
import os
router = APIRouter(prefix = "/dashboard", tags = ["dashboard"])

@router.get("/")
def get_dashboard(request: Request):
    return FileResponse(path = os.path.join(config.TEMPLATE_DIR, "dashboard.html"))
@router.get("/download/{filename:path}")
def get_file(result = Depends(dashboardService.get_file_path)):
    return result

@router.get("/my", response_model = dashboardFileList)
def get_files(user_files: dict = Depends(dashboardService.get_user_files)):
    return user_files

@router.get("/download/{filename:path}")
def get_file(result: FileResponse = Depends(dashboardService.get_file_path)):
    return result

@router.post("/add-file")
async def add_file(result = Depends(dashboardService.add_new_file)):
    return result

@router.get("/delete-file/{filename:path}")
async def delete_file(result = Depends(dashboardService.delete_file)):
    return result

@router.get("/add-folder/{dirname}")
async def add_directory(result = Depends(dashboardService.add_directory)):
    return result
