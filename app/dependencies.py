from app.db.database import LocalSession
from fastapi import Cookie, HTTPException, Depends
from app.services import security
from sqlalchemy.orm import Session

def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Cookie(""), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(401)

    user = security.get_current_user(token, db)

    return user