from svg.path import CubicBezier
from svg.path import parse_path
from . import FromSvgFactory
from graphviz2drawio.svg import SvgUtils
from graphviz2drawio.models import Curve
from graphviz2drawio.models import Edge


class EdgeFactory(FromSvgFactory):
    def from_svg(self, g):
        gid = SvgUtils.get_title(g).replace("--", "->")
        fr, to = gid.split("->")
        curve = None
        if SvgUtils.has(g, "path"):
            path = SvgUtils.get_first(g, "path")
            if "d" in path.attrib:
                curve = self.curve_from_svg(path.attrib["d"])
        return Edge(sid=g.attrib["id"], gid=gid, fr=fr, to=to, curve=curve)

    def curve_from_svg(self, svg_path):
        path = parse_path(svg_path)
        start = self.coords.complex_translate(path[0].start)
        end = self.coords.complex_translate(path[1].end)
        cb = None
        if isinstance(path[1], CubicBezier):
            # TODO: needs to account for multiple bezier in path
            points = [path[1].start, path[1].control1, path[1].control2, path[1].end]
            if not Curve.is_linear(points):
                cb = [self.coords.complex_translate(p) for p in points]
        return Curve(start=start, end=end, cb=cb)