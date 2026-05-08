from app.models.user import User
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

def get_users(db):
    users = db.query(User).all()
    return users

def add_users(name: str, surname: str, db):
    try :
        new_user = User(name=name, surname=surname)
        db.add(new_user)
        db.commit()
        return new_user
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database error: {e}")
        raise e
