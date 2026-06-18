from svg.path import (
    Arc,
    Close,
    CubicBezier,
    Line,
    Move,
    Path,
    QuadraticBezier,
    parse_path,
)

from ..models.CoordsTranslate import CoordsTranslate
from .bezier import (
    Cubic,
    arc_to_cubics,
    cubic_chain_to_quadratic_controls,
    line_to_cubic,
    quadratic_to_cubic,
)
from .Curve import Curve


class CurveFactory:
    def __init__(self, coords: CoordsTranslate) -> None:
        super().__init__()
        self.coords = coords

    def from_svg(self, svg_path: str) -> Curve:
        path: Path = parse_path(svg_path)
        cubics: list[Cubic] = []
        linear_flags: list[bool] = []

        for segment in path:
            if isinstance(segment, Move):
                continue
            if isinstance(segment, CubicBezier):
                cubic = (
                    self.coords.complex_translate(segment.start),
                    self.coords.complex_translate(segment.control1),
                    self.coords.complex_translate(segment.control2),
                    self.coords.complex_translate(segment.end),
                )
                cubics.append(cubic)
                linear_flags.append(Curve.is_linear(segment))
            elif isinstance(segment, QuadraticBezier):
                cubic = quadratic_to_cubic(
                    self.coords.complex_translate(segment.start),
                    self.coords.complex_translate(segment.control),
                    self.coords.complex_translate(segment.end),
                )
                cubics.append(cubic)
                linear_flags.append(Curve.is_linear(CubicBezier(*cubic)))
            elif isinstance(segment, Line | Close):
                start = self.coords.complex_translate(segment.start)
                end = self.coords.complex_translate(segment.end)
                if start != end:
                    cubics.append(line_to_cubic(start, end))
                    linear_flags.append(True)
            elif isinstance(segment, Arc):
                arc_cubics = [
                    tuple(self.coords.complex_translate(point) for point in cubic)
                    for cubic in arc_to_cubics(segment)
                ]
                cubics.extend(arc_cubics)
                linear_flags.extend(False for _cubic in arc_cubics)

        if not cubics:
            start = self.coords.complex_translate(path[0].start)
            end = self.coords.complex_translate(path[-1].end)
            return Curve(start=start, end=end, is_bezier=False, points=[])

        start = cubics[0][0]
        end = cubics[-1][3]
        is_bezier = not all(linear_flags)
        if is_bezier:
            points = cubic_chain_to_quadratic_controls(cubics)
        else:
            points = [cubic[3] for cubic in cubics[:-1]]

        return Curve(start=start, end=end, is_bezier=is_bezier, points=points)
