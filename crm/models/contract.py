from peewee import *
from crm.config import db
from .client import Client
from crm.models.user import User


class Contract(Model):
    id = AutoField(primary_key=True)
    client = ForeignKeyField(Client, backref="contracts")
    total_amount = DecimalField()
    remaining_amount = DecimalField()
    created_at = DateTimeField()
    status = BooleanField(default=False)
    commercial_contact = ForeignKeyField(User, backref="contracts")

    class Meta:
        database = db
