import math
from collections.abc import Callable

from svg.path import CubicBezier

LINE_TOLERANCE = 0.01


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
        """Complex numbers for start, end, and list of 4 Bezier control points."""
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

        y = _line(cb.start, cb.end)

        if y is None:
            return Curve.is_linear(_rotate_bezier(cb))

        return math.isclose(
            y(cb.control1.real),
            cb.control1.imag,
            rel_tol=LINE_TOLERANCE,
        ) and math.isclose(
            y(cb.control2.real),
            cb.control2.imag,
            rel_tol=LINE_TOLERANCE,
        )


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


def _rotate_bezier(cb):
    """Reverse imaginary and real parts for all components."""
    return CubicBezier(
        complex(cb.start.imag, cb.start.real),
        complex(cb.control1.imag, cb.control1.real),
        complex(cb.control2.imag, cb.control2.real),
        complex(cb.end.imag, cb.end.real),
    )
