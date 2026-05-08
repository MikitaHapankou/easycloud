from sqlalchemy import Column, Integer, String
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)
    surname = Column(String(20), nullable=False)

    def __repr__(self):
        return f"<User(name='{self.name}', surname'{self.surname}')>"