# pyrefly: ignore  # import-error
from svg.path import CubicBezier

# pyrefly: ignore  # import-error
from graphviz2drawio.mx.Curve import Curve, _line


def test_line():
    line = _line(complex(-5, 10), complex(-3, 4))
    assert line(0) == -5
    assert line(1) == -8
    assert line(2) == -11


def test_vertical_line_returns_none():
    line = _line(complex(1, 10), complex(1, 4))
    assert line is None


def test_is_linear_uses_absolute_tolerance_on_long_chord():
    cubic = CubicBezier(0j, 250 + 0.005j, 750 - 0.005j, 1000 + 0j)

    assert Curve.is_linear(cubic)


def test_is_linear_rejects_short_chord_outside_absolute_tolerance():
    cubic = CubicBezier(0j, 0.25 + 0.05j, 0.75 - 0.05j, 1 + 0j)

    assert not Curve.is_linear(cubic)
