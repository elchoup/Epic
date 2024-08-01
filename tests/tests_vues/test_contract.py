from typer.testing import CliRunner
from crm.__main__ import app
from crm.views.contract import find_client, sign
from crm.models.client import Client
from crm.models.contract import Contract
from io import StringIO
import contextlib

runner = CliRunner()


def test_find_client_valid(setup_db):
    with setup_db.atomic():
        result = find_client(1)
        assert result == Client.get(id=1)


def test_find_client_invalid(setup_db):
    with setup_db.atomic():
        output = StringIO()
        with contextlib.redirect_stdout(output):
            find_client(45778966)
        result = output.getvalue().strip()
        assert result == "Client not found"


def test_sign_contract_false(setup_db):
    with setup_db.atomic():
        contract = Contract.get(id=1)
        result = sign(contract)

        assert result == "No"


def test_sign_contract_true(setup_db):
    with setup_db.atomic():
        contract = Contract.get(id=2)
        result = sign(contract)

        assert result == "Yes"


def test_create_contract_valid(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(
            app,
            ["contract", "create-contract", "-i", 1, "-t", 4500, "-r", 500, "--sign"],
        )

        assert "Contract created successfully" in result.output
        assert "Contract ID: 4"
        contract = Contract.get(id=4)
        assert contract.status is True


def test_create_contract_invalid(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(
            app,
            [
                "contract",
                "create-contract",
                "-t",
                "str instead of int",
                "-i",
                1,
                "-r",
                500,
                "--sign",
            ],
        )

        assert "Error" in result.output


def test_delete_contract_valid(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(app, ["contract", "delete-contract", "-i", 1])

        assert "contract with id: 1 deleted succesfuly" in result.output


def test_delete_contract_invalid(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(app, ["contract", "delete-contract", "-i", 4528])

        assert "Contract not found" in result.output


def test_list_contracts(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(app, ["contract", "list-contracts"])
        assert "Contract n°1, Client: client1 first" in result.output
        assert "Contract n°2, Client: client2 second" in result.output


def test_list_contracts_filter(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(app, ["contract", "list-contracts", "-s", "signed"])
        assert "not signed" not in result.output


def test_get_contract_valid(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(app, ["contract", "get-contract", "-i", 1])
        assert "Contract n°1, Client: client1 first" in result.output


def test_get_contract_invalid(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(app, ["contract", "get-contract", "-i", 1000000])
        assert "Contract not found" in result.output


def test_update_contract_direct_valid(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(
            app,
            [
                "contract",
                "update-contract-direct",
                "-i",
                "1",
                "-t",
                10000,
                "-r",
                0,
                "-s",
                "sign",
            ],
        )
        assert "Contract updated succesfully" in result.output
        assert "Total amount: 10000" in result.output


def test_update_contract_direct_invalid(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(
            app,
            [
                "contract",
                "update-contract-direct",
                "-i",
                2540012,
                "-t",
                10000,
                "-r",
                0,
                "-s",
                "sign",
            ],
        )
        assert "Contract not found" in result.output


def test_update_contract_valid(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(
            app, ["contract", "update-contract", "-i", 1], input=" \n10000\n0\ny\ny\n"
        )

        contract = Contract.get(id=1)
        assert contract.total_amount == 10000
        assert contract.remaining_amount == 0
        assert contract.status is True

        assert "Contract n°1" in result.output
        assert "Total amount: 10000" in result.output
        assert "Remaining amount: 0" in result.output


def test_update_contract_invalid(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(
            app,
            ["contract", "update-contract", "-i", 45892],
            input=" \n10000\n0\ny\ny\n",
        )
        assert "Contract not found" in result.output
