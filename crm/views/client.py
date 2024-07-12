import typer
from typing_extensions import Annotated
from crm.models.client import Client
from datetime import datetime
from peewee import fn
from crm.auth import auth_required, check_user_and_permissions

app = typer.Typer()


@app.command()
@auth_required
def create_client(
    first_name: Annotated[
        str, typer.Option("-f", prompt=True, help="First_name of the client")
    ],
    last_name: Annotated[
        str, typer.Option("-l", prompt=True, help="Last_name of the client")
    ],
    email: Annotated[str, typer.Option("-e", prompt=True, help="Email of the client")],
    phone: Annotated[int, typer.Option("-p", prompt=True, help="Number of the client")],
    company_name: Annotated[
        str, typer.Option("-c", prompt=True, help="Company name of the client")
    ],
    created_at: datetime = datetime.now(),
    last_contact: datetime = datetime.now(),
    user=None,
):
    try:
        if not check_user_and_permissions(user, "create-client"):
            return

        Client.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            company_name=company_name,
            created_at=created_at,
            last_contact=last_contact,
            epic_events_contact=user,
        )
        typer.echo("Client crée avec succés")

    except Exception as e:
        return typer.echo(f"Erreur : {e}")


@app.command()
@auth_required
def delete_client(
    first_name: Annotated[
        str, typer.Option("-f", prompt=True, help="First_name of the client")
    ],
    last_name: Annotated[
        str, typer.Option("-l", prompt=True, help="Last_name of the client")
    ],
    force: Annotated[
        bool, typer.Option(prompt="Are you sure you want to delete this user?")
    ],
    user=None,
):
    if force:
        try:
            if not check_user_and_permissions(user, "delete-user"):
                return
            client = Client.get(
                fn.LOWER(Client.first_name) == first_name.lower(),
                fn.LOWER(Client.last_name) == last_name.lower(),
            )
            if not user.has_permission_own(client.epic_events_contact):
                typer.echo("Unhautorized !! You are not the contact for this client")
                return
            client.delete_instance()
            typer.echo(f"{client.last_name} deleted succesfully")
        except Client.DoesNotExist:
            typer.echo("Client not found")
        except Exception as e:
            typer.echo(f"Error: {e}")


@app.command(name="list-clients")
@auth_required
def list_clients():
    try:
        clients = Client.select()
        if not clients:
            typer.echo("clients not found")
            return
        for client in clients:
            typer.echo(
                f"Client n°{client.id}: Name: {client.first_name} {client.last_name}, Email:{client.email}, "
                f"Phone: {client.phone}, Company name: {client.company_name}, "
                f"Last_contact: {client.last_contact}"
            )
    except Exception as e:
        typer.echo(f"error: {e}")


@app.command()
@auth_required
def get_client(
    client_id: int = typer.Option(
        ...,
        prompt="Enter the id of the client you want to see details about",
        help="id of the client",
    )
):
    try:
        client = Client.get(id=client_id)
        typer.echo(
            f"Client n°{client.id}: Name: {client.first_name} {client.last_name}, Email:{client.email}, "
            f"Phone: {client.phone}, Company name: {client.company_name}, "
            f"Created at: {client.created_at}, Last_contact: {client.last_contact}"
        )
    except Client.DoesNotExist:
        typer.echo("Client not found")
    except Exception as e:
        typer.echo(f"Error: {e}")


if __name__ == "__main__":
    app()
