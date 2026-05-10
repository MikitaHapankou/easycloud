#config
from dotenv import load_dotenv


load_dotenv()

# Fastapi
from fastapi import FastAPI
from app.routers import userRouter

#Database
from app.db.database import Base, engine


app = FastAPI()

app.include_router(userRouter.router)

Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"hello"}
