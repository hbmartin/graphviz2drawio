from svg.path import CubicBezier, Path, parse_path

from .Curve import Curve


class CurveFactory:
    def __init__(self, coords) -> None:
        super().__init__()
        self.coords = coords

    def from_svg(self, svg_path: str) -> Curve:
        path: Path = parse_path(svg_path)
        print(path)
        print("")
        start = self.coords.complex_translate(path[0].start)
        end = self.coords.complex_translate(path[-1].end)
        cb = None
        cbset = []

        for p in path:
            if not isinstance(p, CubicBezier):
                continue
            # TODO: Need to save roundedness for Mx styling
            # TODO: need to check linearity for all segments
            if not Curve.is_linear(p):
                cb = [self.coords.complex_translate(p) for p in points]
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
