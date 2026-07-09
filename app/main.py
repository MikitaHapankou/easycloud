# Fastapi
from fastapi import FastAPI, Request
from app.routers import userRouter, dashboardRouter
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

#Database
from app.db.database import Base, engine
from supabase import AuthError

from app.config import config
from app.dependencies import raise_auth_error
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/templates"), name="static")
app.include_router(userRouter.router)
app.include_router(dashboardRouter.router)

Base.metadata.create_all(bind = engine)

@app.exception_handler(Exception)
async def internal_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code = 500,
        content = {
            "detail": "Internal server error"
        }
    )

@app.exception_handler(AuthError)
async def auth_error_handler(request: Request, exc: AuthError):
    raise_auth_error(exc)

@app.get("/", response_class = RedirectResponse)
def read_root(request: Request):
    return RedirectResponse(url = "/login")

@app.get("/login", response_class = FileResponse)
def read_login(request: Request):
    return FileResponse(os.path.join(config.TEMPLATE_DIR, "login.html"))

@app.get("/register", response_class = FileResponse)
def read_register(request: Request):
    return FileResponse(os.path.join(config.TEMPLATE_DIR, "register.html"))
