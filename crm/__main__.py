import typer
from crm.views.client import app as client_app
from crm.views.user import app as user_app
from crm.views.contract import app as contract_app
from crm.views.event import app as event_app


app = typer.Typer()

app.add_typer(
    user_app, name="user", help="To access user functions: python -m crm user --help"
)
app.add_typer(
    client_app,
    name="client",
    help="To access client functions: python -m crm client --help",
)
app.add_typer(
    contract_app,
    name="contract",
    help="To access contract functions: python -m crm contract --help",
)
app.add_typer(
    event_app,
    name="event",
    help="To access event functions: python -m crm event --help",
)


if __name__ == "__main__":
    app()
