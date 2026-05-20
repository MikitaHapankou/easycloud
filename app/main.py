# Fastapi
from fastapi import FastAPI, Request
from app.routers import userRouter, dashboardRouter
from fastapi.responses import HTMLResponse, RedirectResponse

#Database
from app.db.database import Base, engine
from app.config import config

app = FastAPI()

app.include_router(userRouter.router)
app.include_router(dashboardRouter.router)

Base.metadata.create_all(bind = engine)

@app.get("/", response_class = HTMLResponse)
def read_root(request: Request):
    return config.templates.TemplateResponse(
        request = request,
        name = "login.html"
    )

@app.get("/register", response_class = HTMLResponse)
def read_register(request: Request):
    return config.templates.TemplateResponse(
        request = request,
        name = "register.html",
    )
