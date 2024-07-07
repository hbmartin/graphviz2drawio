from graphviz2drawio.models import SVG
from .Text import Text

from ..models.Errors import MissingTitleError
from .CurveFactory import CurveFactory
from .Edge import Edge


class EdgeFactory:
    def __init__(self, coords) -> None:
        super().__init__()
        self.curve_factory = CurveFactory(coords)

    @staticmethod
    def _get_labels(g) -> list[Text]:
        labels = []
        for tag in g:
            if SVG.is_tag(tag, "text"):
                labels.append(Text.from_svg(tag))

        return labels

    def from_svg(self, g) -> Edge:
        title = SVG.get_title(g)
        if title is None:
            raise MissingTitleError(g)
        fr, to = title.replace("--", "->").split("->")
        fr = fr.split(":")[0]
        to = to.split(":")[0]
        curve = None
        labels = self._get_labels(g)
        if (path := SVG.get_first(g, "path")) is not None:
            if "d" in path.attrib:
                curve = self.curve_factory.from_svg(path.attrib["d"])
        return Edge(sid=g.attrib["id"], fr=fr, to=to, curve=curve, labels=labels)
