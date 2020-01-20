from svg.path import CubicBezier
from svg.path import parse_path
from .Curve import Curve


class CurveFactory:
    def __init__(self, coords):
        super(CurveFactory, self).__init__()
        self.coords = coords

    def from_svg(self, svg_path):
        path = parse_path(svg_path)
        start = self.coords.complex_translate(path[0].start)
        end = self.coords.complex_translate(path[1].end)
        cb = None
        cbset = []
        if isinstance(path[1], CubicBezier):
            # TODO: needs to account for multiple bezier in path
            points = [path[1].start, path[1].control1,
                      path[1].control2, path[1].end]
            if not Curve.is_linear(points):
                cb = [self.coords.complex_translate(p) for p in points]

            if len(path) > 2:  # set of curves/points
                for r in range(1, len(path)):
                    cbset.append(
                        (
                            self.coords.translate(
                                path[r].start.real, path[r].start.imag),
                            self.coords.translate(
                                path[r].end.real, path[r].end.imag)
                        )
                    )
        return Curve(start=start, end=end, cb=cb, cbset=cbset)
