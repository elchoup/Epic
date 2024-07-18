from peewee import SqliteDatabase
import bcrypt
from crm.models.user import User
from crm.models.client import Client
from crm.models.contract import Contract
from crm.models.event import Event
from crm.models.role import Role
from crm.models.permission import Permission
from crm.models.rolepermission import RolePermission


db = SqliteDatabase("db.sqlite3")


def create_tables():
    """Function to create tables"""
    db.connect()
    db.create_tables([User, Client, Contract, Event, Role, Permission, RolePermission])
    db.close()


def create_roles():
    """Function to create roles"""
    roles = ["Commercial", "Gestion", "Support", "Admin"]
    with db.atomic():
        for role in roles:
            Role.get_or_create(name=role)


def create_users():
    """Function to create exemple users"""
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
    )

    contract3 = Contract.get_or_create(
        client=client3,
        total_amount=5000,
        remaining_amount=2500,
        commercial_contact=client3.epic_events_contact,
    )

    return contract1, contract2, contract3


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
    with db.atomic():
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


def setup_database():
    create_tables()
    create_roles()
    create_users()
    create_clients()
    create_contracts()
    create_events()
    create_permissions()


if __name__ == "__main__":
    setup_database()
