from peewee import *
from crm.config import db


class Permission(Model):
    name = CharField()

    class Meta:
        database = db

    @staticmethod
    def generate_permissions():
        list_actions = ["get", "create", "list", "update", "delete"]
        list_models = ["user", "role", "client", "event", "contract"]

        permissions = []
        for model in list_models:
            for action in list_actions:
                permissions.append(f"{action}-{model}")
        return permissions
