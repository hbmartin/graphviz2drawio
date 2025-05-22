from xml.etree.ElementTree import Element

from pygraphviz import AGraph


class GdValueError(ValueError):
    """Base class for exceptions raised during conversion."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class CouldNotParsePathError(GdValueError):
    """Could not parse path from SVG element."""

    def __init__(self, g: Element) -> None:
        super().__init__(
            f"Could not parse path from SVG element: {g.tag} ({g.attrib})",
        )


class MissingTitleError(GdValueError):
    """Title missing from SVG element."""

    def __init__(self, g: Element) -> None:
        super().__init__(
            f"Title missing from SVG element: {g.tag} with attributes {g.attrib}.",
        )


class MissingTextError(GdValueError):
    """Title missing from SVG element."""

    def __init__(self, g: Element) -> None:
        super().__init__(
            f"Text missing from SVG element: {g.tag} with attributes {g.attrib}.",
        )


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


class UnableToParseGraphError(GdValueError):
    """Graph was unexpectedly None."""

    def __init__(self, graph: AGraph) -> None:
        super().__init__(
            f"Graph.draw() returned by pygraphviz was unexpectedly None: {graph}",
        )
