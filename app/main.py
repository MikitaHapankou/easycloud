from fastapi import FastAPI, APIRouter
from app.routers import userRouter
app = FastAPI()
router = APIRouter()
app.include_router(userRouter.router)
@app.get("/")
def read_root():
    return {"Hello:" "World"}

@app.get("/items/{item_id}", tags = ["items"])
def read_item(item_id: int, q:str = None):
    return {"item_id": item_id, "q": q}