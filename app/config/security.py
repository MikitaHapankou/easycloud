import os

BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "user_storage")
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR, exist_ok = True)