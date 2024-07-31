from peewee import SqliteDatabase
import os
from dotenv import load_dotenv


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

if SECRET_KEY is None:
    raise ValueError("No SECRET_KEY set for this application")

db = SqliteDatabase("db.sqlite3")
