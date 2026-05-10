from app.models.user import User
from .security import hash_password, check_password

def get_users(db):
    users = db.query(User).all()
    return users

def add_user(login: str, password: str, db):
    try:
        password_hash = hash_password(password)
        new_user = User(login=login, password_hash=password_hash)
        db.add(new_user)
        db.commit()
        return new_user
    except Exception as e:
        raise e

def auth(login: str, password: str, db):
    try:
        user = db.query(User).filter_by(login = login).first()
        real_hash_string = user.password_hash
        return check_password(password, real_hash_string)

    except Exception as e:
        raise e