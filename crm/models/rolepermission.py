from peewee import (
    Model,
    ForeignKeyField,
)
from crm.config import db
from .role import Role
from .permission import Permission


class RolePermission(Model):
    role = ForeignKeyField(Role, backref="permission")
    permission = ForeignKeyField(Permission, backref="role")

    class Meta:
        database = db
