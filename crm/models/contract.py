from peewee import *
from datetime import datetime
from crm.config import db
from .client import Client
from crm.models.user import User


class Contract(Model):
    id = AutoField(primary_key=True)
    client = ForeignKeyField(Client, backref="contracts")
    total_amount = DecimalField()
    remaining_amount = DecimalField()
    created_at = DateTimeField(default=datetime.now())
    status = BooleanField(default=False)
    commercial_contact = ForeignKeyField(User, backref="contracts")

    class Meta:
        database = db
