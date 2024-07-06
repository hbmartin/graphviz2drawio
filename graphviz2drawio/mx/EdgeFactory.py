from graphviz2drawio.models import SVG

from .CurveFactory import CurveFactory
from .Edge import Edge
from ..models.Errors import MissingTitleError


class EdgeFactory:
    def __init__(self, coords) -> None:
        super().__init__()
        self.curve_factory = CurveFactory(coords)

    def from_svg(self, g) -> Edge:
        title = SVG.get_title(g)
        if title is None:
            raise MissingTitleError(g)
        fr, to = title.replace("--", "->").split("->")
        fr = fr.split(":")[0]
        to = to.split(":")[0]
        curve = None
        label = SVG.get_text(g) or ""
        if (path := SVG.get_first(g, "path")) is not None:
            if "d" in path.attrib:
                curve = self.curve_factory.from_svg(path.attrib["d"])
        return Edge(sid=g.attrib["id"], fr=fr, to=to, curve=curve, label=label)
