import typer
import bcrypt
from typing_extensions import Annotated
from crm.models.user import User
from crm.models.role import Role
from crm.models.client import Client
from crm.models.contract import Contract
from crm.models.event import Event


app = typer.Typer()
ROLES = ["commercial", "support", "gestion"]


def prompt_for_role():
    role_name = typer.prompt("Choisissez un rôle parmi commercial, support ou gestion")
    while role_name not in ROLES:
        typer.echo("Le role choisi n'est pas dans les roles disponibles")
        role_name = typer.prompt(
            "Choisissez un rôle parmi commercial, support ou gestion"
        )
    return role_name


@app.command()
def create_user(
    name: Annotated[str, typer.Option("-n", prompt=True, help="Name of the user")],
    email: Annotated[str, typer.Option("-e", prompt=True, help="Email of the user")],
    password: Annotated[
        str, typer.Option("-p", prompt=True, help="Password of the user")
    ],
    role_name: str = typer.Option(prompt_for_role),
):

    try:
        role, created = Role.get_or_create(name=role_name)
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        User.create(name=name, email=email, password=hashed_password, role=role)
        if created:
            typer.echo(f"le rôle '{role_name}' à été créé")
        typer.echo("Utilisateur crée avec succés")
    except Exception as e:
        return typer.echo(f"Erreur : {e}")


@app.command()
def login(
    name: str = typer.Option(..., prompt=True),
    password: str = typer.Option(..., prompt=True),
):
    try:
        user = User.get(name=name)
        if bcrypt.checkpw(password.encode(), user.password.encode()):
            typer.echo(f"Vous êtes connecté en tant que {name}")
        else:
            typer.echo("Mot de passe incorrect")
    except:
        typer.echo(f"Utilisateur non trouvé")


@app.command(name="list-users")
def list_users():
    try:
        users = User.select()
        if not users:
            typer.echo("No users found")
        for user in users:
            typer.echo(
                f"User n°{user.id}: Name: {user.name}, "
                f"Email: {user.email}, Role: {user.role.name}"
            )
    except Exception as e:
        typer.echo(f"Error: {e}")


@app.command()
def get_user(
    user_id: int = typer.Option(
        ..., prompt="Enter id of user you want details of", help="ID of the user"
    )
):
    try:
        user = User.get(id=user_id)
        typer.echo(
            f"User n°{user.id}: Name: {user.name}, "
            f"Email: {user.email}, Role: {user.role.name}"
        )
    except User.DoesNotExist:
        typer.echo("User not found")
    except Exception as e:
        typer.echo(f"Error: {e}")


if __name__ == "__main__":
    app()


"""def create_user(
    name: str = None, email: str = None, password: str = None, role: str = None
):
    if name is None:
        name = typer.prompt("Nom")
    if email is None:
        email = typer.prompt("Email")
    if password is None:
        password = typer.prompt("Password")
    if role is None:
        role = typer.prompt("role (Commercial, Support ou Gestion)")
"""
