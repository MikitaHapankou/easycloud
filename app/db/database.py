from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

USERNAME = os.getenv("POSTGRES_USER")
PASSWORD = os.getenv("POSTGRES_PASSWORD")
DBNAME = os.getenv("POSTGRES_DB")

engine = create_engine(f"postgresql://{USERNAME}:{PASSWORD}@localhost:5432/{DBNAME}")