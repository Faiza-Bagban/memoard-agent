class AppError(Exception):
    """Custom application error used across the codebase.

    Args:
        message: Human-readable error description.
        code: Numeric error code for the client.

    Returns:
        None
    """

    def __init__(self, message: str, code: int):
        super().__init__(message)
        self.message = message
        self.code = code