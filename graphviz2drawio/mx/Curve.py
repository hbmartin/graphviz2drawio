from collections.abc import Callable

from svg.path import CubicBezier

LINE_ABS_TOLERANCE = 0.01
_SVG_ROUNDING_TOLERANCE = 0.001
# Two points closer than this (in graphviz points) are treated as coincident
# when locating a waypoint distinct from a terminal for tangent computation.
_COINCIDENT_POINT_TOLERANCE = 0.01


class Curve:
    """A complex number representation of a curve.

    A curve may either be a straight line or a cubic Bézier as specified by is_bezier.
    If the curve is linear then the points list be the polyline anchors.
    If the curve is a cubic Bézier then the points list will be the control points.
    """

    def __init__(
        self,
        start: complex,
        end: complex,
        *,
        is_bezier: bool,
        points: list[complex],
    ) -> None:
        """Build a curve from terminal points and a variable-length point list.

        `points` holds the polyline anchors when the curve is linear, or the
        quadratic control points (one or more, terminals excluded) consumed by
        draw.io's implied-midpoint renderer when the curve is a Bézier.
        """
        self.start: complex = start
        self.end: complex = end
        self.is_bezier: bool = is_bezier
        self.points: list[complex] = points

    def __str__(self) -> str:
        return f"{self.start} -> {self.end} {self.is_bezier} ({self.points})"

    @staticmethod
    def is_linear(cb: CubicBezier) -> bool:
        """Determine if the cubic Bézier is a straight line."""
        if cb.start == cb.end:
            return False

        chord = cb.end - cb.start
        return (
            _distance_from_line(cb.start, chord, cb.control1)
            <= LINE_ABS_TOLERANCE + _SVG_ROUNDING_TOLERANCE
            and _distance_from_line(cb.start, chord, cb.control2)
            <= LINE_ABS_TOLERANCE + _SVG_ROUNDING_TOLERANCE
        )

    def first_interior_point(self) -> complex:
        """Return the first waypoint that is distinct from the source terminal."""
        for point in self.points:
            if abs(point - self.start) > _COINCIDENT_POINT_TOLERANCE:
                return point
        return self.end

    def last_interior_point(self) -> complex:
        """Return the last waypoint that is distinct from the target terminal."""
        for point in reversed(self.points):
            if abs(point - self.end) > _COINCIDENT_POINT_TOLERANCE:
                return point
        return self.start


def _distance_from_line(start: complex, direction: complex, point: complex) -> float:
    return abs(_cross(direction, point - start)) / abs(direction)


def _cross(v1: complex, v2: complex) -> float:
    return (v1.real * v2.imag) - (v1.imag * v2.real)


def _line(start: complex, end: complex) -> Callable[[float], float] | None:
    """Calculate the slope and y-intercept of a line."""
    denom = end.real - start.real
    if denom == 0:
        return None
    m = (end.imag - start.imag) / denom
    b = start.imag - (m * start.real)

    def y(x: float) -> float:
        return (m * x) + b

    return y
