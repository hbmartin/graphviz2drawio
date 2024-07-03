from graphviz2drawio.models import SVG

from .CurveFactory import CurveFactory
from .Edge import Edge


class EdgeFactory:
    def __init__(self, coords) -> None:
        super().__init__()
        self.curve_factory = CurveFactory(coords)

    def from_svg(self, g) -> Edge:
        fr, to = SVG.get_title(g).replace("--", "->").split("->")
        fr = fr.split(":")[0]
        to = to.split(":")[0]
        gid = f"{fr}->{to}"
        curve = None
        label = SVG.get_text(g)
        if SVG.has(g, "path"):
            path = SVG.get_first(g, "path")
            if "d" in path.attrib:
                curve = self.curve_factory.from_svg(path.attrib["d"])
        return Edge(sid=g.attrib["id"], gid=gid, fr=fr, to=to, curve=curve, label=label)
