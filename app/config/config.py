from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from enum import Enum
from supabase import create_client, Client

BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "user_storage")
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")

if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR, exist_ok = True)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"))

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DATABASE_HOST: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    SUPABASE_PROJECT_URL: str
    SUPABASE_KEY: str

    def get_db_url(self):
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.DATABASE_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()

supabase: Client = create_client(settings.SUPABASE_PROJECT_URL, settings.SUPABASE_KEY)
