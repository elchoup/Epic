import pytest
import bcrypt
from peewee import SqliteDatabase
from crm.models.user import User
from crm.models.role import Role
from crm.models.client import Client
from crm.models.contract import Contract
from crm.models.event import Event

test_db = SqliteDatabase(":memory:")


@pytest.fixture
def setup_db():
    # Link models to database
    test_db.bind(
        [
            User,
            Role,
            Client,
            Contract,
            Event,
        ]
    )
    test_db.connect()
    test_db.create_tables(
        [
            User,
            Role,
            Client,
            Contract,
            Event,
        ]
    )
    yield test_db
    # Clean database
    test_db.drop_tables(
        [
            User,
            Role,
            Client,
            Contract,
            Event,
        ]
    )
    test_db.close()


@pytest.fixture
def user1(setup_db):
    with setup_db.atomic():
        role = Role.create(name="support")
        user = User.create(
            name="Jean", email="jean@gmail.com", password="jean", role=role
        )
        yield user


@pytest.fixture
def client1(setup_db):
    with setup_db.atomic():
        client = Client.create(
            first_name="Tom",
            last_name="Cruise",
            email="top-gun@gmail.com",
            phone="0011223344",
            company_name="Top Gun company",
            created_at="2024-06-24 16:39:00",
            last_contact="2024-06-24 16:39:00",
        )
        yield client


@pytest.fixture
def contract1(setup_db):
    with setup_db.atomic():
        client = Client.create(
            first_name="Tom",
            last_name="Cruise",
            email="top-gun@gmail.com",
            phone="0011223344",
            company_name="Top Gun company",
            created_at="2024-06-24 16:39:00",
            last_contact="2024-06-24 16:39:00",
        )
        contract = Contract.create(
            client=client,
            total_amount=15000,
            remaining_amount=5000,
            created_at="2024-06-24 17:00:00",
        )
        yield contract


@pytest.fixture
def user2(setup_db):
    """Creation of a role to create a user then log him in"""
    with setup_db.atomic():
        role, _ = Role.get_or_create(name="commercial")
        user_data = {
            "name": "Jean",
            "email": "jean@gmail.com",
            "password": bcrypt.hashpw("jean".encode(), bcrypt.gensalt()).decode(),
            "role": role.id,
        }
        user = User.create(**user_data)
        yield user


@pytest.fixture
def user3(setup_db):
    """Creation of a role to create a user then log him in"""
    with setup_db.atomic():
        role, _ = Role.get_or_create(name="commercial")
        user_data = {
            "name": "Carlos",
            "email": "carlos@gmail.com",
            "password": bcrypt.hashpw("carlositos".encode(), bcrypt.gensalt()).decode(),
            "role": role.id,
        }
        user = User.create(**user_data)
        yield user
