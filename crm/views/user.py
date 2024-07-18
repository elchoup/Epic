import typer
import bcrypt
from typing_extensions import Annotated, Optional
from crm.models.user import User
from crm.models.role import Role
from crm.auth import auth_required, check_user_and_permissions


app = typer.Typer()
ROLES = ["commercial", "support", "gestion"]


def prompt_for_role(user):
    """Function to choose a role when you create a user.
    **Args = cureent user
    If user is Admin he can assign another admin"""

    role_name = typer.prompt("Choose a role from Commercial, Gestion or Support")
    if role_name == "Admin":
        if user.role.id == 4:
            valid = typer.confirm("Are you sure to name another admin for this app ?")
            if not valid:
                typer.echo("Operation aborted")
                return None
        else:
            typer.echo("You do not have the permissions to allow this role")
            return None
    try:
        role = Role.get(name=role_name)
        return role
    except Role.DoesNotExist:
        typer.echo("Error: This role does not exist")
        return None


@app.command()
@auth_required
def create_user(
    name: Annotated[str, typer.Option("-n", prompt=True, help="Name of the user")],
    email: Annotated[str, typer.Option("-e", prompt=True, help="Email of the user")],
    password: Annotated[
        str, typer.Option("-p", prompt=True, help="Password of the user")
    ],
    user=None,
):
    role = prompt_for_role(user)
    if role is None:
        return
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
def list_users(
    role: Annotated[Optional[str], typer.Option("-r", help="name of the role")] = None,
    user=None,
):
    try:
        valid_roles = {"Admin", "Commercial", "Gestion", "Support"}
        users = User.select()
        if role is not None:
            if role not in valid_roles:
                typer.echo("Invalid role value")
                return
            users = User.select().join(Role).where(Role.name == role)
        if users.count() == 0:
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
    ),
    user=None,
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
