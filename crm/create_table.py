from peewee import SqliteDatabase

from crm.models.user import User
from crm.models.client import Client
from crm.models.contract import Contract
from crm.models.event import Event
from crm.models.role import Role
from crm.models.permission import Permission
from crm.models.rolepermission import RolePermission


db = SqliteDatabase("db.sqlite3")


def create_tables():
    db.connect()
    db.create_tables([User, Client, Contract, Event, Role, Permission, RolePermission])
    db.close()


def create_roles():
    roles = ["Commercial", "Gestion", "Support"]
    with db.atomic():
        for role in roles:
            Role.get_or_create(name=role)


def create_permissions():
    permissions = Permission.generate_permissions()
    with db.atomic():
        for permission in permissions:
            Permission.get_or_create(name=permission)

        commercial = Role.get(Role.name == "Commercial")
        gestion = Role.get(Role.name == "Gestion")
        support = Role.get(Role.name == "Support")

        for perm in Permission.select():
            if "client" in perm.name or "create-event" in perm.name:
                RolePermission.get_or_create(role=commercial, permission=perm)
            if "contract" in perm.name or "user" in perm.name:
                RolePermission.get_or_create(role=gestion, permission=perm)
            if "event" in perm.name and "create-event" not in perm.name:
                RolePermission.get_or_create(role=support, permission=perm)


def setup_database():
    create_tables()
    create_roles()
    create_permissions()


if __name__ == "__main__":
    setup_database()
