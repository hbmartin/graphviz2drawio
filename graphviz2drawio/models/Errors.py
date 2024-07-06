class GdValueError(ValueError):
    """Base class for exceptions raised during conversion."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidCbError(GdValueError):
    """Invalid cubic Bézier value."""

    def __init__(self) -> None:
        super().__init__("Invalid cubic Bézier value.")
