import cmath

from svg.path import CubicBezier, Path, parse_path, QuadraticBezier

from .Curve import Curve
from .bezier import subdivide_inflections, approximate_cubic_bezier_as_quadratic
from ..models.CoordsTranslate import CoordsTranslate


class CurveFactory:
    def __init__(self, coords: CoordsTranslate) -> None:
        super().__init__()
        self.coords = coords

    def from_svg(self, svg_path: str) -> Curve:
        path: Path = parse_path(svg_path)
        points: list[complex] = []
        is_bezier = not all(map(Curve.is_linear, filter(_is_cubic, path)))

        for p in path:
            if isinstance(p, QuadraticBezier):
                points.append(self.coords.complex_translate(p.control))
            elif isinstance(p, CubicBezier):
                if Curve.is_linear(p):
                    points.append(self.coords.complex_translate(p.start))
                else:
                    split_cubes = subdivide_inflections(
                        p.start, p.control1, p.control2, p.end
                    )
                    for cube in split_cubes:
                        points.append(
                            self.coords.complex_translate(
                                approximate_cubic_bezier_as_quadratic(*cube)[1]
                            )
                        )

        start = self.coords.complex_translate(path[0].start)
        end = self.coords.complex_translate(path[-1].end)

        if len(points) > 0 and cmath.isclose(start, points[0], rel_tol=0.1):
            points = points[1:]

        return Curve(start=start, end=end, is_bezier=is_bezier, points=points)

def _is_cubic(p):
    return isinstance(p, CubicBezier)