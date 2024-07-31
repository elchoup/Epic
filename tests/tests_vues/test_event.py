from typer.testing import CliRunner
from crm.__main__ import app
from crm.views.event import find_contract
from crm.models.contract import Contract
from crm.models.event import Event
from unittest.mock import patch

runner = CliRunner()


def test_find_contract_valid(setup_db):
    with setup_db.atomic():
        contract = Contract.get(id=1)
        result = find_contract(1)

        assert result == contract


def test_find_contract_invalid(setup_db):
    with setup_db.atomic():
        with patch("typer.echo") as mock_echo:
            result = find_contract(15000025)

    assert result is None
    mock_echo.assert_called_once_with("Contract not found")


def test_create_event_valid(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(
            app,
            [
                "event",
                "create-event",
                "-na",
                "JO",
                "-l",
                "Paris",
                "-a",
                1500000,
                "-ic",
                4,
            ],
            input="2024-07-26\n2024-08-11\n",
        )

        assert "Event created succesfully" in result.output
        assert "Event id: 4" in result.output


def test_create_event_not_signed(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(
            app,
            [
                "event",
                "create-event",
                "-na",
                "JO",
                "-l",
                "Paris",
                "-a",
                1500000,
                "-ic",
                5,
            ],
            input="2024-07-26\n2024-08-11\n",
        )

        assert "Contract must be sign to create an event" in result.output


def test_create_event_not_unique(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(
            app,
            [
                "event",
                "create-event",
                "-na",
                "JO",
                "-l",
                "Paris",
                "-a",
                1500000,
                "-ic",
                2,
            ],
            input="2024-07-26\n2024-08-11\n",
        )

        assert "An event already exist for this contract." in result.output


def test_delete_event_valid(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(app, ["event", "delete-event", "-i", 1])

        assert "Event with id : 1 deleted succesfully" in result.output


def test_delete_event_invalid(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(app, ["event", "delete-event", "-i", 458799885])

        assert "Event not found" in result.output


def test_list_events_valid(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(app, ["event", "list-events"])

        assert "event1" in result.output
        assert "event2" in result.output
        assert "event3" in result.output


def test_list_events_filtered(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(app, ["event", "list-events", "-s", "Sup"])

        assert "event1" not in result.output
        assert "event2" in result.output
        assert "event3" in result.output


def test_get_event_valid(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(app, ["event", "get-event", "-i", 1])

        assert "event1" in result.output


def test_get_event_invalid(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(app, ["event", "get-event", "-i", "not int"])

        assert "Error" in result.output


def test_update_event_direct_valid(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(
            app,
            [
                "event",
                "update-event-direct",
                "-i",
                2,
                "-n",
                "EVENT2",
                "-no",
                "Notes for event2",
            ],
        )
        assert "EVENT2" in result.output
        assert "Notes for event2" in result.output


def test_update_event_direct_invalid(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(
            app,
            [
                "event",
                "update-event-direct",
                "-i",
                2,
                "-n",
                "EVENT1",
                "-a",
                "str instead of int" "-no",
                "Notes for event2",
            ],
        )
        assert "Error" in result.output


def test_update_event_valid(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(
            app,
            [
                "event",
                "update-event",
                "-i",
                2,
            ],
            input="\n\nEVENT2\nPARIS\n150\n",
        )
        assert "EVENT2" in result.output
        assert "PARIS" in result.output
        assert "150" in result.output
