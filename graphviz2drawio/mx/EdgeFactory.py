from xml.etree.ElementTree import Element

from ..models import SVG, DotAttr

from ..models.CoordsTranslate import CoordsTranslate
from .CurveFactory import CurveFactory
from .Edge import Edge
from .MxConst import DEFAULT_STROKE_WIDTH
from .Text import Text
from .utils import adjust_color_opacity


class EdgeFactory:
    def __init__(self, coords: CoordsTranslate, *, is_directed: bool) -> None:
        super().__init__()
        self.curve_factory = CurveFactory(coords)
        self.is_directed = is_directed

    def from_svg(self, g: Element, title: str) -> Edge:
        fr, to = title.replace("--", "->").split("->")
        curve = None
        stroke = "#000000"
        stroke_width = DEFAULT_STROKE_WIDTH
        line_style = None
        # pyrefly: ignore  # bad-assignment
        labels: list[Text] = [
            text_from_tag
            for tag in g
            if SVG.is_tag(tag, "text")
            and (text_from_tag := Text.from_svg(tag)) is not None
        ]
        if (path := SVG.get_first(g, "path")) is not None:
            if "d" in path.attrib:
                curve = self.curve_factory.from_svg(path.attrib["d"])
            if "stroke" in path.attrib:
                stroke = path.attrib["stroke"]
                if "stroke-opacity" in path.attrib:
                    stroke = adjust_color_opacity(
                        stroke,
                        float(path.attrib["stroke-opacity"]),
                    )
            if "stroke-width" in path.attrib:
                stroke_width = path.attrib["stroke-width"]
            if "stroke-dasharray" in path.attrib:
                line_style = DotAttr.DASHED
        return Edge(
            sid=g.attrib["id"],
            fr=fr,
            to=to,
            is_directed=self.is_directed,
            curve=curve,
            labels=labels,
            stroke=stroke,
            stroke_width=stroke_width,
            line_style=line_style,
        )
