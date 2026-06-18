from itertools import chain, pairwise

from svg.path import (
    Arc,
    Close,
    CubicBezier,
    Line,
    Move,
    QuadraticBezier,
    parse_path,
)

from graphviz2drawio.models.CoordsTranslate import CoordsTranslate
from graphviz2drawio.mx.bezier import (
    MAX_QUAD_ERROR,
    Cubic,
    arc_to_cubics,
    line_to_cubic,
    quadratic_to_cubic,
)
from graphviz2drawio.mx.CurveFactory import CurveFactory


def test_drawio_renderer_simulation_stays_within_error_bound():
    path_data = [
        "M0,0 C20,30 60,30 80,0",
        "M0,0 C25,60 55,-60 80,0",
        "M50,50 C10,20 10,80 50,50",
        (
            "M0,0 C10,20 30,20 40,0 C50,-20 70,-20 80,0 "
            "C90,20 110,20 120,0 C130,-20 150,-20 160,0 "
            "C170,20 190,20 200,0"
        ),
        "M0,0 C20,20 40,0 60,0 L80,0 C90,0 100,20 120,20",
        "M10,0 A10,10 0 1 1 0,-10",
    ]

    for svg_path in path_data:
        curve = CurveFactory(CoordsTranslate(0, 0)).from_svg(svg_path)
        cubics = _path_to_cubics(svg_path)
        points = [curve.start, *curve.points, curve.end]

        assert curve.is_bezier
        assert _max_deviation(cubics, points) <= MAX_QUAD_ERROR + 0.05


def test_drawio_curved_quads_matches_implied_midpoint_model():
    points = [0j, 10 + 10j, 20 + 10j, 30 + 0j]

    quads = _drawio_curved_quads(points)

    assert quads == [
        (0j, 10 + 10j, 15 + 10j),
        (15 + 10j, 20 + 10j, 30 + 0j),
    ]


def _path_to_cubics(svg_path: str) -> list[Cubic]:
    cubics: list[Cubic] = []
    for segment in parse_path(svg_path):
        if isinstance(segment, Move):
            continue
        if isinstance(segment, CubicBezier):
            cubics.append(
                (segment.start, segment.control1, segment.control2, segment.end),
            )
        elif isinstance(segment, QuadraticBezier):
            cubics.append(
                quadratic_to_cubic(segment.start, segment.control, segment.end),
            )
        elif isinstance(segment, Line | Close):
            if segment.start != segment.end:
                cubics.append(line_to_cubic(segment.start, segment.end))
        elif isinstance(segment, Arc):
            cubics.extend(arc_to_cubics(segment))
    return cubics


def _max_deviation(cubics, points: list[complex]) -> float:
    cubic_polyline = _sample_cubics(cubics)
    quad_polyline = _sample_quads(_drawio_curved_quads(points))
    return max(
        chain(
            (_distance_to_polyline(point, quad_polyline) for point in cubic_polyline),
            (_distance_to_polyline(point, cubic_polyline) for point in quad_polyline),
        ),
    )


def _drawio_curved_quads(
    points: list[complex],
) -> list[tuple[complex, complex, complex]]:
    quads = []
    current = points[0]
    for index in range(1, len(points) - 2):
        end = (points[index] + points[index + 1]) / 2
        quads.append((current, points[index], end))
        current = end
    quads.append((current, points[-2], points[-1]))
    return quads


def _sample_cubics(cubics) -> list[complex]:
    return [
        _cubic_point(cubic, sample / 80) for cubic in cubics for sample in range(81)
    ]


def _sample_quads(quads) -> list[complex]:
    return [
        _quadratic_point(*quad, sample / 80) for quad in quads for sample in range(81)
    ]


def _distance_to_polyline(point: complex, polyline: list[complex]) -> float:
    return min(
        _distance_to_segment(point, start, end) for start, end in pairwise(polyline)
    )


def _distance_to_segment(point: complex, start: complex, end: complex) -> float:
    segment = end - start
    if segment == 0:
        return abs(point - start)
    projection = ((point - start).real * segment.real) + (
        (point - start).imag * segment.imag
    )
    t = min(max(projection / (abs(segment) ** 2), 0), 1)
    return abs(point - (start + t * segment))


def _quadratic_point(
    p0: complex,
    c: complex,
    p1: complex,
    t: float,
) -> complex:
    mt = 1 - t
    return (mt * mt * p0) + (2 * mt * t * c) + (t * t * p1)


def _cubic_point(cubic, t: float) -> complex:
    mt = 1 - t
    return (
        (mt * mt * mt * cubic[0])
        + (3 * mt * mt * t * cubic[1])
        + (3 * mt * t * t * cubic[2])
        + (t * t * t * cubic[3])
    )
