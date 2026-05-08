from pydantic import BaseModel, ConfigDict

class userRequest(BaseModel):
    name: str
    password: str

class userOutScheme(BaseModel):
    login: str
    password_hash: str

    model_config = ConfigDict(from_attributes=True)
