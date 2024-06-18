from peewee import *
from . import db
from .role import Role


class User(Model):

    name = CharField()
    email = CharField(unique=True)
    password = CharField()
    role = ForeignKeyField(Role, backref="user")

    class Meta:
        database = db
