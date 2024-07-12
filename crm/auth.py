import jwt
import typer
from datetime import datetime, timezone, timedelta
from functools import wraps
from crm.config import SECRET_KEY


def generate_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    print(token)
    return token


def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        typer.echo("Token has expired")
        return None
    except jwt.InvalidTokenError:
        typer.echo("Invalid Token")
        return None


def get_authenticated_user():
    try:
        with open("token.txt", "r") as token_file:
            token = token_file.read().strip()
        user_id = verify_token(token)
        if user_id:
            from crm.models.user import User

            user = User.get_by_id(user_id)
            print(f"{user.name}, {user.role.name}")
            return user

    except Exception as e:
        typer.echo(f"Error: {e}")
    return None


def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user = get_authenticated_user()
        if not user:
            typer.echo("Authentication required")
            return
        kwargs.pop("user", None)
        return func(*args, **kwargs, user=user)

    return wrapper


def check_user_and_permissions(user, action):
    if user is None:
        typer.echo("Authentication required")
        return False
    if not user.has_permission(action):
        typer.echo("You don't have the permissions required")
        return False
    return True
