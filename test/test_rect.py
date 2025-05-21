import cmath

# pyrefly: ignore  # import-error
from graphviz2drawio.models.Rect import Rect


def test_closest_point_along_perimeter():
    rect = Rect(x=432.0, y=543.6, width=100.8, height=100.8)
    p1 = rect.closest_point_along_perimeter(544.08, 617.4)
    assert p1 == (532.8, 617.4)


def test_relative_location_along_perimeter():
    rect = Rect(x=432.0, y=543.6, width=100.8, height=100.8)
    p1 = rect.relative_location_along_perimeter(complex(544.08, 617.4))
    assert cmath.isclose(complex(*p1), complex(1.0, 0.73), abs_tol=0.01)
