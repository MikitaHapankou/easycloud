from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.models.acl import acl_records

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True)
    login = Column(String(20), nullable = False, unique = True)
    role = Column(String(10), nullable = False)
    password_hash = Column(String(60), nullable = False)
    created_at = Column(TIMESTAMP(timezone = True))

    shared_directories = relationship(
        "Permission",
        secondary=acl_records,
        back_populates="authorized_users"
    )

    def __repr__(self):
        return f"<User(login='{self.login}')>"