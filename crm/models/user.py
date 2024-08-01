from peewee import (
    Model,
    CharField,
    ForeignKeyField,
)
import typer
from crm.config import db
from crm.models.role import Role
from crm.auth import generate_token
from crm.models.permission import Permission
from crm.models.rolepermission import RolePermission


class User(Model):

    name = CharField()
    email = CharField(unique=True)
    password = CharField()
    role = ForeignKeyField(Role, backref="user")

    class Meta:
        database = db

    def generate_token(self):
        return generate_token(self.id)

    def has_permission(self, permission_name):
        permission = Permission.get_or_none(Permission.name == permission_name)
        if not permission:
            return False
        role_perm = (
            RolePermission.get_or_none(role=self.role, permission=permission)
            is not None
        )
        return role_perm

    def has_permission_own(self, contact):
        print(self.id)
        print(contact.id)
        if self.id == contact.id:
            return True
        typer.echo("Unauthorized")
        return False
