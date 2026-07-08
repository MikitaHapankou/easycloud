# Fastapi
from fastapi import FastAPI, Request
from app.routers import userRouter, dashboardRouter
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

#Database
from app.db.database import Base, engine
from app.config import config

#os
import os
app = FastAPI()

app.mount("/static", StaticFiles(directory="app/templates"), name="static")
app.include_router(userRouter.router)
app.include_router(dashboardRouter.router)

Base.metadata.create_all(bind = engine)

@app.exception_handler(Exception)
async def internal_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error"
        }
    )
@app.get("/", response_class = FileResponse)
def read_root(request: Request):
    return FileResponse(os.path.join(config.TEMPLATE_DIR, "login.html"))

@app.get("/register", response_class = FileResponse)
def read_register(request: Request):
    return FileResponse(os.path.join(config.TEMPLATE_DIR, "register.html"))
