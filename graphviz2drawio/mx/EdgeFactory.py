from xml.etree.ElementTree import Element

from graphviz2drawio.models import SVG

from ..models.CoordsTranslate import CoordsTranslate
from ..models.Errors import MissingTitleError
from .CurveFactory import CurveFactory
from .Edge import Edge
from .Text import Text


class EdgeFactory:
    def __init__(self, coords: CoordsTranslate, *, is_directed: bool) -> None:
        super().__init__()
        self.curve_factory = CurveFactory(coords)
        self.is_directed = is_directed

    def from_svg(self, g: Element) -> Edge:
        title = SVG.get_title(g)
        if title is None:
            raise MissingTitleError(g)
        fr, to = title.replace("--", "->").split("->")
        fr = fr.split(":")[0]
        to = to.split(":")[0]
        curve = None
        labels = [Text.from_svg(tag) for tag in g if SVG.is_tag(tag, "text")]
        if (path := SVG.get_first(g, "path")) is not None:
            if "d" in path.attrib:
                curve = self.curve_factory.from_svg(path.attrib["d"])
        return Edge(
            sid=g.attrib["id"],
            fr=fr,
            to=to,
            is_directed=self.is_directed,
            curve=curve,
            labels=labels,
        )
