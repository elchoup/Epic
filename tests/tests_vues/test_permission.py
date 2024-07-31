from crm.auth import check_user_and_permissions
from unittest.mock import patch


def test_permission_valid(setup_db, com_logged):
    with setup_db.atomic():
        result = check_user_and_permissions(com_logged, "create-client")
        assert result == True


def test_not_permission_valid(setup_db, com_logged):
    with setup_db.atomic():
        with patch("typer.echo") as mock_echo:
            result = check_user_and_permissions(com_logged, "create-contract")
            assert result == False
            mock_echo.assert_called_once_with("You don't have the permissions required")


def test_not_permission_no_user(setup_db):
    with setup_db.atomic():
        with patch("typer.echo") as mock_echo:
            user = None
            result = check_user_and_permissions(user, "create-contract")
            assert result == False
            mock_echo.assert_called_once_with("Authentication required")
