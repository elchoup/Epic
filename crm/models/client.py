from peewee import *
from datetime import datetime
from crm.config import db
from .user import User


class Client(Model):
    first_name = CharField(max_length=255)
    last_name = CharField(max_length=255)
    email = CharField(max_length=255, unique=True)
    phone = CharField(max_length=20)
    company_name = CharField(max_length=255)
    created_at = DateTimeField(default=datetime.now())
    last_contact = DateTimeField(default=datetime.now())
    epic_events_contact = ForeignKeyField(User, backref="clients")

    class Meta:
        database = db
