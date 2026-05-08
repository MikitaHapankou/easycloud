import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    password_bytes = password.encode('utf-8')
    password_hash = bcrypt.hashpw(password_bytes, salt)
    hash_string = password_hash.decode('utf-8')

    return hash_string

def check_password(password: str, real_hash_string: str) -> bool:
    provided_bytes = password.encode('utf-8')
    real_bytes = real_hash_string.encode('utf-8')

    if bcrypt.checkpw(provided_bytes, real_bytes):
        return True
    else: return False