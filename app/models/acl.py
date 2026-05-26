from sqlalchemy import Column, Integer, String, ForeignKey, Table, UniqueConstraint
from app.db.database import Base

acl_records = Table(
    "acl",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False),
    Column("action", String(20), nullable=False),

    UniqueConstraint("user_id", "permission_id", "action", name="uq_user_permission_action")
)