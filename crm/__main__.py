import typer
from .views.client import app as client_app
from .views.user import app as user_app
from .views.contract import app as contract_app
from .views.event import app as event_app

app = typer.Typer()

app.add_typer(user_app, name="user")
app.add_typer(client_app, name="client")
app.add_typer(contract_app, name="contract")
app.add_typer(event_app, name="event")


if __name__ == "__main__":
    app()


"""username: Annotated[
        str, typer.Option("-u", prompt=True, help="The name of the user.")
    ],"""
