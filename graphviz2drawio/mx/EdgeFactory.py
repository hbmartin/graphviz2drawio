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
        gid_template = "{}->{}"
        sp_fr = fr.split(":")
        sp_to = to.split(":")
        if len(sp_fr) == 2:
            fr = sp_fr[0]
        if len(sp_to) == 2:
            to = sp_to[0]
        gid = gid_template.format(fr, to)
        curve = None
        if SVG.has(g, "path"):
            path = SVG.get_first(g, "path")
            if "d" in path.attrib:
                curve = self.curve_factory.from_svg(path.attrib["d"])
        return Edge(sid=g.attrib["id"], gid=gid, fr=fr, to=to, curve=curve)
