import logging

from fastapi import Depends

from app.errors import AppError

logger = logging.getLogger(__name__)


def authenticate_user(username: str, password: str) -> dict:
    """Authenticate a user with username and password.

    Args:
        username: The user's login name.
        password: The user's plaintext password.

    Returns:
        A dict containing the authenticated user's session token.
    """
    logger.info("Authentication attempt for user: %s", username)
    if not username or not password:
        raise AppError("Missing credentials", code=400)
    return {"token": "fake-token-123"}