from pydantic import BaseModel

class userRequest(BaseModel):
    login: str
    password: str

class CurrentUser(BaseModel):
    login: str
    token: str