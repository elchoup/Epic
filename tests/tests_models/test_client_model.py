import pytest
from peewee import IntegrityError
from crm.models.client import Client


def test_create_client(setup_db, user2):
    with setup_db.atomic():
        client = Client.create(
            first_name="Tom",
            last_name="Cruise",
            email="top-gun@gmail.com",
            phone="0011223344",
            company_name="Top Gun company",
            created_at="2024-06-24 16:39:00",
            last_contact="2024-06-24 16:39:00",
            epic_events_contact=user2,
        )

        assert client.first_name == "Tom"
        assert client.last_name == "Cruise"
        assert client.email == "top-gun@gmail.com"
        assert client.phone == "0011223344"
        assert client.company_name == "Top Gun company"
        assert client.epic_events_contact.name == "Com"


def test_duplicate_email_client(setup_db, user2):
    with setup_db.atomic():
        Client.create(
            first_name="Tom",
            last_name="Cruise",
            email="top-gun@gmail.com",
            phone="0011223344",
            company_name="Top Gun company",
            created_at="2024-06-24 16:39:00",
            last_contact="2024-06-24 16:39:00",
            epic_events_contact=user2,
        )

        with pytest.raises(IntegrityError):
            Client.create(
                first_name="Tom",
                last_name="Cruise",
                email="top-gun@gmail.com",
                phone="0011223344",
                company_name="Top Gun company",
                created_at="2024-06-24 16:39:00",
                last_contact="2024-06-24 16:39:00",
                epic_events_contact=user2,
            )
