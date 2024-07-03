from svg.path import CubicBezier, Move, parse_path

from .Curve import Curve


class CurveFactory:
    def __init__(self, coords) -> None:
        super().__init__()
        self.coords = coords

    def from_svg(self, svg_path) -> Curve:
        path = parse_path(svg_path)
        start = self.coords.complex_translate(path[0].start)
        end = self.coords.complex_translate(path[-1].end)
        cb = None
        cbset = []
        if isinstance(path[0], Move):
            path = [path[i] for i in range(1, len(path))]
        if isinstance(path[0], CubicBezier):
            # TODO: needs to account for multiple bezier in path
            points = [path[0].start, path[0].control1, path[0].control2, path[0].end]
            if not Curve.is_linear(points):
                cb = [self.coords.complex_translate(p) for p in points]

            if len(path) > 1:  # set of curves/points
                for p in path:
                    cbset.append(
                        (
                            self.coords.translate(
                                p.start.real,
                                p.start.imag,
                            ),
                            self.coords.translate(p.end.real, p.end.imag),
                        ),
                    )
        return Curve(start=start, end=end, cb=cb, cbset=cbset)
