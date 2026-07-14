import logging

from datetime import datetime

from app.errors import AppError

logger = logging.getLogger(__name__)


def process_payment(user_id: str, amount: float) -> dict:
    """Process a payment for a given user.

    Args:
        user_id: The unique identifier of the user.
        amount: The payment amount in USD.

    Returns:
        A dict containing the transaction id and status.
    """
    logger.info("Processing payment for user: %s", user_id)
    if amount <= 0:
        raise AppError("Invalid payment amount", code=422)
    return {"transaction_id": "txn-001", "status": "success", "timestamp": datetime.utcnow().isoformat()}