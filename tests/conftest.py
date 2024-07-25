import sys
import os
import pytest
import bcrypt
from peewee import SqliteDatabase
from typer.testing import CliRunner
from crm.models.user import User
from crm.models.role import Role
from crm.models.client import Client
from crm.models.contract import Contract
from crm.models.event import Event
from crm.models.rolepermission import RolePermission
from crm.models.permission import Permission
from crm.__main__ import app
from crm.auth import generate_token

# Ajoute le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


test_db = SqliteDatabase(":memory:")
runner = CliRunner()


@pytest.fixture
def setup_db():
    # Link models to database
    test_db.bind([User, Role, Client, Contract, Event, RolePermission, Permission])
    test_db.connect()
    test_db.create_tables(
        [User, Role, Client, Contract, Event, RolePermission, Permission]
    )

    def create_roles():
        Role.create(name="Commercial"),
        Role.create(name="Gestion"),
        Role.create(name="Support"),
        Role.create(name="Admin"),

    def create_users():
        user1 = User.get_or_create(
            name="Com",
            email="com@gmail.com",
            password=bcrypt.hashpw("com".encode(), bcrypt.gensalt()).decode(),
            role=Role.get(id=1),
        )
        user2 = User.get_or_create(
            name="Gest",
            email="gest@gmail.com",
            password=bcrypt.hashpw("gest".encode(), bcrypt.gensalt()).decode(),
            role=Role.get(id=2),
        )
        user3 = User.get_or_create(
            name="Sup",
            email="sup@gmail.com",
            password=bcrypt.hashpw("sup".encode(), bcrypt.gensalt()).decode(),
            role=Role.get(id=3),
        )
        user4 = User.get_or_create(
            name="Admin",
            email="admin@gmail.com",
            password=bcrypt.hashpw("admin".encode(), bcrypt.gensalt()).decode(),
            role=Role.get(id=4),
        )

        user5 = User.get_or_create(
            name="Com1",
            email="com1@gmail.com",
            password=bcrypt.hashpw("com1".encode(), bcrypt.gensalt()).decode(),
            role=Role.get(id=1),
        )

        return user1, user2, user3, user4, user5

    def create_clients():
        """Function to create exemple clients"""
        user1 = User.get(id=1)
        user5 = User.get(id=5)

        client1 = Client.get_or_create(
            first_name="client1",
            last_name="first",
            email="client1@gmail.com",
            phone="0123456",
            company_name="client1&co",
            epic_events_contact=user1,
        )

        client2 = Client.get_or_create(
            first_name="client2",
            last_name="second",
            email="client2@gmail.com",
            phone="0123456",
            company_name="client1&co",
            epic_events_contact=user1,
        )

        client3 = Client.get_or_create(
            first_name="client3",
            last_name="third",
            email="client3@gmail.com",
            phone="0123456",
            company_name="client3&co",
            epic_events_contact=user5,
        )

        return client1, client2, client3

    def create_contracts():
        """Function to create exemple contracts"""
        client1 = Client.get(id=1)
        client2 = Client.get(id=2)
        client3 = Client.get(id=3)

        contract1 = Contract.get_or_create(
            client=client1,
            total_amount=150000,
            remaining_amount=50000,
            commercial_contact=client1.epic_events_contact,
        )

        contract2 = Contract.get_or_create(
            client=client2,
            total_amount=10000,
            remaining_amount=0,
            commercial_contact=client2.epic_events_contact,
            status=True,
        )

        contract3 = Contract.get_or_create(
            client=client3,
            total_amount=5000,
            remaining_amount=2500,
            commercial_contact=client3.epic_events_contact,
        )

        contract4 = Contract.get_or_create(
            client=client3,
            total_amount=5000,
            remaining_amount=2500,
            commercial_contact=client3.epic_events_contact,
            status=True,
        )

        contract5 = Contract.get_or_create(
            client=client2,
            total_amount=7000,
            remaining_amount=4500,
            commercial_contact=client3.epic_events_contact,
        )

        return contract1, contract2, contract3, contract4, contract5

    def create_events():
        """Function to create exemple events"""
        contract1 = Contract.get(id=1)
        contract2 = Contract.get(id=2)
        contract3 = Contract.get(id=3)

        user3 = User.get(id=3)

        event1 = Event.get_or_create(
            name="event1",
            contract=contract1,
            start_date="2025-10-12",
            end_date="2025-12-11",
            location="paris",
            attendees=25000,
            notes="Big party coming",
        )

        event2 = Event.get_or_create(
            name="event2",
            contract=contract2,
            start_date="2025-10-11",
            end_date="2025-12-15",
            location="london",
            attendees=5000,
            notes="Speaker needed",
            support_contact=user3,
        )

        event3 = Event.get_or_create(
            name="event3",
            contract=contract3,
            start_date="2025-08-10",
            end_date="2025-10-12",
            location="spain",
            attendees=500,
            notes="checked",
            support_contact=user3,
        )

        return event1, event2, event3

    def create_permissions():
        """Function to assign permissions to the roles"""
        permissions = Permission.generate_permissions()
        for permission in permissions:
            Permission.get_or_create(name=permission)

        commercial = Role.get(Role.name == "Commercial")
        gestion = Role.get(Role.name == "Gestion")
        support = Role.get(Role.name == "Support")
        admin = Role.get(Role.name == "Admin")

        for perm in Permission.select():
            if (
                "client" in perm.name
                and "delete-client" not in perm.name
                or "create-event" in perm.name
            ):
                RolePermission.get_or_create(role=commercial, permission=perm)
            if (
                "contract" in perm.name
                and "delete-contract" not in perm.name
                or "user" in perm.name
            ):
                RolePermission.get_or_create(role=gestion, permission=perm)
            if (
                "event" in perm.name
                and "create-event" not in perm.name
                and "delete-event" not in perm.name
            ):
                RolePermission.get_or_create(role=support, permission=perm)
            if (
                "user" in perm.name
                or "client" in perm.name
                or "contract" in perm.name
                or "event" in perm.name
            ):
                RolePermission.get_or_create(role=admin, permission=perm)

    create_roles()
    create_users()
    create_clients()
    create_contracts()
    create_events()
    create_permissions()
    yield test_db
    # Clean database
    test_db.drop_tables([User, Role, Client, Contract, Event, RolePermission])
    test_db.close()


@pytest.fixture
def admin_logged():
    runner.invoke(
        app, ["user", "login", "--email", "admin@gmail.com", "--password", "admin"]
    )


@pytest.fixture
def com_logged():
    runner.invoke(
        app, ["user", "login", "--email", "com@gmail.com", "--password", "com"]
    )


@pytest.fixture
def gest_logged():
    runner.invoke(
        app, ["user", "login", "--email", "gest@gmail.com", "--password", "gest"]
    )


@pytest.fixture
def sup_logged():
    runner.invoke(
        app, ["user", "login", "--email", "sup@gmail.com", "--password", "sup"]
    )


@pytest.fixture
def user1(setup_db):
    with setup_db.atomic():
        role = Role.get(name="Support")
        user = User.create(
            name="Jean", email="jean@gmail.com", password="jean", role=role
        )
        yield user


@pytest.fixture
def user2(setup_db):
    """Creation of a role to create a user then log him in"""
    with setup_db.atomic():
        role = Role.get(name="Commercial")
        user_data = {
            "name": "Nath",
            "email": "nath@gmail.com",
            "password": bcrypt.hashpw("com".encode(), bcrypt.gensalt()).decode(),
            "role": role.id,
        }
        user = User.create(**user_data)
        yield user


@pytest.fixture
def user3(setup_db):
    """Creation of a role to create a user then log him in"""
    with setup_db.atomic():
        role = Role.get(name="Commercial")
        user_data = {
            "name": "Carlos",
            "email": "carlos@gmail.com",
            "password": bcrypt.hashpw("carlositos".encode(), bcrypt.gensalt()).decode(),
            "role": role.id,
        }
        user = User.create(**user_data)
        yield user


"""@pytest.fixture
def auth_admin_user(setup_db):
    with setup_db.atomic():
        role = Role.get(name="Admin")
        password = bcrypt.hashpw("admin".encode(), bcrypt.gensalt()).decode()
        user = User.get_or_create(
            name="Admin", email="admin@gmail.com", password=password, role=role
        )
        token = generate_token(user.id)

        yield user, token"""


@pytest.fixture
def client1(setup_db, user1):
    with setup_db.atomic():
        client = Client.create(
            first_name="Tom",
            last_name="Cruise",
            email="top-gun@gmail.com",
            phone="0011223344",
            company_name="Top Gun company",
            created_at="2024-06-24 16:39:00",
            last_contact="2024-06-24 16:39:00",
            epic_events_contact=user1,
        )
        yield client


@pytest.fixture
def contract1(setup_db, user2, client1):
    with setup_db.atomic():
        contract = Contract.create(
            id=1,
            client=client1,
            total_amount=15000,
            remaining_amount=5000,
            created_at="2024-06-24 17:00:00",
            commercial_contact=user2,
        )
        yield contract
