from pydantic import BaseModel, ConfigDict

class userRequest(BaseModel):
    login: str
    password: str

class userOutScheme(BaseModel):
    login: str
    password_hash: str

    model_config = ConfigDict(from_attributes=True)
