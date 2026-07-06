# Fastapi
from fastapi import FastAPI, Request
from app.routers import userRouter, dashboardRouter
from fastapi.responses import FileResponse
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

@app.get("/", response_class = FileResponse)
def read_root(request: Request):
    return FileResponse(os.path.join(config.TEMPLATE_DIR, "login.html"))

@app.get("/register", response_class = FileResponse)
def read_register(request: Request):
    return FileResponse(os.path.join(config.TEMPLATE_DIR, "register.html"))
