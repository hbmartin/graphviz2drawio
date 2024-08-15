from xml.etree.ElementTree import Element

from graphviz2drawio.models import SVG

from ..models.CoordsTranslate import CoordsTranslate
from ..models.Errors import MissingIdentifiersError
from . import Shape
from .Node import Node
from .RectFactory import rect_from_ellipse_svg, rect_from_image, rect_from_svg_points
from .Text import Text
from .utils import adjust_color_opacity


class NodeFactory:
    def __init__(self, coords: CoordsTranslate) -> None:
        super().__init__()
        self.coords = coords

    def from_svg(self, g: Element, labelloc: str) -> Node:
        sid = g.attrib["id"]
        gid = SVG.get_title(g)
        rect = None
        fill = None
        stroke = None
        stroke_width = None
        dashed = False

        if sid is None or gid is None:
            raise MissingIdentifiersError(sid, gid)

        if (inner_g := SVG.get_first(g, "g")) is not None:
            if (inner_a := SVG.get_first(inner_g, "a")) is not None:
                g = inner_a

        if (polygon := SVG.get_first(g, "polygon")) is not None:
            rect = rect_from_svg_points(self.coords, polygon.attrib["points"])
            shape = Shape.RECT
            fill, stroke = self._extract_fill_and_stroke(polygon)
            stroke_width = polygon.attrib.get("stroke-width", "1")
            if "stroke-dasharray" in polygon.attrib:
                dashed = True
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
            stroke_width = ellipse.attrib.get("stroke-width", "1")
            if "stroke-dasharray" in ellipse.attrib:
                dashed = True
        else:
            shape = Shape.ELLIPSE

        texts, text_offset = self._extract_texts(g)

        return Node(
            sid=sid,
            gid=gid,
            rect=rect,
            texts=texts,
            fill=fill,
            stroke=stroke,
            shape=shape,
            labelloc=labelloc,
            stroke_width=stroke_width,
            text_offset=text_offset,
            dashed=dashed,
        )

    @staticmethod
    def _extract_fill_and_stroke(g: Element) -> tuple[str | None, str | None]:
        fill, stroke = g.attrib.get("fill", None), g.attrib.get("stroke", None)
        if "fill-opacity" in g.attrib:
            fill = adjust_color_opacity(fill, float(g.attrib["fill-opacity"]))
        if "stroke-opacity" in g.attrib:
            stroke = adjust_color_opacity(stroke, float(g.attrib["stroke-opacity"]))
        return fill, stroke

    def _extract_texts(self, g: Element) -> tuple[list[Text], complex | None]:
        texts = []
        current_text = None
        offset = None
        for t in g:
            if SVG.is_tag(t, "text"):
                if current_text is None:
                    current_text = Text.from_svg(t)
                else:
                    current_text.text += f"<br/>{t.text}"
                if offset is None and current_text is not None:
                    x = None
                    y = None
                    try:
                        x = float(t.attrib.get("x", "x"))
                        y = float(t.attrib.get("y", "y")) - current_text.size
                    except ValueError:
                        pass
                    if x is not None and y is not None:
                        offset = self.coords.complex_translate(complex(x, y))
            elif current_text is not None:
                texts.append(current_text)
                current_text = None
        if current_text is not None:
            texts.append(current_text)
        return texts, offset
