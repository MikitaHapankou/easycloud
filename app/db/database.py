from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

import os
from sqlalchemy.orm import sessionmaker

USERNAME = os.getenv("POSTGRES_USER")
PASSWORD = os.getenv("POSTGRES_PASSWORD")
DBNAME = os.getenv("POSTGRES_DB")

engine = create_engine(f"postgresql://{USERNAME}:{PASSWORD}@localhost:5432/{DBNAME}")

Base = declarative_base()

LocalSession = sessionmaker(autocommit = False, autoflush = False, bind = engine)
