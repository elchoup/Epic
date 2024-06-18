from peewee import SqliteDatabase

from models.user import User
from models.client import Client
from models.contract import Contract
from models.event import Event
from models.role import Role


def create_table():
    db = SqliteDatabase("db.sqlite3")
    db.connect()
    db.create_tables([User, Client, Contract, Event, Role])
    db.close()
