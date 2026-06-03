import pymysql
from flask import g
from config import Config


def get_db():
    """Returns a MySQL database connection for the current request context."""
    if "db" not in g:
        g.db = pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )
    return g.db


def close_db(e=None):
    """Closes the database connection at end of request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()
