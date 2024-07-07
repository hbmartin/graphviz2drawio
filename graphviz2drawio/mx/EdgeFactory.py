from graphviz2drawio.models import SVG

from ..models.Errors import MissingTitleError
from .CurveFactory import CurveFactory
from .Edge import Edge
from .Text import Text


class EdgeFactory:
    def __init__(self, coords) -> None:
        super().__init__()
        self.curve_factory = CurveFactory(coords)

    def _get_labels(g):
      texts = []
      current_text = None
      for t in g:
         if SVG.is_tag(t, "text"):
             if current_text is None:
                 current_text = Text.from_svg(t)
             else:
                 current_text.text += "<br/>" + t.text
         elif current_text is not None:
             texts.append(current_text)
             current_text = None
      if current_text is not None:
         texts.append(current_text)
      return texts

    def from_svg(self, g) -> Edge:
        title = SVG.get_title(g)
        if title is None:
            raise MissingTitleError(g)
        fr, to = title.replace("--", "->").split("->")
        fr = fr.split(":")[0]
        to = to.split(":")[0]
        curve = None
        labels = _get_labels(g)
        if (path := SVG.get_first(g, "path")) is not None:
            if "d" in path.attrib:
                curve = self.curve_factory.from_svg(path.attrib["d"])
        return Edge(sid=g.attrib["id"], fr=fr, to=to, curve=curve, labels=labels)
