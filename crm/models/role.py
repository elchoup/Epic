from peewee import *
from crm.config import db


class Role(Model):
    name = CharField(unique=True)

    class Meta:
        database = db
