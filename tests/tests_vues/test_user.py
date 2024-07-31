import pytest
import bcrypt
import sys
from io import StringIO
from typer.testing import CliRunner
from crm.models.user import User
from crm.models.role import Role
from crm.views.user import prompt_for_role
from crm.__main__ import app

runner = CliRunner()


def test_login(setup_db):
    with setup_db.atomic():
        result = runner.invoke(
            app,
            ["user", "login", "-e", "admin@gmail.com", "-p", "admin"],
        )

        assert "Welcome Admin" in result.output


def test_wrong_login(setup_db):
    with setup_db.atomic():
        result = runner.invoke(
            app,
            ["user", "login", "-e", "wrong email", "-p", "wrong password"],
        )
    print("yo", result.output)
    assert "Wrong email or password" in result.output


def test_prompt_for_role(setup_db, user1):
    with setup_db.atomic():
        # Rediriger stdout vers un StringIO temporaire
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        try:
            role = prompt_for_role(user1, role_name="Commercial")
            output = mystdout.getvalue()
        finally:
            # Restaurer stdout
            sys.stdout = old_stdout

        assert "Commercial assigned succesfully" in output
        assert role.name == "Commercial"


def test_prompt_for_role_no_perm(setup_db, user1):
    with setup_db.atomic():
        # Rediriger stdout vers un StringIO temporaire
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        try:
            role = prompt_for_role(user1, role_name="Admin")
            output = mystdout.getvalue()
        finally:
            # Restaurer stdout
            sys.stdout = old_stdout

        assert "You do not have the permissions to allow this role" in output


def test_prompt_for_role_no_exist(setup_db, user1):
    with setup_db.atomic():
        # Rediriger stdout vers un StringIO temporaire
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        try:
            role = prompt_for_role(user1, role_name="No exist")
            output = mystdout.getvalue()
        finally:
            # Restaurer stdout
            sys.stdout = old_stdout
        assert "Error: This role does not exist" in output


def test_create_user_success(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
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
            input="Commercial\n",
        )

        print(f"salut{result.output}")
        assert "User created successfully" in result.output

        user = User.get(email="alain@gmail.com")
        assert user.name == "Alain"
        assert bcrypt.checkpw("alaindu95".encode(), user.password.encode())
        assert user.role.name == "Commercial"


def test_create_with_wrong_role(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
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
            input="Wrong role\n",
        )

        print(result.output)
        assert "Error: This role does not exist" in result.output


def test_list_users(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(
            app,
            ["user", "list-users"],
        )

        print(result.output)

        assert "Name: Admin" in result.output
        assert "Email: com@gmail.com" in result.output
        assert "Email: sup@gmail.com" in result.output


def test_get_user(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(
            app,
            ["user", "get-user", "-i", "1"],
        )

        print(result.output)
        assert (
            "User n°1: Name: Com, Email: com@gmail.com, Role: Commercial"
            in result.output
        )


def test_get_user_no_exist(setup_db, admin_logged):
    with setup_db:
        admin_logged
        result = runner.invoke(
            app,
            ["user", "get-user", "-i", "8"],
        )

        assert "User not found" in result.output


def test_update_user_direct_success(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(
            app,
            [
                "user",
                "update-user-direct",
                "-i",
                5,
                "-n",
                "COM1",
                "-e",
                "COM1@gmail.com",
            ],
        )

        print(result.output)

        assert "User updated succesfully" in result.output


def test_update_user_direct_no_user(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(
            app,
            [
                "user",
                "update-user-direct",
                "-i",
                89,
                "-n",
                "COM1",
                "-e",
                "COM1@gmail.com",
            ],
        )

        assert "User not found" in result.output


def test_update_user_valid(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        runner.invoke(
            app,
            [
                "user",
                "update-user",
                "-i",
                1,
            ],
            input="COM1\nCOM1@GMAIL.COM\nn\n",
        )

    user = User.get(id=1)
    assert user.name == "COM1"
    assert user.email == "COM1@GMAIL.COM"


def test_update_user_invalid(setup_db, admin_logged):
    with setup_db.atomic():
        admin_logged
        result = runner.invoke(
            app,
            [
                "user",
                "update-user",
                "-i",
                445465465,
            ],
            input="COM1\nCOM1@GMAIL.COM\nn\n",
        )
        assert "Not found" in result.output
