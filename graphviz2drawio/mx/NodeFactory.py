from xml.etree.ElementTree import Element

from graphviz2drawio.models import SVG

from ..models.Errors import MissingIdentifiersError
from . import Shape
from .Node import Node
from .RectFactory import rect_from_ellipse_svg, rect_from_image, rect_from_svg_points
from .Text import Text


class NodeFactory:
    def __init__(self, coords) -> None:
        super().__init__()
        self.coords = coords

    def from_svg(self, g: Element) -> Node:
        texts = self._extract_texts(g)
        rect = None
        fill = None
        stroke = None

        if (polygon := SVG.get_first(g, "polygon")) is not None:
            rect = rect_from_svg_points(self.coords, polygon.attrib["points"])
            shape = Shape.RECT
            fill, stroke = self._extract_fill_and_stroke(polygon)
        elif (image := SVG.get_first(g, "image")) is not None:
            rect = rect_from_image(self.coords, image.attrib)
            shape = Shape.IMAGE
        elif (ellipse := SVG.get_first(g, "ellipse")) is not None:
            rect = rect_from_ellipse_svg(
                coords=self.coords,
                attrib=ellipse.attrib,  # pytype: disable=attribute-error
            )
            shape = (
                Shape.ELLIPSE
                if SVG.count_tags(g, "ellipse") == 1
                else Shape.DOUBLE_CIRCLE
            )
            fill, stroke = self._extract_fill_and_stroke(ellipse)
        else:
            shape = Shape.ELLIPSE

        sid = g.attrib["id"]
        gid = SVG.get_title(g)

        if sid is None or gid is None:
            raise MissingIdentifiersError(sid, gid)

        return Node(
            sid=sid,
            gid=gid,
            rect=rect,
            texts=texts,
            fill=fill,
            stroke=stroke,
            shape=shape,
        )

    @staticmethod
    def _extract_fill_and_stroke(g: Element) -> tuple[str | None, str | None]:
        return g.attrib.get("fill", None), g.attrib.get("stroke", None)

    @staticmethod
    def _extract_texts(g: Element):
        texts = []
        current_text = None
        for t in g:
            if SVG.is_tag(t, "text"):
                if current_text is None:
                    current_text = Text.from_svg(t)
                else:
                    current_text.text += f"<br/>{t.text}"
            elif current_text is not None:
                texts.append(current_text)
                current_text = None
        if current_text is not None:
            texts.append(current_text)
        return texts
