from graphviz2drawio.models import SVG
from .CurveFactory import CurveFactory
from .Edge import Edge
from .Text import Text


class EdgeFactory:
    def __init__(self, coords):
        super(EdgeFactory, self).__init__()
        self.curve_factory = CurveFactory(coords)

    def from_svg(self, g):
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

        gid = SVG.get_title(g).replace("--", "->")
        fr, to = gid.split("->")
        curve = None
        if SVG.has(g, "path"):
            path = SVG.get_first(g, "path")
            if "d" in path.attrib:
                curve = self.curve_factory.from_svg(path.attrib["d"])
        return Edge(sid=g.attrib["id"], gid=gid, fr=fr, to=to, curve=curve,texts=texts)
