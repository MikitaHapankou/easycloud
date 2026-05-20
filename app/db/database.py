from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from app.config import config

import os
from sqlalchemy.orm import sessionmaker

USERNAME = os.getenv("POSTGRES_USER")
PASSWORD = os.getenv("POSTGRES_PASSWORD")
DBNAME = os.getenv("POSTGRES_DB")

engine = create_engine(config.settings.get_db_url())

Base = declarative_base()

LocalSession = sessionmaker(autocommit = False, autoflush = False, bind = engine)
