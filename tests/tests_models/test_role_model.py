import pytest
from peewee import IntegrityError
from crm.models.role import Role
from tests.test_config import setup_db


def test_create_role(setup_db):
    with setup_db:
        role = Role.create(name="commercial")
        assert role.name == "commercial"
        assert role.id is not None


def test_dupicate_role(setup_db):
    with setup_db:
        Role.create(name="commercial")
        with pytest.raises(IntegrityError):
            Role.create(name="commercial")
