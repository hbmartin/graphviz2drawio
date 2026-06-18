# Cubic-to-quadratic spline conversion adapted from fontTools cu2qu.
# fontTools is MIT licensed; the original cu2qu algorithm is copyright
# 2015 Google Inc. and distributed under the Apache License, Version 2.0.
# See: https://github.com/fonttools/fonttools/tree/main/Lib/fontTools/cu2qu

import math
from typing import TypeAlias

from svg.path import Arc

from ..models.Errors import InvalidBezierParameterError

MAX_QUAD_ERROR: float = 0.5
MAX_SEGMENTS_PER_CUBIC: int = 16

_FIT_RECURSION_LIMIT = 30
_JUNCTION_REFINEMENT_PASSES = 4
_PARALLEL_TOLERANCE = 1e-12
_ZERO_LENGTH_TOLERANCE = 1e-12

Cubic: TypeAlias = tuple[complex, complex, complex, complex]


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
    d01 = mt * p1 + t * c1
    d12 = mt * c1 + t * c2
    d23 = mt * c2 + t * p2
    d012 = mt * d01 + t * d12
    d123 = mt * d12 + t * d23
    d0123 = mt * d012 + t * d123
    return d01, d012, d0123, d123, d23


def subdivide(
    p1: complex,
    c1: complex,
    c2: complex,
    p2: complex,
    t: float,
) -> tuple[Cubic, Cubic]:
    """Subdivide this curve at the point on the curve at `t`."""
    if t < 0 or t > 1:
        raise InvalidBezierParameterError(t)
    cp0, cp1, p, cp2, cp3 = controlpoints_at(p1, c1, c2, p2, t)
    return (p1, cp0, cp1, p), (p, cp2, cp3, p2)


def cubic_to_quadratic_controls(
    p0: complex,
    c1: complex,
    c2: complex,
    p3: complex,
    max_err: float = MAX_QUAD_ERROR,
    max_n: int = MAX_SEGMENTS_PER_CUBIC,
    min_n: int = 1,
) -> list[complex]:
    """Approximate one cubic as draw.io/TrueType-style quadratic controls."""
    curve = (p0, c1, c2, p3)
    min_n = max(1, min_n)
    max_n = max(min_n, max_n)

    for n in range(min_n, max_n + 1):
        if spline := _cubic_approx_spline(curve, n, max_err):
            return spline[1:-1]

    return _cubic_approx_spline(curve, max_n, max_err, check=False)[1:-1]


def cubic_chain_to_quadratic_controls(
    cubics: list[Cubic],
    max_err: float = MAX_QUAD_ERROR,
) -> list[complex]:
    """Approximate a cubic chain as controls for draw.io's curved edge renderer."""
    if not cubics:
        return []
    if len(cubics) == 1:
        return cubic_to_quadratic_controls(*cubics[0], max_err=max_err)

    tol = max_err / 2
    adjustment_budget = 0.75 * tol
    min_segments = [
        2 if 0 < index < len(cubics) - 1 else 1
        for index, _cubic in enumerate(cubics)
    ]

    controls_by_cubic: list[list[complex]] = []
    for pass_index in range(_JUNCTION_REFINEMENT_PASSES):
        controls_by_cubic = [
            cubic_to_quadratic_controls(*cubic, max_err=tol, min_n=min_n)
            for cubic, min_n in zip(cubics, min_segments, strict=True)
        ]
        deltas = _junction_adjustment_deltas(cubics, controls_by_cubic)
        if (
            all(delta <= adjustment_budget for delta in deltas)
            or pass_index == _JUNCTION_REFINEMENT_PASSES - 1
        ):
            break
        for junction_index, delta in enumerate(deltas):
            if delta > adjustment_budget:
                min_segments[junction_index] = min(
                    MAX_SEGMENTS_PER_CUBIC,
                    min_segments[junction_index] + 1,
                )
                min_segments[junction_index + 1] = min(
                    MAX_SEGMENTS_PER_CUBIC,
                    min_segments[junction_index + 1] + 1,
                )

    _enforce_junction_symmetry(cubics, controls_by_cubic)
    return [control for controls in controls_by_cubic for control in controls]


def line_to_cubic(p0: complex, p1: complex) -> Cubic:
    """Represent a line segment as a cubic using third-points."""
    delta = p1 - p0
    return p0, p0 + delta / 3, p0 + (2 * delta) / 3, p1


def quadratic_to_cubic(p0: complex, c: complex, p1: complex) -> Cubic:
    """Represent a quadratic exactly as a cubic."""
    return p0, p0 + (2 / 3) * (c - p0), p1 + (2 / 3) * (c - p1), p1


def arc_to_cubics(arc: Arc) -> list[Cubic]:
    """Approximate an SVG elliptical arc with cubic segments of <= 90 degrees."""
    delta_degrees = float(arc.delta)
    if math.isclose(delta_degrees, 0, abs_tol=_ZERO_LENGTH_TOLERANCE):
        return []

    segment_count = max(1, math.ceil(abs(delta_degrees) / 90))
    theta = math.radians(float(arc.theta))
    delta = math.radians(delta_degrees) / segment_count
    rotation = math.radians(float(arc.rotation))
    scale = float(getattr(arc, "radius_scale", 1) or 1)
    radius = arc.radius
    rx = abs(radius.real) * scale
    ry = abs(radius.imag) * scale

    cubics: list[Cubic] = []
    for index in range(segment_count):
        start_angle = theta + index * delta
        end_angle = start_angle + delta
        cubics.append(
            _arc_segment_to_cubic(
                arc.center,
                rx,
                ry,
                rotation,
                start_angle,
                end_angle,
            ),
        )

    if cubics:
        first = cubics[0]
        cubics[0] = (arc.start, first[1], first[2], first[3])
        last = cubics[-1]
        cubics[-1] = (last[0], last[1], last[2], arc.end)
    return cubics


def _junction_adjustment_deltas(
    cubics: list[Cubic],
    controls_by_cubic: list[list[complex]],
) -> list[float]:
    deltas: list[float] = []
    for index in range(len(cubics) - 1):
        left = controls_by_cubic[index][-1]
        right = controls_by_cubic[index + 1][0]
        joint = cubics[index][3]
        deltas.append(abs(joint - ((left + right) / 2)))
    return deltas


def _enforce_junction_symmetry(
    cubics: list[Cubic],
    controls_by_cubic: list[list[complex]],
) -> None:
    for index in range(len(cubics) - 1):
        left = controls_by_cubic[index][-1]
        right = controls_by_cubic[index + 1][0]
        joint = cubics[index][3]
        half_span = (right - left) / 2
        controls_by_cubic[index][-1] = joint - half_span
        controls_by_cubic[index + 1][0] = joint + half_span


def _arc_segment_to_cubic(
    center: complex,
    rx: float,
    ry: float,
    rotation: float,
    start_angle: float,
    end_angle: float,
) -> Cubic:
    alpha = (4 / 3) * math.tan((end_angle - start_angle) / 4)
    p0 = _ellipse_point(center, rx, ry, rotation, start_angle)
    p3 = _ellipse_point(center, rx, ry, rotation, end_angle)
    c1 = p0 + alpha * _ellipse_derivative(rx, ry, rotation, start_angle)
    c2 = p3 - alpha * _ellipse_derivative(rx, ry, rotation, end_angle)
    return p0, c1, c2, p3


def _ellipse_point(
    center: complex,
    rx: float,
    ry: float,
    rotation: float,
    angle: float,
) -> complex:
    cos_rotation = math.cos(rotation)
    sin_rotation = math.sin(rotation)
    x = rx * math.cos(angle)
    y = ry * math.sin(angle)
    return center + complex(
        (x * cos_rotation) - (y * sin_rotation),
        (x * sin_rotation) + (y * cos_rotation),
    )


def _ellipse_derivative(
    rx: float,
    ry: float,
    rotation: float,
    angle: float,
) -> complex:
    cos_rotation = math.cos(rotation)
    sin_rotation = math.sin(rotation)
    x = -rx * math.sin(angle)
    y = ry * math.cos(angle)
    return complex(
        (x * cos_rotation) - (y * sin_rotation),
        (x * sin_rotation) + (y * cos_rotation),
    )


def _cubic_approx_spline(
    cubic: Cubic,
    n: int,
    tolerance: float,
    *,
    check: bool = True,
) -> list[complex] | None:
    if n == 1:
        return _cubic_approx_quadratic(cubic, tolerance, check=check)

    split_cubics = _split_cubic_into_n(*cubic, n)
    next_cubic = split_cubics[0]
    next_q1 = _cubic_approx_control(0, *next_cubic)
    q2 = cubic[0]
    d1 = 0j
    spline = [cubic[0], next_q1]

    for index in range(1, n + 1):
        _c0, c1, c2, c3 = next_cubic
        q0 = q2
        q1 = next_q1

        if index < n:
            next_cubic = split_cubics[index]
            next_q1 = _cubic_approx_control(index / (n - 1), *next_cubic)
            spline.append(next_q1)
            q2 = (q1 + next_q1) / 2
        else:
            q2 = c3

        d0 = d1
        d1 = q2 - c3
        if check and (
            abs(d1) > tolerance
            or not _cubic_farthest_fit_inside(
                d0,
                q0 + (q1 - q0) * (2 / 3) - c1,
                q2 + (q1 - q2) * (2 / 3) - c2,
                d1,
                tolerance,
            )
        ):
            return None

    spline.append(cubic[3])
    return spline


def _cubic_approx_quadratic(
    cubic: Cubic,
    tolerance: float,
    *,
    check: bool,
) -> list[complex] | None:
    q1 = _tangent_intersection(cubic[0], cubic[1], cubic[2], cubic[3])
    if q1 is None:
        if check:
            return None
        q1 = (cubic[1] + cubic[2]) / 2

    c0 = cubic[0]
    c3 = cubic[3]
    c1 = c0 + (q1 - c0) * (2 / 3)
    c2 = c3 + (q1 - c3) * (2 / 3)
    if check and not _cubic_farthest_fit_inside(
        0,
        c1 - cubic[1],
        c2 - cubic[2],
        0,
        tolerance,
    ):
        return None
    return [c0, q1, c3]


def _cubic_approx_control(
    t: float,
    p0: complex,
    p1: complex,
    p2: complex,
    p3: complex,
) -> complex:
    q1_start = p0 + (p1 - p0) * 1.5
    q1_end = p3 + (p2 - p3) * 1.5
    return q1_start + (q1_end - q1_start) * t


def _split_cubic_into_n(
    p0: complex,
    p1: complex,
    p2: complex,
    p3: complex,
    n: int,
) -> list[Cubic]:
    a, b, c, d = _calc_cubic_parameters(p0, p1, p2, p3)
    dt = 1 / n
    delta_2 = dt * dt
    delta_3 = dt * delta_2
    cubics: list[Cubic] = []
    for index in range(n):
        t = index * dt
        t2 = t * t
        a1 = a * delta_3
        b1 = (3 * a * t + b) * delta_2
        c1 = (2 * b * t + c + 3 * a * t2) * dt
        d1 = a * t * t2 + b * t2 + c * t + d
        cubics.append(_calc_cubic_points(a1, b1, c1, d1))
    return cubics


def _calc_cubic_parameters(
    p0: complex,
    p1: complex,
    p2: complex,
    p3: complex,
) -> Cubic:
    c = (p1 - p0) * 3
    b = (p2 - p1) * 3 - c
    d = p0
    a = p3 - d - c - b
    return a, b, c, d


def _calc_cubic_points(
    a: complex,
    b: complex,
    c: complex,
    d: complex,
) -> Cubic:
    p0 = d
    p1 = c / 3 + d
    p2 = (b + c) / 3 + p1
    p3 = a + b + c + d
    return p0, p1, p2, p3


def _cubic_farthest_fit_inside(
    p0: complex,
    p1: complex,
    p2: complex,
    p3: complex,
    tolerance: float,
    depth: int = 0,
) -> bool:
    if all(abs(point) <= tolerance for point in (p0, p1, p2, p3)):
        return True

    mid = (p0 + 3 * (p1 + p2) + p3) * 0.125
    if abs(mid) > tolerance or depth >= _FIT_RECURSION_LIMIT:
        return False

    deriv3 = (p3 + p2 - p1 - p0) * 0.125
    return _cubic_farthest_fit_inside(
        p0,
        (p0 + p1) * 0.5,
        mid - deriv3,
        mid,
        tolerance,
        depth + 1,
    ) and _cubic_farthest_fit_inside(
        mid,
        mid + deriv3,
        (p2 + p3) * 0.5,
        p3,
        tolerance,
        depth + 1,
    )


def _tangent_intersection(
    a: complex,
    b: complex,
    c: complex,
    d: complex,
) -> complex | None:
    ab = b - a
    cd = d - c
    denom = _cross(ab, cd)
    if abs(denom) < _PARALLEL_TOLERANCE:
        return None
    return a + ab * (_cross(c - a, cd) / denom)


def _cross(v1: complex, v2: complex) -> float:
    return (v1.real * v2.imag) - (v1.imag * v2.real)
