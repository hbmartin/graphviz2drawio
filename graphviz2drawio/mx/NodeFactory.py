from xml.etree.ElementTree import Element

from graphviz2drawio.models import SVG

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
        fill = g.attrib.get("fill", None)
        stroke = g.attrib.get("stroke", None)

        if (polygon := SVG.get_first(g, "polygon")) is not None:
            rect = rect_from_svg_points(self.coords, polygon.attrib["points"])
            shape = Shape.RECT
            if "stroke" in polygon.attrib:
                stroke = polygon.attrib["stroke"]
            if "fill" in polygon.attrib:
                fill = polygon.attrib["fill"]
        elif (image := SVG.get_first(g, "image")) is not None:
            rect = rect_from_image(self.coords, image.attrib)
            shape = Shape.IMAGE
        elif (ellipse := SVG.get_first(g, "ellipse")) is not None:
            rect = rect_from_ellipse_svg(
                coords=self.coords,
                attrib=ellipse.attrib,  # pytype: disable=attribute-error
            )
            shape = Shape.ELLIPSE
            if "fill" in ellipse.attrib:
                fill = ellipse.attrib["fill"]
            if "stroke" in ellipse.attrib:
                stroke = ellipse.attrib["stroke"]
        else:
            shape = Shape.ELLIPSE

        return Node(
            sid=g.attrib["id"],
            gid=SVG.get_title(g),
            rect=rect,
            texts=texts,
            fill=fill,
            stroke=stroke,
            shape=shape,
        )

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
