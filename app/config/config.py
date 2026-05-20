from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory = "app/templates")

BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "user_storage")
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR, exist_ok = True)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"))

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    JWT_SECRET: str
    JWT_EXPIRE_MINUTES: int
    JWT_ALGO: str

    def get_db_url(self):
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@localhost:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
