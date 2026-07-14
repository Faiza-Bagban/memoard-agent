import logging

from app.errors import AppError

logger = logging.getLogger(__name__)


def get_user_profile(user_id: str) -> dict:
    """Retrieve a user's profile information.

    Args:
        user_id: The unique identifier of the user.

    Returns:
        A dict containing the user's profile data.
    """
    logger.info("Fetching profile for user: %s", user_id)
    if not user_id:
        raise AppError("User id is required", code=400)
    return {"user_id": user_id, "name": "Jane Doe", "email": "jane@example.com"}