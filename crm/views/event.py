import typer
from typing_extensions import Annotated
from crm.models.contract import Contract
from crm.models.event import Event
from crm.models.user import User
from datetime import datetime, date
from crm.auth import auth_required, check_user_and_permissions

app = typer.Typer()


def find_contract():
    contract_id = typer.prompt("Enter the id of the contract")
    try:
        contract = Contract.get(id=contract_id)
    except Contract.DoesNotExist:
        typer.echo("Contrat non trouvé")
        return
    return contract


def find_user():
    user_id = typer.prompt("Enter the id of the support user")
    try:
        user = User.get(id=user_id)
        if not user.role.name == "Support":
            typer.echo("Only a support user can be assigned")
            return
    except User.DoesNotExist:
        typer.echo("User not found")
        return
    return user


def prompt_date(prompt_text):
    while True:
        date_str = typer.prompt(prompt_text)
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            typer.echo("Format de date non valid try : YYYY-MM-DD")


@app.command()
@auth_required
def create_event(
    name: Annotated[str, typer.Option("-na", prompt=True, help="Name of the event")],
    location: Annotated[
        str, typer.Option("-l", prompt=True, help="location of the event")
    ],
    attendees: Annotated[
        int, typer.Option("-a", prompt=True, help="number of attendees")
    ],
    notes: Annotated[str, typer.Option("-no", prompt=True, help="notes")],
    user=None,
):
    try:
        if not check_user_and_permissions(user, "create-event"):
            return
        support_contact = find_user()
        contract = find_contract()
        if not user.has_permission_own(contract.commercial_contact):
            return
        start_date = prompt_date("Start date YYYY-MM-DD")
        end_date = prompt_date("End date YYYY-MM-DD")
        existing_event = Event.select().where(Event.contract == contract).first()
        if existing_event:
            typer.echo("Un événement existe déjà pour ce contrat.")
            return
        event = Event.create(
            name=name,
            contract=contract,
            location=location,
            attendees=attendees,
            notes=notes,
            start_date=start_date,
            end_date=end_date,
            support_contact=support_contact,
        )
        typer.echo("Event created succesfully")
        typer.echo(f"Event id: {event.id}")
    except Exception as e:
        typer.echo(f"Error {e}")


@app.command()
@auth_required
def delete_event(
    event_id: int = typer.Option(..., "-i", prompt=True, help="id of the event"),
    user=None,
):
    try:
        if not check_user_and_permissions(user, "delete-event"):
            return
        event = Event.get(id=event_id)
        if not user.has_permission_own(event.support_contact):
            return
        event.delete_instance()
        typer.echo(f"Event with id : {event_id} deleted succesfully")
    except Event.DoesNotExist:
        typer.echo("Event not found")
    except Exception as e:
        typer.echo(f"error: {e}")


@app.command(name="list-events")
@auth_required
def list_events(user=None):
    try:
        if not check_user_and_permissions(user, "list-event"):
            return
        events = Event.select()
        if not events:
            typer.echo("No events in the database")
            return
        for event in events:
            typer.echo(
                f"Events n°{event.id}: Name: {event.name}, Contract n°: {event.contract.id}, "
                f"Location: {event.location}, Attendees: {event.attendees}, "
                f"Notes: {event.notes}, Start date: {event.start_date}, End date: {event.end_date}"
            )
    except Exception as e:
        typer.echo(f"Error: {e}")


@app.command()
@auth_required
def get_event(
    event_id: int = typer.Option(
        ...,
        "-i",
        prompt="Enter id of the event you want to see the details of",
        help="ID of the event",
    ),
    user=None,
):
    try:
        if not check_user_and_permissions(user, "get-event"):
            return
        event = Event.get(id=event_id)
        typer.echo(
            f"Events n°{event.id}: Name: {event.name}, Contract n°: {event.contract.id}, "
            f"Location: {event.location}, Attendees: {event.attendees}, "
            f"Notes: {event.notes}, Start date: {event.start_date}, End date: {event.end_date}"
        )
    except Event.DoesNotExist:
        typer.echo("Event not found")
    except Exception as e:
        typer.echo(f"Error: {e}")


@app.command()
@auth_required
def update_event(
    event_id: int = typer.Option(
        ...,
        "-i",
        prompt="Enter id of the event you want to see the details of",
        help="ID of the event",
    ),
    user=None,
):
    try:
        if not check_user_and_permissions(user, "update-event"):
            return
        event = Event.get(id=event_id)
        if not user.has_permission_own(event.support_contact):
            return
        typer.echo(
            f"Details of event n°{event.id}"
            f"Events n°{event.id}: Name: {event.name}, Contract n°: {event.contract.id}, "
            f"Location: {event.location}, Attendees: {event.attendees}, "
            f"Notes: {event.notes}, Start date: {event.start_date}, End date: {event.end_date}"
        )

        change_contract = typer.confirm(
            f"Current contract for the event is {event.contract.id} "
            "DO you want to change it ?",
            default=False,
        )

        if change_contract:
            new_contract = find_contract()
            event.contract = new_contract
            event.contract.save()

        name = typer.prompt(
            f"Current name is {event.name}. Enter a new name or pass with enter",
            default=event.name,
        )

        location = typer.prompt(
            f"Current location is {event.location}. Enter a new location or pass with enter",
            default=event.location,
        )

        attendees = typer.prompt(
            f"Current number of attendees is {event.attendees}. Enter a new number or pass with enter",
            default=event.attendees,
        )

        notes = typer.prompt(
            f"Current note is {event.notes}. Enter a new note or pass with enter",
            default=event.notes,
        )

        start_date_change = typer.confirm(
            f"Current start date is {event.start_date}. Do you want to change it ?",
            default=False,
        )

        if start_date_change:
            new_start_date = prompt_date("Start date YYYY-MM-DD")
        else:
            new_start_date = event.start_date

        end_date_change = typer.confirm(
            f"Current end date is {event.end_date}. Do you want to change it ?",
            default=False,
        )

        if end_date_change:
            new_end_date = prompt_date("End date YYYY-MM-DD")
        else:
            new_end_date = event.end_date

        event.name = name
        event.location = location
        event.attendees = attendees
        event.notes = notes
        event.start_date = new_start_date
        event.end_date = new_end_date

        event.save()
        typer.echo("Event updated succesfully")

        typer.echo(
            f"Details of the updated event n°{event.id}: "
            f"Events n°{event.id}: Name: {event.name}, Contract n°: {event.contract.id}, "
            f"Location: {event.location}, Attendees: {event.attendees}, "
            f"Notes: {event.notes}, Start date: {event.start_date}, End date: {event.end_date}"
        )

    except Event.DoesNotExist:
        typer.echo("Event not found")

    except Exception as e:
        typer.echo(f"Error: {e}")


if __name__ == "__main__":
    app()
