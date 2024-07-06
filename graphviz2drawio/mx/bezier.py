# Based on https://github.com/utlco/utl-geom2d/blob/main/src/geom2d/bezier.py
# See also https://pomax.github.io/bezierinfo/

import math

EPSILON: float = 1e-03


def controlpoints_at(
    p1: complex,
    c1: complex,
    c2: complex,
    p2: complex,
    t: float,
) -> tuple[complex, complex, complex, complex, complex]:
    """Get the point on this curve at `t` plus control points.

    Useful for subdividing the curve at `t`.

    Returns
    -------
        A tuple of the form (C0, C1, P, C2, C3) where C1 and C2 are
        the control points tangent to P and C0 and C3 would be the
        new control points of the endpoints where this curve to be
        subdivided at P.

    """
    mt = 1 - t
    # First intermediate points
    d01 = mt * p1 + t * c1
    d12 = mt * c1 + t * c2
    d23 = mt * c2 + t * p2
    # Second intermediate points
    d012 = mt * d01 + t * d12
    d123 = mt * d12 + t * d23
    # Finally, the split point
    d0123 = mt * d012 + t * d123
    return d01, d012, d0123, d123, d23


def subdivide(
    p1: complex,
    c1: complex,
    c2: complex,
    p2: complex,
    t: float,
) -> tuple[tuple, tuple | None]:
    """Subdivide this curve at the point on the curve at `t`.

    Split curve into two cubic Bézier curves, where 0<t<1.
    Uses De Casteljaus's algorithm.

    Returns
    -------
        A tuple of one or two CubicBezier objects.

    """
    if t < 0 or t > 1:
        return (p1, c1, c2, p2), None
    cp0, cp1, p, cp2, cp3 = controlpoints_at(p1, c1, c2, p2, t)
    curve1 = (p1, cp0, cp1, p)
    curve2 = (p, cp2, cp3, p2)
    return curve1, curve2


def subdivide_inflections(p1: complex, c1: complex, c2: complex, p2: complex) -> tuple:
    """Subdivide this curve at the inflection points, if any.

    Returns
    -------
        A list containing one to three curves depending on whether
        there are no inflections, one inflection, or two inflections.

    """
    t1, t2 = roots(p1, c1, c2, p2)
    if t2 < 0:
        if t1 > 0:
            return subdivide(p1, c1, c2, p2, t1)  # one inflection at t1
        return ((p1, c1, c2, p2),)  # no inflections
    if t1 < 0:
        if t2 > 0:
            return subdivide(p1, c1, c2, p2, t2)  # one inflection at t2
        return ((p1, c1, c2, p2),)  # no inflections

    # Two roots/inflection points

    # Subdivide at first inflection
    curve1, curve2x = subdivide(p1, c1, c2, p2, t1)

    # Subdivide at second inflection.
    # Need to recalculate roots for subcurve.
    t1, t2 = roots(*curve2x)
    t = max(t1, t2)
    if t > 0:
        curve2, curve3 = subdivide(*curve2x, t)
    else:
        curve2 = curve2x
        curve3 = None
    return curve1, curve2, curve3


def roots(p1: complex, c1: complex, c2: complex, p2: complex) -> tuple[float, float]:
    """Find roots of this curve.

    The roots are inflection points are where the curve changes direction,
    has a cusp, or a loop.
    There may be none, one, or two inflections on the curve.
    A loop will have two inflections.

    These inflection points can be used to subdivide the curve.

    See:
        http://web.archive.org/web/20220129063812/https://www.caffeineowl.com/graphics/2d/vectorial/cubic-inflexion.html

    Returns
    -------
        A tuple containing the roots (t1, t2).
        The root values will be 0 < t < 1 or -1 if no root.
        If there is only one root it will always be the
        first value of the tuple.
        The roots will be ordered by ascending value if
        there is more than one.

    """
    # Basically the equation to be solved is where the cross product of
    # the first and second derivatives is zero:
    # P' X P'' = 0
    # Where P' and P'' are the first and second derivatives respectively

    # Temporary vectors to simplify the math
    v1 = c1 - p1
    v2 = c2 - c1 - v1
    v3 = p2 - c2 - v1 - 2 * v2

    # Calculate quadratic coefficients
    # of the form a*t**2 + b*t + c = 0
    a = v2.real * v3.imag - v2.imag * v3.real
    b = v1.real * v3.imag - v1.imag * v3.real
    c = v1.real * v2.imag - v1.imag * v2.real

    def _valid_t(t: float) -> float:
        """Check range of t, returns -1 if t is out of range."""
        return t if EPSILON < t < 1 - EPSILON else -1

    if is_zero(a):
        if not is_zero(b):
            # This would be a straight line so there shouldn't really
            # be an inflection point.
            return _valid_t(-c / b), -1
        return -1, -1

    # the discriminant of the quadratic eq.
    dis = b * b - 4 * a * c
    if is_zero(dis):
        if a != 0:
            return _valid_t(-b / (2 * a)), -1
        return -1, -1

    # When a curve has a loop the discriminant will be negative
    # so use the absolute value to use the real part of a
    # normally complex number...
    disroot = math.sqrt(abs(dis))
    t1 = _valid_t((-b - disroot) / (2 * a))
    t2 = _valid_t((-b + disroot) / (2 * a))

    # Return in ascending order
    if t1 > 0:
        return (t1, t2) if t1 <= t2 or t2 < 0 else (t2, t1)
    return t2, t1


def is_zero(value: float) -> bool:
    """Determine if the float value is essentially zero."""
    return -EPSILON < value < EPSILON


def approximate_cubic_bezier_as_quadratic(
    p0: complex,
    c1: complex,
    c2: complex,
    p2: complex,
) -> tuple[complex, complex, complex]:
    """Approximates a cubic Bézier as a quadratic using tangent intersection."""
    # Calculate tangent vectors at start and end points
    tan_start = 3.0 * (c1 - p0)
    tan_end = 3.0 * (p2 - c2)

    # Find the intersection point of the tangent lines (if they're not parallel)
    denom = tan_start.imag * tan_end.real - tan_start.real * tan_end.imag
    if denom != 0:
        t = (
            (p2.imag - p0.imag) * tan_end.real - (p2.real - p0.real) * tan_end.imag
        ) / denom
        quadratic_control = p0 + t * tan_start
    else:
        # Tangent lines are parallel, fallback to averaging
        quadratic_control = (c1 + c2) / 2

    return p0, quadratic_control, p2
