import pytest
import bcrypt
from typer.testing import CliRunner
from crm.models.user import User
from crm.models.role import Role
from crm.__main__ import app

runner = CliRunner()


def test_create_user_succes(setup_db, auth_admin_user):
    with setup_db.atomic():
        user, token = auth_admin_user
        result = runner.invoke(
            app,
            [
                "user",
                "create-user",
                "-n",
                "Alain",
                "-e",
                "alain@gmail.com",
                "-p",
                "alaindu95",
            ],
            input="Commercial",
            headers={"Authorization": f"Bearer {token}"},
        )

        print(result.output)
        assert "User created successfully" in result.output

        user = User.get(email="alain@gmail.com")
        assert user.name == "Alain"
        assert bcrypt.checkpw("alaindu95".encode(), user.password.encode())
        assert user.role.name == "Commercial"


def test_create_with_wrong_role(setup_db, auth_admin_user):
    with setup_db.atomic():
        user, token = auth_admin_user
        result = runner.invoke(
            app,
            [
                "user",
                "create-user",
                "-n",
                "Alain",
                "-e",
                "alain@gmail.com",
                "-p",
                "alaindu95",
            ],
            input="Wrong role",
            headers={"Authorization": f"Bearer {token}"},
        )

        print(result.output)
        assert "Error: This role does not exist" in result.output


def test_login(setup_db, user2, auth_admin_user):
    user2
    with setup_db.atomic():
        user, token = auth_admin_user
        result = runner.invoke(
            app,
            ["user", "login", "--name", "Jean", "--password", "jean"],
            headers={"Authorization": f"Bearer {token}"},
        )

        assert result.exit_code == 0
        assert "Welcome Jean" in result.output


def test_login_wrong_password(setup_db, user2, auth_admin_user):
    user2
    with setup_db.atomic():
        user, token = auth_admin_user
        result = runner.invoke(
            app,
            ["user", "login", "--name", "Jean", "--password", "lolipop"],
            headers={"Authorization": f"Bearer {token}"},
        )

        assert "Wrong email or password" in result.output


def test_wrong_login(setup_db, auth_admin_user):
    with setup_db.atomic():
        user, token = auth_admin_user
        result = runner.invoke(
            app,
            ["user", "login", "--name", "JUAN", "--password", "JUANITO"],
            headers={"Authorization": f"Bearer {token}"},
        )

    assert "Wrong email or password" in result.output


def test_list_users(user2, user3, auth_admin_user):
    user, token = auth_admin_user
    user2
    user3
    result = runner.invoke(
        app, ["user", "list-users"], headers={"Authorization": f"Bearer {token}"}
    )

    print(result.output)

    assert "Name: Jean" in result.output
    assert "Email: carlos@gmail.com" in result.output


def test_no_user(setup_db, auth_admin_user):
    with setup_db:
        user, token = auth_admin_user
        result = runner.invoke(
            app, ["user", "list-users"], headers={"Authorization": f"Bearer {token}"}
        )

        assert "No users found" in result.output


def test_get_user(setup_db, user2, auth_admin_user):
    user2
    with setup_db.atomic():
        user, token = auth_admin_user
        result = runner.invoke(
            app,
            ["user", "get-user", "--user-id", "1"],
            headers={"Authorization": f"Bearer {token}"},
        )

        print(result.output)
        assert (
            "User n°1: Name: Jean, Email: jean@gmail.com, Role: commercial"
            in result.output
        )


def test_get_user_no_exist(setup_db, auth_admin_user):
    with setup_db:
        user, token = auth_admin_user
        result = runner.invoke(
            app,
            ["user", "get-user", "--user-id", "1"],
            headers={"Authorization": f"Bearer {token}"},
        )

        assert "User not found" in result.output
