import cmath

from svg.path import CubicBezier, Path, QuadraticBezier, parse_path

from ..models.CoordsTranslate import CoordsTranslate
from .bezier import approximate_cubic_bezier_as_quadratic, subdivide_inflections
from .Curve import Curve


class CurveFactory:
    def __init__(self, coords: CoordsTranslate) -> None:
        super().__init__()
        self.coords = coords

    def from_svg(self, svg_path: str) -> Curve:
        path: Path = parse_path(svg_path)
        points: list[complex] = []
        is_bezier = not all(map(Curve.is_linear, filter(_is_cubic, path)))

        for segment in path:
            if isinstance(segment, QuadraticBezier):
                points.append(self.coords.complex_translate(segment.control))
            elif isinstance(segment, CubicBezier):
                if Curve.is_linear(segment):
                    points.append(self.coords.complex_translate(segment.start))
                else:
                    split_cubes = subdivide_inflections(
                        segment.start, segment.control1, segment.control2, segment.end,
                    )
                    for cube in split_cubes:
                        if cube:
                            points.append(  # noqa: PERF401
                                self.coords.complex_translate(
                                    approximate_cubic_bezier_as_quadratic(*cube)[1],
                                ),
                            )

        start = self.coords.complex_translate(path[0].start)
        end = self.coords.complex_translate(path[-1].end)

        if len(points) > 0 and cmath.isclose(start, points[0], rel_tol=0.1):
            points = points[1:]

        return Curve(start=start, end=end, is_bezier=is_bezier, points=points)


def _is_cubic(p):
    return isinstance(p, CubicBezier)
