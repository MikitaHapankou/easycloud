from fastapi import APIRouter, Depends, Request
from app.config import config
from fastapi.responses import FileResponse
from app.schemas.dashboard import dashboardFileList
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
def get_file(file: str, file_path: str = Depends(dashboardService.get_file_path)):
    return FileResponse(file_path, filename = file)

@router.post("/add-file")
async def add_file(result = Depends(dashboardService.add_new_file)):
    return result

@router.get("/delete-file/{filename}")
async def delete_file(result = Depends(dashboardService.delete_file)):
    return result

@router.get("/add-folder/{dirname}")
async def add_directory(result = Depends(dashboardService.add_directory)):
    return result
