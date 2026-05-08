from fastapi import FastAPI, APIRouter

app = FastAPI()
router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
def read_root():
    return {"User:" "World"}
