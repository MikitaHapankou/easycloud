from app.models.user import User
from sqlalchemy.orm import Session

def get_users(db: Session):
    session = db()
    users = session.query(User).first()
    session.close()
    return users

def add_users(db: Session, name: str, surname: str):
    session = db()
    new_user = User(name=name, surname=surname)
    session.add(new_user)
    session.commit()
    session.close()