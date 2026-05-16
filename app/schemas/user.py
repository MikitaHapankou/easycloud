from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Tuple
from app.models.user import User

class userRequest(BaseModel):
    login: str
    password: str

class userORM(BaseModel):
    ConfigDict(from_attributes = True)

    login: str
    password_hash: str

class userOutScheme(BaseModel):
    user_list: List[userORM]

