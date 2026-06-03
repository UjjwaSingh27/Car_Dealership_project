import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "car-dealership-secret-key-2026")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = int(os.environ.get("DB_PORT", 3306))
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "Admin1234!")
    DB_NAME = os.environ.get("DB_NAME", "car_dealership_real")

    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
