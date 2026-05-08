# Fastapi
from fastapi import FastAPI
from app.routers import userRouter

#Database
import app.models
from app.db.database import Base, engine
from app.services.userService import get_users, add_users

app = FastAPI()

app.include_router(userRouter.router)

Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"hello"}
