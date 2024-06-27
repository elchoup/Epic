import pytest
import bcrypt
from typer.testing import CliRunner
from test_config import setup_db, user2, user3
from crm.models.user import User
from crm.models.role import Role
from crm.__main__ import app

runner = CliRunner()


def test_create_user_succes(setup_db):
    with setup_db.atomic():
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
                "--role-name",
                "commercial",
            ],
        )

        print(result.output)

        assert result.exit_code == 0
        assert "User created successfully" in result.output

        user = User.get(email="alain@gmail.com")
        assert user.name == "Alain"
        assert bcrypt.checkpw("alaindu95".encode(), user.password.encode())
        assert user.role.name == "commercial"


def test_create_with_wrong_role(setup_db):
    with setup_db.atomic():
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
            input="g,ergoerjgeo",
        )

        print(result.output)
        assert "Error role choosen is invalid" in result.output


def test_login(setup_db, user2):
    user2
    with setup_db.atomic():
        result = runner.invoke(
            app, ["user", "login", "--name", "Jean", "--password", "jean"]
        )

        assert result.exit_code == 0
        assert "Welcome Jean" in result.output


def test_login_wrong_password(setup_db, user2):
    user2
    with setup_db.atomic():
        result = runner.invoke(
            app, ["user", "login", "--name", "Jean", "--password", "lolipop"]
        )

        assert "Wrong password" in result.output


def test_wrong_login(setup_db):
    with setup_db.atomic():
        result = runner.invoke(
            app, ["user", "login", "--name", "JUAN", "--password", "JUANITO"]
        )

    assert "User not found" in result.output


def test_list_users(user2, user3):
    user2
    user3
    result = runner.invoke(app, ["user", "list-users"])

    print(result.output)

    assert "Name: Jean" in result.output
    assert "Email: carlos@gmail.com" in result.output


def test_no_user(setup_db):
    with setup_db:
        result = runner.invoke(app, ["user", "list-users"])

        assert "No users found" in result.output


def test_get_user(setup_db, user2):
    user2
    with setup_db.atomic():
        result = runner.invoke(app, ["user", "get-user", "--user-id", "1"])

        print(result.output)
        assert (
            "User n°1: Name: Jean, Email: jean@gmail.com, Role: commercial"
            in result.output
        )


def test_get_user_no_exist(setup_db):
    with setup_db:
        result = runner.invoke(app, ["user", "get-user", "--user-id", "1"])

        assert "User not found" in result.output
