from pydantic import BaseModel, ConfigDict

class userScheme(BaseModel):
    name: str
    surname: str

class userOutScheme(BaseModel):
    name: str
    surname: str

    model_config = ConfigDict(from_attributes=True)