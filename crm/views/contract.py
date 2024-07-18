import typer

from typing_extensions import Annotated, Optional
from crm.models.contract import Contract
from crm.models.client import Client
from datetime import datetime
from crm.auth import auth_required, check_user_and_permissions


app = typer.Typer()


def find_client():
    """Function to get the client by id with a prompt"""
    client_id = typer.prompt("Enter the id of the client")
    try:
        client = Client.get(id=client_id)
    except Client.DoesNotExist:
        typer.echo("Client non trouvé")
        return
    return client


def sign(contract):
    """Function to change true or false by yes or no"""
    if contract.status == True:
        return "Yes"
    else:
        return "No"


def get_list(status, remain):
    """Function to filter or not the list of contracts by status or remaining amount"""
    contracts = Contract.select()
    if status is not None:
        if status.lower() == "signed":
            contracts = contracts.where(Contract.status == True)
            return contracts
        elif status.lower() == "not signed":
            contracts = contracts.where(Contract.status == False)
            return contracts
        else:
            typer.echo("Invalid status value")
            return

    if remain is not None:
        if remain.lower() == "rest to pay":
            contracts = contracts.where(Contract.remaining_amount > 0)
            return contracts
        if remain == "paid":
            contracts = contracts.where(Contract.remaining_amount == 0)
            return contracts
        else:
            typer.echo("Invalid remain value")
            return
    return contracts


@app.command()
@auth_required
def create_contract(
    total_amount: int = typer.Option(
        ..., "-t", prompt=True, help="Total amount of the contract"
    ),
    remaining_amount: int = typer.Option(
        ..., "-r", prompt=True, help="Remaining amount to be paid"
    ),
    status: bool = typer.Option(
        ..., "--sign", prompt=True, help="Indicate if the contract is signed or not"
    ),
    created_at: datetime = datetime.now(),
    user=None,
):
    try:
        if not check_user_and_permissions(user, "create-contract"):
            return
        client = find_client()

        commercial_contact = client.epic_events_contact
        contract = Contract.create(
            client=client,
            total_amount=total_amount,
            remaining_amount=remaining_amount,
            status=status,
            created_at=created_at,
            commercial_contact=commercial_contact,
        )
        typer.echo("Contract created successfully")
        typer.echo(f"Contract ID: {contract.id}")
    except Exception as e:
        typer.echo(f"Error: {e}")


@app.command()
@auth_required
def delete_contract(
    contract_id: int = typer.Option(..., "-i", prompt=True, help="id of the contract"),
    user=None,
):
    try:
        contract = Contract.get(id=contract_id)
        if not check_user_and_permissions(
            user, "delete-contract"
        ) and not user.has_permission_own(contract.commercial_contact):
            return
        contract.delete_instance()
        typer.echo(f"contract with id: {contract_id} deleted succesfuly")

    except Contract.DoesNotExist:
        typer.echo("Contract not found")
    except Exception as e:
        typer.echo(f"error: {e}")


@app.command(name="list-contracts")
@auth_required
def list_contracts(
    status: Annotated[
        Optional[str],
        typer.Option("-s", help="Status of the contract (signed or not signed)"),
    ] = None,
    remain: Annotated[
        Optional[str],
        typer.Option("-r", help="Remaining amount(rest to pay or paid)"),
    ] = None,
    user=None,
):
    try:
        contracts = get_list(status, remain)
        if contracts is None:
            return
        if contracts.count() == 0:
            typer.echo("No elements found")
            return
        for contract in contracts:
            status = sign(contract)
            typer.echo(
                f"Contract n°{contract.id}, Client: {contract.client.first_name} {contract.client.last_name},"
                f"Total amount: {contract.total_amount}, Remanining_amount: {contract.remaining_amount},"
                f"Sign: {status}, Created at: {contract.created_at}"
            )
    except Exception as e:
        typer.echo(f"error: {e}")


@app.command()
@auth_required
def get_contract(
    contract_id: int = typer.Option(
        ...,
        "-i",
        prompt="Enter id of the contract you want to see details about",
        help="id of the contract",
    ),
    user=None,
):
    try:
        if not check_user_and_permissions(user, "get-contract"):
            return
        contract = Contract.get(id=contract_id)
        status = sign(contract)
        typer.echo(
            f"Contract n°{contract.id}, Client: {contract.client.first_name} {contract.client.last_name},"
            f"Total amount: {contract.total_amount}, Remanining_amount: {contract.remaining_amount},"
            f"Sign: {status}, Created at: {contract.created_at}"
        )
    except Contract.DoesNotExist:
        typer.echo("Contract not found")
    except Exception as e:
        typer.echo(f"error: {e}")


@app.command()
@auth_required
def update_contract(
    contract_id: Annotated[
        int, typer.Option(..., prompt=True, help="ID of the contract")
    ],
    user=None,
):
    try:
        contract = Contract.get(id=contract_id)
        if not check_user_and_permissions(
            user, "update-contract"
        ) and not user.has_permission_own(contract.commercial_contact):
            return
        status = sign(contract)
        typer.echo(
            "Details of the contract: "
            f"Contract n°{contract.id}, Client: {contract.client.first_name} {contract.client.last_name},"
            f"Total amount: {contract.total_amount}, Remanining_amount: {contract.remaining_amount},"
            f"Sign: {status}, Created at: {contract.created_at}"
        )

        client = typer.prompt(
            f"current client is {contract.client.first_name} {contract.client.last_name}"
            "if you want to change the client press y or press enter ?",
            default=contract.client,
        )
        if client == "y":
            new_client = find_client()
            contract.client = new_client
            contract.client.save()
            typer.echo(f"Client updated successfully")
            typer.echo(
                f"New client details: {contract.client.first_name} {contract.client.last_name}"
            )

        total_amount = typer.prompt(
            f"Current total amount is {contract.total_amount}"
            "Press a new amount or pass with enter",
            default=contract.total_amount,
        )

        remaining_amount = typer.prompt(
            f"Current remaining amount is {contract.remaining_amount}"
            "Press a new amount or pass with enter",
            default=contract.remaining_amount,
        )

        status_change = typer.confirm(
            f"Current status is {'signed' if contract.status else 'not signed'}. Do you want to change it?",
            default=contract.status,
        )

        if status_change:
            status = typer.confirm(
                "Press 'y' for signed or 'n' for not signed", default=contract.status
            )
            contract.status = status

        contract.total_amount = total_amount
        contract.remaining_amount = remaining_amount

        contract.save()
        typer.echo("Contract updated succesfully")
        typer.echo(
            f"New contract details: "
            f"Contract n°{contract.id}, Client: {contract.client.first_name} {contract.client.last_name},"
            f"Total amount: {contract.total_amount}, Remanining_amount: {contract.remaining_amount},"
            f"Sign: {status}, Created at: {contract.created_at}"
        )
    except Contract.DoesNotExist:
        typer.echo("Contract not found")
    except Exception as e:
        typer.echo(f"error: {e}")


"""@app.command()
def update_test_contract(
    contract_id: Annotated[
        int, typer.Option(..., prompt=True, help="ID of the contract")
    ],
    total_amount: Annotated[
        int, typer.Option(
        ..., "-t", prompt=True, help="Total amount of the contract"
    )],
    remaining_amount: int = typer.Option(
        ..., "-r", prompt=True, help="Remaining amount to be paid"
    ),
    status: bool = typer.Option(
        ..., "--sign", prompt=True, help="Indicate if the contract is signed or not"
    ),
    created_at: datetime = datetime.now(),
):
    try:
        contract = Contract.get(id=contract_id)
        status = sign(contract)"""


if __name__ == "__main__":
    app()
