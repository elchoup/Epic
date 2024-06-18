from peewee import *
from . import db
from .client import Client


class Contract(Model):
    id = AutoField(primary_key=True)
    client = ForeignKeyField(Client, backref="contracts")
    total_amount = DecimalField()
    remaining_amount = DecimalField()
    created_at = DateTimeField()
    status = BooleanField(default=False)

    class Meta:
        database = db
