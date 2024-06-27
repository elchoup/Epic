from peewee import *
from . import db


class Role(Model):
    name = CharField(unique=True)

    class Meta:
        database = db
