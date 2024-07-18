import pytest
from peewee import IntegrityError
from crm.models.user import User
from crm.models.role import Role


def test_create_user(setup_db):
    with setup_db.atomic():
        role = Role.create(name="commercial")

        user = User.create(
            name="Alain", email="alain@gmail.com", password="Ducasse4ever", role=role
        )

        assert user.name == "Alain"
        assert user.email == "alain@gmail.com"
        assert user.password == "Ducasse4ever"
        assert user.role.name == "commercial"


def test_dupicate_user_email(setup_db):
    with setup_db.atomic():
        role = Role.create(name="commercial")
        User.create(
            name="Alain", email="alain@gmail.com", password="Ducasse4ever", role=role
        )
        with pytest.raises(IntegrityError):
            User.create(
                name="Alain",
                email="alain@gmail.com",
                password="Ducasse4ever",
                role=role,
            )
