import typer
from typing_extensions import Annotated, Optional
from crm.models.client import Client
from crm.models.user import User
from datetime import datetime
from crm.auth import auth_required, check_user_and_permissions

app = typer.Typer()


def check_date(date):
    """Function to check if the date format enter by user is valid"""
    try:
        return datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        typer.echo("Non valid format: date not updated. date format : YYYY-MM-DD")
        return None


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
    """Function to create a client: python -m crm client create-client or
    python -m crm client create-client -f "first name" -l "last name" -e "email" -p "phone" -c "company name"
    """
    try:
        if user.role.name == "Admin":
            try:
                user_id = typer.prompt("Enter the user id")
                user = User.get(id=user_id)
                if not user.role.name == "Commercial":
                    typer.echo("user must be a commercial contact")
                    return
            except User.DoesNotExist:
                typer.echo("This user does not exist")
                return
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
        typer.echo("Client created succesfully")

    except Exception as e:
        return typer.echo(f"Error : {e}")


@app.command()
@auth_required
def delete_client(
    client_id: int = typer.Option(..., "-i", prompt=True, help="client id"),
    user=None,
):
    """Function to delete a client by id: python -m crm client delete-client or
    python -m crm client delete-client -i "client id" """
    try:
        if not user.role == "Admin":
            client = Client.get(id=client_id)
            if not check_user_and_permissions(
                user, "delete-client"
            ) and not user.has_permission_own(client.epic_events_contact):
                return
        client.delete_instance()
        typer.echo(f"{client.last_name} deleted succesfully")
    except Client.DoesNotExist:
        typer.echo("Client not found")
    except Exception as e:
        typer.echo(f"Error: {e}")


@app.command(name="list-clients")
@auth_required
def list_clients(user=None):
    """Function to get the list of the clients: python -m client list-clients"""
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
        "-i",
        prompt="Enter the id of the client you want to see details about",
        help="id of the client",
    ),
    user=None,
):
    """Function to get a user by id: python -m crm client get client or
    python -m crm client get-client -i "client id" """
    try:
        client = Client.get(id=client_id)
        typer.echo(
            f"Client n°{client.id}: Name: {client.first_name} {client.last_name}, Email: {client.email}, "
            f"Phone: {client.phone}, Company name: {client.company_name}, "
            f"Created at: {client.created_at}, Last_contact: {client.last_contact}"
        )
    except Client.DoesNotExist:
        typer.echo("Client not found")
    except Exception as e:
        typer.echo(f"Error: {e}")


@app.command()
@auth_required
def update_client(
    client_id: int = typer.Option(
        ...,
        "-i",
        prompt="Enter the id of the client you want to see details about",
        help="id of the client",
    ),
    user=None,
):
    """Function to update client by prompt: python -m crm client update-client -i "client id" """
    try:
        client = Client.get(id=client_id)
        if not user.role.name == "Admin":
            if not check_user_and_permissions(
                user, "update-client"
            ) or not user.has_permission_own(client.epic_events_contact):
                return

        typer.echo(
            "Client details: \n"
            f"Client n°{client.id}: Name: {client.first_name} {client.last_name}, Email:{client.email}, "
            f"Phone: {client.phone}, Company name: {client.company_name}, "
            f"Created at: {client.created_at}, Last_contact: {client.last_contact}"
        )

        first_name = typer.prompt(
            "Enter new first name or pass", default=client.first_name
        )
        last_name = typer.prompt(
            "Enter new last name or pass", default=client.last_name
        )
        email = typer.prompt("Enter new email or pass", default=client.email)
        phone = typer.prompt("Enter new phone number or pass", default=client.phone)
        company_name = typer.prompt(
            "Enter new company name or pass", default=client.company_name
        )
        new_last_contact = typer.prompt(
            "Enter new date or pass: format = YYYY-MM-DD", default=client.last_contact
        )
        last_contact_up = check_date(new_last_contact)
        if last_contact_up is not None:
            last_contact = last_contact_up
        else:
            last_contact = client.last_contact

        client.first_name = first_name
        client.last_name = last_name
        client.email = email
        client.phone = phone
        client.company_name = company_name
        client.last_contact = last_contact

        client.save()
        typer.echo("Client updated succesfully")
        typer.echo(
            "New client details: \n"
            f"Client n°{client.id}: Name: {client.first_name} {client.last_name}, Email: {client.email}, "
            f"Phone: {client.phone}, Company name: {client.company_name}, "
            f"Created at: {client.created_at}, Last_contact: {client.last_contact}"
        )

    except Client.DoesNotExist:
        typer.echo("Client not found")
        return


@app.command()
@auth_required
def update_client_direct(
    client_id: int = typer.Option(
        ...,
        "-i",
        prompt="Enter the id of the client you want to see details about",
        help="id of the client",
    ),
    first_name: Annotated[
        Optional[str], typer.Option("-f", help="First name of the client")
    ] = None,
    last_name: Annotated[
        Optional[str], typer.Option("-l", help="Last name of the client")
    ] = None,
    email: Annotated[
        Optional[str], typer.Option("-e", help="Email of the client")
    ] = None,
    phone: Annotated[
        Optional[int], typer.Option("-p", help="Phoneof the client")
    ] = None,
    company_name: Annotated[
        Optional[str], typer.Option("-c", help="Company name of the client")
    ] = None,
    last_contact: Annotated[
        Optional[str], typer.Option("-d", help="Last contact with the client")
    ] = None,
    user=None,
):
    """Function to update client by command:
    python -m crm client update-client -i "client id" -f "first name" -l "last name" -e "email" -p "phone" -c "company name" "d "last contact"
    """

    try:
        client = Client.get(id=client_id)
        if not user.role.name == "Admin":
            if not check_user_and_permissions(
                user, "update-client"
            ) or not user.has_permission_own(client.epic_events_contact):
                return

        if first_name is not None:
            client.first_name = first_name
        if last_name is not None:
            client.last_name = last_name
        if email is not None:
            client.email = email
        if phone is not None:
            client.phone = phone
        if company_name is not None:
            client.company_name = company_name
        if last_contact is not None:
            new_last_contact = check_date(last_contact)
            client.last_contact = new_last_contact

        client.save()
        typer.echo("Clien updated succesfully")
        typer.echo(
            "New client details: \n"
            f"Client n°{client.id}: Name: {client.first_name} {client.last_name}, Email: {client.email}, "
            f"Phone: {client.phone}, Company name: {client.company_name}, "
            f"Created at: {client.created_at}, Last_contact: {client.last_contact}"
        )

    except Client.DoesNotExist:
        typer.echo("Client not found")
        return


if __name__ == "__main__":
    app()
