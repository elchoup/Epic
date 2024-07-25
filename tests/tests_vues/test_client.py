from typer.testing import CliRunner
import pytest
from crm.models.client import Client
from crm.views.client import check_date
from datetime import date, datetime
from io import StringIO
from crm.__main__ import app

runner = CliRunner()


def test_check_date_valid():
    date_str = "2024-11-25"
    expected_date = date(2024, 11, 25)
    result = check_date(date_str)
    assert result == expected_date


def test_check_date_wrong():
    date_str = "wrong date"
    result = check_date(date_str)
    assert result == None


def test_create_client_valid(setup_db):
    with setup_db.atomic():
        result = runner.invoke(
            app,
            [
                "client",
                "create-client",
                "-f",
                "valid",
                "-l",
                "client",
                "-e",
                "valid@gmail.com",
                "-p",
                "0123456",
                "-c",
                "Valid&co",
            ],
            input="1\n",
        )

        assert "Client created succesfully" in result.output


def test_create_client_wrong_value(setup_db):
    with setup_db.atomic():
        result = runner.invoke(
            app,
            [
                "client",
                "create-client",
                "-f",
                "valid",
                "-l",
                "client",
                "-e",
                "wrong maim",
                "-p",
                "str for int",
                "-c",
                "Valid&co",
            ],
            input="1\n",
        )

        assert "Error" in result.output


def test_delete_client_valid(setup_db):
    with setup_db.atomic():
        result = runner.invoke(app, ["client", "delete-client", "-i", 1])
        assert "first deleted succesfully" in result.output


def test_delete_client_no_exist(setup_db):
    with setup_db.atomic():
        result = runner.invoke(app, ["client", "delete-client", "-i", 45])
        assert "Client not found" in result.output


def test_list_clients(setup_db):
    with setup_db.atomic():
        result = runner.invoke(app, ["client", "list-clients"])
        assert "Client n°1: Name: client1" in result.output
        assert "Company name: client3&co" in result.output


def test_get_client_valid(setup_db):
    with setup_db.atomic():
        result = runner.invoke(app, ["client", "get-client", "-i", 1])
        assert (
            "Client n°1: Name: client1 first, Email: client1@gmail.com" in result.output
        )


def test_get_client_invalid(setup_db):
    with setup_db.atomic():
        result = runner.invoke(app, ["client", "get-client", "-i", 10145])
        assert "Client not found" in result.output


def test_update_client_direct_valid(setup_db):
    with setup_db.atomic():
        result = runner.invoke(
            app,
            [
                "client",
                "update-client-direct",
                "-i",
                1,
                "-f",
                "CLIENT1",
                "-l",
                "FIRST",
                "-e",
                "CLIENT1@gmail.com",
            ],
        )
        assert "Clien updated succesfully" in result.output
        assert "Name: CLIENT1 FIRST" in result.output
        assert "Email: CLIENT1@gmail.com" in result.output


def test_update_client_direct_no_exist(setup_db):
    with setup_db.atomic():
        result = runner.invoke(
            app,
            [
                "client",
                "update-client-direct",
                "-i",
                4569875,
                "-f",
                "CLIENT1",
                "-l",
                "FIRST",
                "-e",
                "CLIENT1@gmail.com",
            ],
        )
        assert "Client not found" in result.output


def test_update_client_valid(setup_db):
    with setup_db.atomic():
        result = runner.invoke(
            app,
            ["client", "update-client", "-i", 1],
            input="CLIENT1\nFIRST\nCLIENT1@gmail.com\n0123456\nclient1&co\n2024-12-31\n",
        )

        client = Client.get(id=1)
        assert client.first_name == "CLIENT1"
        assert client.last_name == "FIRST"
        assert client.email == "CLIENT1@gmail.com"
        assert client.phone == "0123456"
        assert client.company_name == "client1&co"
        assert client.last_contact == datetime(2024, 12, 31)

        assert (
            "Client n°1: Name: CLIENT1 FIRST, Email: CLIENT1@gmail.com" in result.output
        )
        assert "Phone: 0123456, Company name: client1&co" in result.output
        assert "Created at:" in result.output
        assert "Last_contact: 2024-12-31" in result.output
