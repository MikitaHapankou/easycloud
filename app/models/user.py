from sqlalchemy import Column, Integer, String
from app.db.database import Base
from sqlalchemy.sql.sqltypes import TIMESTAMP

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True)
    login = Column(String(20), nullable = False, unique = True)
    password_hash = Column(String(60), nullable = False)
    created_at = Column(TIMESTAMP(timezone = True))

    def __repr__(self):
        return f"<User(login='{self.login}')>"