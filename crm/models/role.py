from peewee import *
from . import db


class Role(Model):
    name = CharField()

    class Meta:
        database = db
