from peewee import SqliteDatabase

SECRET_KEY = "THE_SECRET_KEY"
db = SqliteDatabase("db.sqlite3")
