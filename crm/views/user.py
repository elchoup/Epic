import typer
import bcrypt
from typing_extensions import Annotated
from crm.models.user import User
from crm.models.role import Role
from crm.auth import auth_required, check_user_and_permissions


app = typer.Typer()
ROLES = ["commercial", "support", "gestion"]


def prompt_for_role():
    role_name = typer.prompt("Choisissez un rôle parmi Commercial, Support ou Gestion")
    try:
        role = Role.get(name=role_name)
        return role
    except Role.DoesNotExist:
        typer.echo("This role does not exist")


@app.command()
@auth_required
def create_user(
    name: Annotated[str, typer.Option("-n", prompt=True, help="Name of the user")],
    email: Annotated[str, typer.Option("-e", prompt=True, help="Email of the user")],
    password: Annotated[
        str, typer.Option("-p", prompt=True, help="Password of the user")
    ],
    role: str = typer.Option(prompt_for_role),
    user=None,
):
    if not role:
        typer.echo("You need to choose a role")
        raise typer.Exit(code=1)
    try:
        if not check_user_and_permissions(user, "create-user"):
            return
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        User.create(name=name, email=email, password=hashed_password, role=role)
        typer.echo("User created successfully")
    except Exception as e:
        return typer.echo(f"Error : {e}")


@app.command()
def login(
    email: str = typer.Option(..., prompt=True),
    password: str = typer.Option(..., prompt=True),
):
    try:
        user = User.get(email=email)
        if user and bcrypt.checkpw(password.encode(), user.password.encode()):
            token = user.generate_token()
            print(f"salut {token}")
            with open("token.txt", "w") as token_file:
                token_file.write(token)
            typer.echo(f"Welcome {user.name}")
        else:
            typer.echo("Wrong email or password")
    except Exception as e:
        typer.echo(f"Error {e}")


@app.command(name="list-users")
@auth_required
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
@auth_required
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


@app.command()
@auth_required
def delete_user(
    user_id: int = typer.Option(..., "-i", prompt="Enter user ID you want to delete"),
    user=None,
):
    try:
        if not check_user_and_permissions(user, "delete-user"):
            return
        user = User.get(id=user_id)
        user.delete_instance()
        typer.echo("User deleted succesfully")
    except User.DoesNotExist:
        typer.echo("User not found")
        return
    except Exception as e:
        typer.echo(f"Error: {e}")
        return


@app.command()
@auth_required
def update_user(
    user_id: int = typer.Option(..., "-i", prompt="Enter user id"), user=None
):
    try:
        if not user.id == user_id and not check_user_and_permissions(
            user, "update-user"
        ):
            typer.echo(
                "Unauthorized: You can only update your profile or be a gestion member"
            )
            return
        user_to_up = User.get(id=user_id)
        name = typer.prompt(
            "Enter a new name or pass with enter", default=user_to_up.name
        )
        email = typer.prompt(
            "Enter a new mail or pass with enter", default=user_to_up.email
        )
        change_password = typer.confirm(
            "do you want to change password ?", default=False
        )
        if change_password:
            new_password = typer.prompt(
                "Enter new password", hide_input=True, confirmation_prompt=True
            )
            password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        else:
            password = user_to_up.password

        user_to_up.name = name
        user_to_up.email = email
        user_to_up.password = password

        user_to_up.save()

    except User.DoesNotExist:
        typer.echo("Not found")

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
