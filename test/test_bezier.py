import math
from itertools import pairwise

from svg.path import parse_path

from graphviz2drawio.mx.bezier import (
    MAX_QUAD_ERROR,
    MAX_SEGMENTS_PER_CUBIC,
    arc_to_cubics,
    cubic_chain_to_quadratic_controls,
    cubic_to_quadratic_controls,
    line_to_cubic,
    quadratic_to_cubic,
)


def test_single_control_for_gentle_cubic():
    cubic = (0j, 1 + 0.2j, 3 + 0.2j, 4 + 0j)

    controls = cubic_to_quadratic_controls(*cubic)

    assert len(controls) == 1
    assert _max_deviation_for_cubic(cubic, controls) <= MAX_QUAD_ERROR


def test_control_count_grows_with_curvature():
    gentle = (0j, 1 + 0.2j, 3 + 0.2j, 4 + 0j)
    hairpin = (0j, 0 + 80j, 100 - 80j, 100 + 0j)

    gentle_controls = cubic_to_quadratic_controls(*gentle)
    hairpin_controls = cubic_to_quadratic_controls(*hairpin)

    assert len(hairpin_controls) > len(gentle_controls)


def test_error_bound_respected_for_common_shapes():
    cubics = [
        (0j, 25 + 40j, 55 + 40j, 80 + 0j),
        (0j, 25 + 60j, 55 - 60j, 80 + 0j),
        (0j, 0 + 40j, 60 - 40j, 60 + 0j),
    ]

    for cubic in cubics:
        controls = cubic_to_quadratic_controls(*cubic)
        assert _max_deviation_for_cubic(cubic, controls) <= MAX_QUAD_ERROR + 1e-6


def test_cap_returns_best_effort_without_raising():
    controls = cubic_to_quadratic_controls(
        0j,
        0 + 500j,
        1000 - 500j,
        1000 + 0j,
        max_err=1e-12,
    )

    assert len(controls) == MAX_SEGMENTS_PER_CUBIC


def test_min_n_is_respected():
    controls = cubic_to_quadratic_controls(
        0j,
        1 + 0.2j,
        3 + 0.2j,
        4 + 0j,
        max_err=100,
        min_n=5,
    )

    assert len(controls) == 5


def test_line_to_cubic_controls_are_collinear():
    cubic = line_to_cubic(1 + 1j, 7 + 4j)
    chord = cubic[3] - cubic[0]

    assert all(math.isclose(_cross(chord, point - cubic[0]), 0) for point in cubic)


def test_two_cubic_chain_junction_lands_on_implied_midpoint():
    cubics = [
        (0j, 10 + 0j, 20 + 0j, 30 + 0j),
        (30 + 0j, 40 + 0j, 50 + 0j, 60 + 0j),
    ]

    controls = cubic_chain_to_quadratic_controls(cubics)

    assert any(abs(joint - 30) < 1e-9 for joint in _implied_joints(controls))


def test_three_cubic_chain_junctions_land_exactly():
    cubics = [
        (0j, 10 + 10j, 20 + 10j, 30 + 0j),
        (30 + 0j, 40 - 10j, 50 - 10j, 60 + 0j),
        (60 + 0j, 70 + 10j, 80 + 10j, 90 + 0j),
    ]

    controls = cubic_chain_to_quadratic_controls(cubics)
    joints = _implied_joints(controls)

    assert any(abs(joint - (30 + 0j)) < 1e-9 for joint in joints)
    assert any(abs(joint - (60 + 0j)) < 1e-9 for joint in joints)


def test_chain_junction_tangent_direction_is_preserved():
    cubics = [
        (0j, 10 + 10j, 20 + 10j, 30 + 0j),
        (30 + 0j, 40 - 10j, 50 - 10j, 60 + 0j),
    ]

    controls = cubic_chain_to_quadratic_controls(cubics)
    left, right = _controls_around_joint(controls, 30 + 0j)
    adjusted_tangent = right - left
    original_tangent = cubics[1][1] - cubics[1][0]

    assert math.isclose(
        _cross(adjusted_tangent, original_tangent),
        0,
        abs_tol=1e-9,
    )


def test_quadratic_to_cubic_is_exact_degree_elevation():
    quadratic = (0j, 5 + 10j, 10 + 0j)
    cubic = quadratic_to_cubic(*quadratic)

    for sample in range(21):
        t = sample / 20
        assert abs(_quadratic_point(*quadratic, t) - _cubic_point(cubic, t)) < 1e-9


def test_arc_sweep_split_and_endpoints():
    arc = parse_path("M 10,0 A 10,10 0 1 1 0,-10")[1]

    cubics = arc_to_cubics(arc)

    assert len(cubics) == 3
    assert cubics[0][0] == arc.start
    assert cubics[-1][3] == arc.end


def test_arc_radial_error_is_small():
    arc = parse_path("M 10,0 A 10,10 0 1 1 0,-10")[1]

    cubics = arc_to_cubics(arc)
    max_radial_error = max(
        abs(abs(_cubic_point(cubic, sample / 50)) - 10)
        for cubic in cubics
        for sample in range(51)
    )

    assert max_radial_error < 0.01


def _implied_joints(controls: list[complex]) -> list[complex]:
    return [(left + right) / 2 for left, right in pairwise(controls)]


def _controls_around_joint(
    controls: list[complex],
    joint: complex,
) -> tuple[complex, complex]:
    for left, right in pairwise(controls):
        if abs(((left + right) / 2) - joint) < 1e-9:
            return left, right
    message = f"joint {joint} not found"
    raise AssertionError(message)


def _max_deviation_for_cubic(cubic, controls: list[complex]) -> float:
    segment_count = len(controls)
    quads = _drawio_curved_quads([cubic[0], *controls, cubic[3]])
    max_deviation = 0.0
    for segment_index, quad in enumerate(quads):
        for sample in range(51):
            u = sample / 50
            cubic_t = (segment_index + u) / segment_count
            max_deviation = max(
                max_deviation,
                abs(_quadratic_point(*quad, u) - _cubic_point(cubic, cubic_t)),
            )
    return max_deviation


def _drawio_curved_quads(points: list[complex]) -> list[tuple[complex, complex, complex]]:
    quads = []
    current = points[0]
    for index in range(1, len(points) - 2):
        end = (points[index] + points[index + 1]) / 2
        quads.append((current, points[index], end))
        current = end
    quads.append((current, points[-2], points[-1]))
    return quads


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


def _cross(v1: complex, v2: complex) -> float:
    return (v1.real * v2.imag) - (v1.imag * v2.real)
