from xml.etree.ElementTree import Element


class GdValueError(ValueError):
    """Base class for exceptions raised during conversion."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class MissingTitleError(GdValueError):
    """Title missing from SVG element."""

    def __init__(self, g: Element) -> None:
        super().__init__(f"Title missing from SVG element: {g.tag}")


class InvalidBezierParameterError(GdValueError):
    """Invalid Bezier parameter, must be 0 <= t <= 1."""

    def __init__(self, t: float) -> None:
        super().__init__(f"Invalid Bezier parameter (t={t}), must be 0 <= t <= 1.")


class MissingIdentifiersError(GdValueError):
    """Missing identifiers for a geometry."""

    def __init__(self, sid: str | None, gid: str | None) -> None:
        super().__init__(
            f"Missing identifiers for a geometry: sid(id): {sid}, gid(title): {gid}.",
        )
