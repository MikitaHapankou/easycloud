import app.models
from app.db.database import Session, Base, engine
from app.services.userService import get_users, add_users

Base.metadata.create_all(bind=engine)
add_users(Session, "John", "Doe")
print(get_users(Session))