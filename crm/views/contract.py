import typer
import sentry_sdk
from typing_extensions import Annotated, Optional
from crm.models.contract import Contract
from crm.models.client import Client
from datetime import datetime
from crm.auth import auth_required, check_user_and_permissions


app = typer.Typer()


def find_client(client_id):
    """Function to get the client by id with a prompt"""
    try:
        client = Client.get(id=client_id)
    except Client.DoesNotExist:
        typer.echo("Client not found")
        return
    return client


def sign(contract):
    """Function to change true or false by yes or no"""
    if contract.status is True:
        return "Yes"
    else:
        return "No"


def sign_fo_sdk(contract):
    if contract.status is True:
        sentry_sdk.capture_message(f"Contract sign: {contract.id}")


def get_list(status, remain):
    """Function to filter or not the list of contracts by status or remaining amount"""
    try:
        contracts = Contract.select()
        if status is not None:
            if status.lower() == "signed":
                contracts = contracts.where(Contract.status is True)

            elif status.lower() == "not signed":
                contracts = contracts.where(Contract.status is False)

            else:
                typer.echo("Invalid status value")
                return

        if remain is not None:
            if remain.lower() == "rest to pay":
                contracts = contracts.where(Contract.remaining_amount > 0)

            elif remain == "paid":
                contracts = contracts.where(Contract.remaining_amount == 0)

            else:
                typer.echo("Invalid remain value")
                return
        return contracts
    except Contract.DoesNotExist:
        typer.echo("Contract not found")
        return


@app.command()
@auth_required
def create_contract(
    client_id: int = typer.Option(..., "-i", prompt=True, help="Id of the client"),
    total_amount: int = typer.Option(
        ..., "-t", prompt=True, help="Total amount of the contract"
    ),
    remaining_amount: int = typer.Option(
        ..., "-r", prompt=True, help="Remaining amount to be paid"
    ),
    status: bool = typer.Option(
        False,
        "--sign",
        prompt=True,
        help="Indicate if the contract is signed or not",
        is_flag=True,
    ),
    created_at: datetime = datetime.now(),
    user=None,
):
    """Function to create a contract: python -m crm contract create-contract or
    python -m crm contract create-contract -i "client id" -t "total amount" -r "remaining amount" --sign "if signed.
    AUTH REQUIRED LOGIN FIRST
    """
    try:
        if not check_user_and_permissions(user, "create-contract"):
            return
        client = find_client(client_id)

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
        sign_fo_sdk(contract)
    except Exception as e:
        typer.echo(f"Error: {e}")


@app.command()
@auth_required
def delete_contract(
    contract_id: int = typer.Option(..., "-i", prompt=True, help="id of the contract"),
    user=None,
):
    """Function to delete a contract by id:
    python -m crm contract delete-contract or python -m crm contract delete-contract -i "contract id".
    AUTH REQUIRED LOGIN FIRST
    """
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
    """Function to get the list of all contracts: python -m crm contract list-contracts or
    contract by status or remaining amount: python -m crm contract list-contracts -s "signed or not signed" -r "rest to pay or paid".
    AUTH REQUIRED LOGIN FIRST
    """
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
    """Function to get contract by id: python -m crm contract get-contract or
    python -m crm contract get-contract -i "contract id".
    AUTH REQUIRED LOGIN FIRST"""
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
        int, typer.Option(..., "-i", prompt=True, help="ID of the contract")
    ],
    user=None,
):
    """Function to update a contract by prompt: python -m crm contract update-contract or
    python -m crm contract update-contract -i "contract id" AUTH REQUIRED LOGIN FIRST"""
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
            typer.echo("Client updated successfully")
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
            sign_fo_sdk(contract)

        contract.total_amount = total_amount
        contract.remaining_amount = remaining_amount

        contract.save()
        typer.echo("Contract updated succesfully")
        typer.echo(
            f"New contract details: "
            f"Contract n°{contract.id}, Client: {contract.client.first_name} {contract.client.last_name},"
            f"Total amount: {contract.total_amount}, Remaining amount: {contract.remaining_amount},"
            f"Sign: {status}, Created at: {contract.created_at}"
        )
    except Contract.DoesNotExist:
        typer.echo("Contract not found")
    except Exception as e:
        typer.echo(f"error: {e}")


@app.command()
@auth_required
def update_contract_direct(
    contract_id: Annotated[
        int, typer.Option(..., "-i", prompt=True, help="contract id")
    ],
    client_id: Annotated[Optional[int], typer.Option("-c", help="client id")] = None,
    total_amount: Annotated[
        Optional[int], typer.Option("-t", help="total amount of the contract")
    ] = None,
    remaining_amount: Annotated[
        Optional[int], typer.Option("-r", help="remaining amount of the contract")
    ] = None,
    new_status: Annotated[
        Optional[str], typer.Option("-s", help="sign or not sign")
    ] = None,
    user=None,
):
    """Function to update a contract by command:
    python -m crm contract update-contract -i "contract id" -c "client id" -t "total amount" -r "remaining amount" -s "sign or not sign".
    AUTH REQUIRED LOGIN FIRST"""
    try:
        contract = Contract.get(id=contract_id)
        if not check_user_and_permissions(
            user, "update-contract"
        ) and not user.has_permission_own(contract.commercial_contact):
            return

        if client_id is not None:
            try:
                client = Client.get(id=client_id)
                contract.client = client
            except Client.DoesNotExist:
                typer.echo("Client not found")
                return

        if total_amount is not None:
            contract.total_amount = total_amount

        if remaining_amount is not None:
            contract.remaining_amount = remaining_amount

        if new_status is not None:
            if new_status.lower() == "signed":
                contract.status = True
                sentry_sdk.capture_message(f"Contract signed: {contract.id}")
            elif new_status.lower() == "not signed":
                contract.status = False
            else:
                typer.echo("Value of status not available status not changed")

        contract.save()
        status = sign(contract)
        typer.echo("Contract updated succesfully")
        typer.echo(
            f"New contract details: "
            f"Contract n°{contract.id}, Client: {contract.client.first_name} {contract.client.last_name},"
            f"Total amount: {contract.total_amount}, Remanining amount: {contract.remaining_amount},"
            f"Sign: {status}, Created at: {contract.created_at}"
        )
    except Contract.DoesNotExist:
        typer.echo("Contract not found")
    except Exception as e:
        typer.echo(f"error: {e}")


if __name__ == "__main__":
    app()
