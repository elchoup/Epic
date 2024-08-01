from peewee import (
    Model,
    CharField,
)
from crm.config import db


class Role(Model):
    name = CharField(unique=True)

    class Meta:
        database = db
