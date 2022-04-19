from graphviz2drawio.models import SVG
from .CurveFactory import CurveFactory
from .Edge import Edge


class EdgeFactory:
    def __init__(self, coords):
        super(EdgeFactory, self).__init__()
        self.curve_factory = CurveFactory(coords)

    def from_svg(self, g):
        gid = SVG.get_title(g).replace("--", "->")
        fr, to = gid.split("->")
        curve = None
        label = SVG.get_text(g)
        if SVG.has(g, "path"):
            path = SVG.get_first(g, "path")
            if "d" in path.attrib:
                curve = self.curve_factory.from_svg(path.attrib["d"])
        return Edge(sid=g.attrib["id"], gid=gid, fr=fr, to=to, curve=curve, label=label)
