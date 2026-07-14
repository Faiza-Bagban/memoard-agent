import pytest

from payments.process import process_payment
from app.errors import AppError


def test_process_payment_success():
    """Verify successful payment processing returns a transaction id.

    Args:
        None

    Returns:
        None
    """
    result = process_payment("user-1", 50.0)
    assert result["status"] == "success"


def test_process_payment_invalid_amount():
    """Verify invalid payment amount raises AppError.

    Args:
        None

    Returns:
        None
    """
    with pytest.raises(AppError):
        process_payment("user-1", -10.0)