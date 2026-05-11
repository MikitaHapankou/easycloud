#config
from dotenv import load_dotenv


load_dotenv()

# Fastapi
from fastapi import FastAPI, Request
from app.routers import userRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

#Database
from app.db.database import Base, engine


app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

app.include_router(userRouter.router)

Base.metadata.create_all(bind=engine)

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request
        }
    )

@app.get("/register", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request
        }
    )
