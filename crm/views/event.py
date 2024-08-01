import typer
from typing_extensions import Annotated, Optional
from crm.models.contract import Contract
from crm.models.event import Event
from crm.models.user import User
from datetime import datetime
from crm.auth import auth_required, check_user_and_permissions

app = typer.Typer()


def find_contract(contract_id):
    """function to find a contract by id from a prompt"""
    try:
        contract = Contract.get(id=contract_id)
    except Contract.DoesNotExist:
        typer.echo("Contract not found")
        return
    return contract


def find_user(user_id):
    """Function to fin a user by id from a prompt"""
    try:
        if user_id is None:
            return None
        user = User.get(id=user_id)
        if not user.role.name == "Support":
            typer.echo("Only a support user can be assigned")
            return
    except User.DoesNotExist:
        typer.echo("User not found")
        return
    return user


def prompt_date(prompt_text):
    """Function to get the date by prompt"""
    while True:
        date_str = typer.prompt(prompt_text)
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            typer.echo("Format de date non valid try : YYYY-MM-DD")
            return


def check_date(date):
    """Function to check if the date format enter by user is valid"""
    try:
        return datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        typer.echo("Non valid format: date not updated. date format : YYYY-MM-DD")
        return None


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
    contract_id: Annotated[int, typer.Option("-ic", prompt=True, help="Contract id")],
    user_id: Annotated[int, typer.Option("-iu", help="User id")] = None,
    notes: Annotated[str, typer.Option("-no", help="notes")] = "",
    user=None,
):
    """Functon to create an event: python -m crm event create-event or
    python -m crm event create-event -na "name" -l "location" -a "nbre of attendees" -ic "contract id" -iu "Optional support user id" -no "notes".
    AUTH REQUIRED LOGIN FIRST
    """
    try:
        contract = find_contract(contract_id)
        if contract.status is False:
            typer.echo("Contract must be sign to create an event")
            return
        if not check_user_and_permissions(
            user, "create-event"
        ) and not user.has_permission_own(contract.commercial_contact):
            return
        support_contact = find_user(user_id)

        start_date = prompt_date("Start date YYYY-MM-DD")
        end_date = prompt_date("End date YYYY-MM-DD")
        existing_event = Event.select().where(Event.contract == contract).first()
        if existing_event:
            typer.echo("An event already exist for this contract.")
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
    """Function to delete an event by id: python -m crm event delete-event or
    python -m crm event create-event -i "event id". AUTH REQUIRED LOGIN FIRST"""
    try:
        event = Event.get(id=event_id)
        if not check_user_and_permissions(
            user, "delete-event"
        ) and not user.has_permission_own(event.support_contact):
            return

        event.delete_instance()
        typer.echo(f"Event with id : {event_id} deleted succesfully")
    except Event.DoesNotExist:
        typer.echo("Event not found")
    except Exception as e:
        typer.echo(f"error: {e}")


@app.command(name="list-events")
@auth_required
def list_events(
    support_contact: Annotated[
        Optional[str], typer.Option("-s", help="name of the support contact")
    ] = None,
    own_events: Annotated[
        Optional[str],
        typer.Option("-o", help="filter your events: own or not yours : not own"),
    ] = None,
    support_or_not: Annotated[
        Optional[str],
        typer.Option(
            "-son",
            help="filter events with support contact or not: support for events with support"
            "and no support for the ones with no support",
        ),
    ] = None,
    user=None,
):
    """Function to get the list of all events: python -m crm event list-events or
    get events by support contact: python -m crm event list-events -s "support contact name" or
    your events only: python -m crm event list-events -o "own or not yours" or
    events with support or no support: python -m crm event list-events -son "support" or "no support".
    AUTH REQUIRED LOGIN FIRST
    """
    try:
        events = Event.select()
        if support_contact is not None:
            events = events.join(User).where(User.name == support_contact)
        if own_events is not None:
            if own_events.lower() == "own":
                events = events.where(Event.support_contact == user)
            elif own_events.lower() == "not own":
                events = events.where(Event.support_contact != user)
            else:
                typer.echo("Invalid own_events value")
                return
        if support_or_not is not None:
            if support_or_not.lower() == "support":
                events = events.where(Event.support_contact.is_null(False))
            elif support_or_not.lower() == "no support":
                events = events.where(Event.support_contact.is_null(True))
            else:
                typer.echo("Invalid values for support_or_not")
                return
        if events is None:
            typer.echo("No events found")
            return
        if not events:
            typer.echo("No events in the database")
            return

        for event in events:
            if event.support_contact is None:
                support_contact_name = ""
            else:
                support_contact_name = event.support_contact.name
            typer.echo(
                f"Events n°{event.id}: Name: {event.name}, Contract n°: {event.contract.id}, "
                f"Location: {event.location}, Attendees: {event.attendees}, "
                f"Notes: {event.notes}, Start date: {event.start_date}, End date: {event.end_date}, Support contact: {support_contact_name}"
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
    """Function to get event by id: python -m crm event get-event or
    python -m crm event get-event _i "event id".
    AUTH REQUIRED LOGIN FIRST"""
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
        prompt="Enter id of the event you want to update",
        help="ID of the event",
    ),
    user=None,
):
    """Function to update the event by prompt using id:
    python -m crm event update-event or python -m crm event update-event -i "Event id".
    AUTH REQUIRED LOGIN FIRST
    """
    try:
        event = Event.get(id=event_id)
        if not check_user_and_permissions(
            user, "update-event"
        ) and not user.has_permission_own(event.support_contact):
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
            if new_contract.status is False:
                typer.echo("Contract must be sign to create an event")
                return
            existing_event = (
                Event.select().where(Event.contract == new_contract).first()
            )
            if existing_event:
                typer.echo("An event already exist for this contract.")
                return
            event.contract = new_contract
            event.contract.save()

        change_support_contact = typer.confirm(
            "Do you want to change or add a support contact ?", default=False
        )

        if change_support_contact:
            new_support_contact = find_user()
            event.support_contact = new_support_contact
            event.support_contact.save()

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

        if event.support_contact is not None:
            support_contact_name = event.support_contact.name
        else:
            support_contact_name = ""

        typer.echo(
            f"Details of the updated event n°{event.id}: "
            f"Events n°{event.id}: Name: {event.name}, Contract n°: {event.contract.id}, "
            f"Location: {event.location}, Attendees: {event.attendees}, "
            f"Notes: {event.notes}, Start date: {event.start_date}, End date: {event.end_date}, Support contact: {support_contact_name}"
        )

    except Event.DoesNotExist:
        typer.echo("Event not found")

    except Exception as e:
        typer.echo(f"Error: {e}")


@app.command()
@auth_required
def update_event_direct(
    event_id: int = typer.Option(
        ...,
        "-i",
        prompt="Enter id of the event you want to see the details of",
        help="ID of the event",
    ),
    contract_id: Annotated[
        Optional[int], typer.Option("-c", help=" contract id")
    ] = None,
    support_contact_id: Annotated[
        Optional[int], typer.Option("-s", help="Support contact id")
    ] = None,
    name: Annotated[Optional[str], typer.Option("-n", help="Name of the event")] = None,
    location: Annotated[
        Optional[str], typer.Option("-l", help="Location of the event")
    ] = None,
    attendees: Annotated[
        Optional[int],
        typer.Option("-a", help="Number of attendees expected at the event"),
    ] = None,
    notes: Annotated[Optional[str], typer.Option("-no", help="Notes")] = None,
    start_date: Annotated[
        Optional[str], typer.Option("-sd", help="Start date of the event")
    ] = None,
    end_date: Annotated[
        Optional[str], typer.Option("-ed", help="End date of the event")
    ] = None,
    user=None,
):
    """Function to update the event by command only:
    python -m crm event update-event-direct -i "event id" -c "contract id" -s "support contact id"
    -n "name" -l "location" -a "attendees" -no "notes" -sd "start date YYYY-MM-DD" -ed "end date YYYY-MM-DD".
    AUTH REQUIRED LOGIN FIRST
    """
    try:
        event = Event.get(id=event_id)
        if not check_user_and_permissions(
            user, "update-event"
        ) and not user.has_permission_own(event.support_contact):
            return

        if contract_id is not None:
            try:
                contract = Contract.get(id=contract_id)
                if contract.status is False:
                    typer.echo("Contract must be sign to create an event")
                    return
                existing_event = (
                    Event.select().where(Event.contract == contract).first()
                )
                if existing_event:
                    typer.echo("An event already exist for this contract.")
                    return
                event.contract = contract
            except Contract.DoesNotExist:
                typer.echo("Contract not found")
                return

        if support_contact_id is not None:
            try:
                support_contact = User.get(id=support_contact_id)
                event.support_contact = support_contact
            except User.DoesNotExist:
                typer.echo("User support not found")

        if name is not None:
            event.name = name

        if location is not None:
            event.location = location

        if attendees is not None:
            event.attendees = attendees

        if notes is not None:
            event.notes = notes

        if start_date is not None:
            new_start_date = check_date(start_date)
            event.start_date = new_start_date

        if end_date is not None:
            new_end_date = check_date(end_date)
            event.end_date = new_end_date

        event.save()
        typer.echo("Event updated succesfully")

        if event.support_contact is not None:
            support_contact_name = event.support_contact.name
        else:
            support_contact_name = ""

        typer.echo(
            f"Details of the updated event n°{event.id}: "
            f"Events n°{event.id}: Name: {event.name}, Contract n°: {event.contract.id}, "
            f"Location: {event.location}, Attendees: {event.attendees}, "
            f"Notes: {event.notes}, Start date: {event.start_date}, End date: {event.end_date}, Support contact: {support_contact_name}"
        )

    except Event.DoesNotExist:
        typer.echo("Event not found")
        return

    except Exception as e:
        typer.echo(f"Error: {e}")


if __name__ == "__main__":
    app()
