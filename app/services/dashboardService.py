import os
from app.models.user import User
from app.config import config

def get_user_files(user: User):
    user_dir = os.path.join(config.BASE_DIR, user.login)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir, exist_ok=True)
        filenames = []
    else:
        filenames = os.listdir(user_dir)

    return {"username": user.login, "files": filenames}