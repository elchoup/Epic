import typer
import sentry_sdk
import sys
from sentry_sdk.integrations.logging import LoggingIntegration
from crm.views.client import app as client_app
from crm.views.user import app as user_app
from crm.views.contract import app as contract_app
from crm.views.event import app as event_app

sentry_sdk.init(
    dsn="https://7f3e3fa8e1da07fa34416675437df761@o4507657772269568.ingest.de.sentry.io/4507689957589072",
    integrations=[LoggingIntegration()],
    traces_sample_rate=1.0,
)

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


def handle_exception(exc_type, exc_value, exc_traceback):
    # Ignore KeyboardInterrupt to allow normal termination of the program
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # Log the exception with Sentry
    sentry_sdk.capture_exception(exc_value)
    print(f"Exception captured: {exc_value}")


# Override the default sys.excepthook
sys.excepthook = handle_exception

"""
try:
    raise ValueError("This is a test exception for Sentry")
except Exception as e:
    sentry_sdk.capture_exception(e)
    print(f"Exception captured and sent to Sentry: {e}")"""


if __name__ == "__main__":
    app()
