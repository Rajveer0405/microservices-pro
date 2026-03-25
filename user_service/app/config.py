import os


DB_PATH = "users.db"
AUTH_SERVICE_VERIFY_URL = os.getenv("AUTH_SERVICE_VERIFY_URL", "http://127.0.0.1:8000/verify")
