from peewee import (
    Model,
    AutoField,
    CharField,
    ForeignKeyField,
    DateTimeField,
    TextField,
    IntegerField,
)
from .contract import Contract
from .user import User
from crm.config import db


class Event(Model):
    id = AutoField(primary_key=True)
    name = CharField(max_length=255)
    contract = ForeignKeyField(Contract, backref="events")
    start_date = DateTimeField()
    end_date = DateTimeField()
    support_contact = ForeignKeyField(User, backref="events", null=True)
    location = CharField()
    attendees = IntegerField()
    notes = TextField()

    class Meta:
        database = db
