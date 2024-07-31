import pytest
from peewee import IntegrityError
from crm.models.event import Event
from crm.models.contract import Contract


def test_create_event(setup_db, user1):
    with setup_db.atomic():
        contract = Contract.get(id=4)
        event = Event.create(
            name="JO",
            contract=contract,
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


def test_create_event_invalid_data(user1):
    with pytest.raises(IntegrityError):
        contract = Contract.get(id=4)
        Event.create(
            contract=contract,
            start_date="2024-07-26",
            end_date="2024-08-11",
            support_contact=user1,
        )
