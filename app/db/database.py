from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from app.config import config
from sqlalchemy.orm import sessionmaker

USERNAME = config.settings.POSTGRES_USER
PASSWORD = config.settings.POSTGRES_PASSWORD
DBNAME = config.settings.POSTGRES_DB

engine = create_engine(config.settings.get_db_url())

Base = declarative_base()

LocalSession = sessionmaker(autocommit = False, autoflush = False, bind = engine)
