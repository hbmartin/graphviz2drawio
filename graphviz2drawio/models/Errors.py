class GdValueError(ValueError):
    """Base class for exceptions raised during conversion."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class MissingTitleError(GdValueError):
    """Title missing from SVG element."""

    def __init__(self, g) -> None:
        super().__init__("Title missing from SVG element.")
        self.g = g


class InvalidBezierParameterError(GdValueError):
    """Invalid Bezier parameter, must be 0 <= t <= 1."""

    def __init__(self, t) -> None:
        super().__init__(f"Invalid Bezier parameter (t={t}), must be 0 <= t <= 1.")
