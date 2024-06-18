from peewee import *
from . import db
from .user import User


class Client(Model):
    first_name = CharField(max_length=255)
    last_name = CharField(max_length=255)
    email = CharField(max_length=255, unique=True)
    phone = CharField(max_length=20)
    company_name = CharField(max_length=255)
    created_at = DateTimeField()
    last_contact = DateTimeField()
    epic_events_contact = ForeignKeyField(User, backref="clients", null=True)

    class Meta:
        database = db
