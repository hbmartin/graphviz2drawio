class GdValueError(ValueError):
    """Base class for exceptions raised during conversion."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class MissingTitleError(GdValueError):
    """Title missing from SVG element."""

    def __init__(self, g) -> None:
        super().__init__("Title missing from SVG element.")
        self.g = g
