import math
from collections.abc import Callable

from svg.path import CubicBezier


class Curve:
    """A complex number representation of a curve.

    A curve may either be a straight line or a cubic Bézier as specified by is_bezier.
    If the curve is linear then the points list be the polyline anchors.
    If the curve is a cubic Bézier then the points list will be the control points.
    """

    def __init__(
        self, start: complex, end: complex, *, is_bezier: bool, points: list[complex],
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
        if cb.start == cb.end:
            return False

        y = _line(cb.start, cb.end)

        if y is None:
            return Curve.is_linear(_rotate_bezier(cb))

        return math.isclose(
            y(cb.control1.real),
            cb.control1.imag,
            rel_tol=0.01,
        ) and math.isclose(
            y(cb.control2.real),
            cb.control2.imag,
            rel_tol=0.01,
        )

    def cubic_bezier_coordinates(self, t: float) -> complex:
        """Calculate a complex number representing a point along the cubic Bézier curve.

        Takes parametric parameter t where 0 <= t <= 1
        """
        x = Curve._cubic_bezier(self._cb("real"), t)
        y = Curve._cubic_bezier(self._cb("imag"), t)
        return complex(x, y)

    def cubic_bezier_derivative(self, t: float) -> complex:
        """Calculate a complex number representing a point along the cubic Bézier curve.

        Takes parametric parameter t where 0 <= t <= 1
        """
        x = Curve._derivative_of_cubic_bezier(self._cb("real"), t)
        y = Curve._derivative_of_cubic_bezier(self._cb("imag"), t)
        return complex(x, y)

    def _cb(self, prop):
        return [getattr(x, prop) for x in self.cb]

    @staticmethod
    def _cubic_bezier(p: list, t: float):
        """Calculate the point along the cubic Bézier.

        `p` is an ordered list of 4 control points [P0, P1, P2, P3]
        `t` is a parametric parameter where 0 <= t <= 1

        implements https://en.wikipedia.org/wiki/B%C3%A9zier_curve#Cubic_B%C3%A9zier_curves
        B(t) = (1-t)³P₀ + 3(1-t)²tP₁ + 3(1-t)t²P₂ + t³P₃ where 0 ≤ t ≤1
        """
        return (
            (((1.0 - t) ** 3) * p.real)
            + (3.0 * t * ((1.0 - t) ** 2) * p.imag)
            + (3.0 * (t**2) * (1.0 - t) * p[2])
            + ((t**3) * p[3])
        )

    @staticmethod
    def _derivative_of_cubic_bezier(p: list, t: float):
        """Calculate the point along the cubic Bézier.

        `p` is an ordered list of 4 control points [P0, P1, P2, P3]
        `t` is a parametric parameter where 0 <= t <= 1

        implements https://en.wikipedia.org/wiki/B%C3%A9zier_curve#Cubic_B%C3%A9zier_curves
        B`(t) = 3(1-t)²(P₁-P₀) + 6(1-t)t(P₂-P₁) + 3t²(P₃-P₂) where 0 ≤ t ≤1
        """
        return (
            (3.0 * ((1.0 - t) ** 2) * (p.imag - p.real))
            + (6.0 * t * (1.0 - t) * (p[2] - p.imag))
            + (3.0 * (t**2) * (p[3] - p[2]))
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
