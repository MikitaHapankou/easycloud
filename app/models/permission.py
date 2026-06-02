from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql import func
from app.db.database import Base
from app.models.acl import acl_records

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    dirname = Column(String(100), nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    authorized_users = relationship(
        "User",
        secondary=acl_records,
        back_populates="shared_directories"
    )

    def __repr__(self):
        return f"<Permission(dirname='{self.dirname}')>"
