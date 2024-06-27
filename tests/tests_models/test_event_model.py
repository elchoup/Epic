import pytest
from peewee import IntegrityError
from test_config import setup_db, contract1, user1
from crm.models.event import Event


def test_create_event(setup_db, contract1, user1):
    with setup_db.atomic():
        event = Event.create(
            name="JO",
            contract=contract1,
            start_date="2024-07-26",
            end_date="2024-08-11",
            support_contact=user1,
            location="Paris",
            attendees="15000000",
            notes="Be careful",
        )

        assert event.name == "JO"
        assert event.contract.total_amount == 15000
        assert event.start_date == "2024-07-26"
        assert event.end_date == "2024-08-11"
        assert event.support_contact.name == "Jean"
        assert event.location == "Paris"
        assert event.attendees == "15000000"
        assert event.notes == "Be careful"


def test_create_event_invalid_data(contract1, user1):
    with pytest.raises(IntegrityError):
        Event.create(
            name="JO",
            contract=contract1,
            start_date="2024-07-26",
            end_date="2024-08-11",
            support_contact=user1,
        )
