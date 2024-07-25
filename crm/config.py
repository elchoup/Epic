from peewee import SqliteDatabase
import os

SECRET_KEY = SECRET_KEY = os.getenv("SECRET_KEY")

if SECRET_KEY is None:
    raise ValueError("No SECRET_KEY set for this application")


db = SqliteDatabase("db.sqlite3")
