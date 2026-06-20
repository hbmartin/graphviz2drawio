import re
from dataclasses import dataclass
from xml.etree.ElementTree import Element

from ..models import SVG
from ..models.CoordsTranslate import CoordsTranslate
from ..models.Errors import MissingIdentifiersError
from ..models.Rect import Rect
from . import MxConst, Shape
from .MxConst import DEFAULT_STROKE_WIDTH
from .Node import Gradient, Node
from .RectFactory import (
    rect_from_ellipse_svg,
    rect_from_image,
    rect_from_svg_path,
    rect_from_svg_points,
)
from .Text import Text
from .utils import adjust_color_opacity


@dataclass(frozen=True)
class _NodeShape:
    rect: Rect | None = None
    fill: str | Gradient = MxConst.NONE
    stroke: str = MxConst.NONE
    shape: str = Shape.ELLIPSE
    stroke_width: str = DEFAULT_STROKE_WIDTH
    dashed: bool = False


class NodeFactory:
    def __init__(self, coords: CoordsTranslate) -> None:
        super().__init__()
        self.coords = coords

    def from_svg(
        self,
        g: Element,
        labelloc: str,
        gradients: dict[str, Gradient],
    ) -> Node:
        sid = g.attrib["id"]
        gid = SVG.get_title(g)

        if sid is None or gid is None:
            raise MissingIdentifiersError(sid, gid)

        g = self._unwrap_anchor(g)
        node_shape = self._extract_shape(g, gradients)
        texts, text_offset = self._extract_texts(g)

        return Node(
            sid=sid,
            gid=gid,
            rect=node_shape.rect,
            texts=texts,
            fill=node_shape.fill,
            stroke=node_shape.stroke,
            shape=node_shape.shape,
            labelloc=labelloc,
            stroke_width=node_shape.stroke_width,
            text_offset=text_offset,
            dashed=node_shape.dashed,
        )

    @staticmethod
    def _unwrap_anchor(g: Element) -> Element:
        inner_g = SVG.get_first(g, "g")
        if inner_g is None:
            return g
        inner_a = SVG.get_first(inner_g, "a")
        return inner_a if inner_a is not None else g

    def _extract_shape(
        self,
        g: Element,
        gradients: dict[str, Gradient],
    ) -> _NodeShape:
        if (polygon := SVG.get_first(g, "polygon")) is not None:
            return _NodeShape(
                rect=rect_from_svg_points(self.coords, polygon.attrib["points"]),
                fill=self._extract_fill(polygon, gradients),
                stroke=self._extract_stroke(polygon),
                shape=Shape.RECT,
                stroke_width=polygon.attrib.get("stroke-width", DEFAULT_STROKE_WIDTH),
                dashed="stroke-dasharray" in polygon.attrib,
            )

        if (image := SVG.get_first(g, "image")) is not None:
            return _NodeShape(
                rect=rect_from_image(self.coords, image.attrib),
                shape=Shape.IMAGE,
            )

        if (ellipse := SVG.get_first(g, "ellipse")) is not None:
            shape = Shape.ELLIPSE
            if len(SVG.findall_recursive(g, "ellipse")) != 1:
                shape = Shape.DOUBLE_CIRCLE
            return _NodeShape(
                rect=rect_from_ellipse_svg(
                    coords=self.coords,
                    attrib=ellipse.attrib,
                ),
                fill=self._extract_fill(ellipse, gradients),
                stroke=self._extract_stroke(ellipse),
                shape=shape,
                stroke_width=ellipse.attrib.get("stroke-width", DEFAULT_STROKE_WIDTH),
                dashed="stroke-dasharray" in ellipse.attrib,
            )

        if (path := SVG.get_first(g, "path")) is not None:
            return _NodeShape(
                rect=rect_from_svg_path(self.coords, path.attrib["d"]),
                fill=self._extract_fill(path, gradients),
                stroke=self._extract_stroke(path),
                shape=Shape.RECT,
            )

        return _NodeShape()

    _fill_url_re = re.compile(r"url\(#([^)]+)\)")

    @staticmethod
    def _extract_fill(g: Element, gradients: dict[str, Gradient]) -> str | Gradient:
        fill = g.attrib.get("fill", MxConst.NONE)
        if fill.startswith("url"):
            match = NodeFactory._fill_url_re.search(fill)
            if match is not None:
                return gradients[match.group(1)]
        if "fill-opacity" in g.attrib and fill != MxConst.NONE:
            fill = adjust_color_opacity(fill, float(g.attrib["fill-opacity"]))
        return fill

    @staticmethod
    def _extract_stroke(g: Element) -> str:
        stroke = g.attrib.get("stroke", MxConst.NONE)
        if "stroke-opacity" in g.attrib and stroke != MxConst.NONE:
            stroke = adjust_color_opacity(stroke, float(g.attrib["stroke-opacity"]))
        return stroke

    def _extract_texts(self, g: Element) -> tuple[list[Text], complex | None]:
        texts = []
        current_text: Text | None = None
        offset: complex | None = None
        # pyrefly: ignore  # unknown
        for t in g:
            if SVG.is_tag(t, "text"):
                current_text = self._append_text(current_text, t)
                if offset is None and current_text is not None:
                    offset = self._extract_text_offset(t, current_text)
                continue

            self._flush_text(texts, current_text)
            current_text = None

        self._flush_text(texts, current_text)
        return texts, offset

    @staticmethod
    def _append_text(current_text: Text | None, t: Element) -> Text | None:
        if current_text is None:
            return Text.from_svg(t)
        current_text.text += f"<br/>{t.text}"
        return current_text

    @staticmethod
    def _flush_text(texts: list[Text], current_text: Text | None) -> None:
        if current_text is not None:
            texts.append(current_text)

    def _extract_text_offset(self, t: Element, text: Text) -> complex | None:
        origin = self._text_origin(t, text.size)
        if origin is None:
            return None
        return self.coords.complex_translate(origin)

    @staticmethod
    def _text_origin(t: Element, text_size: float) -> complex | None:
        try:
            x = float(t.attrib.get("x", "x"))
            y = float(t.attrib.get("y", "y")) - text_size
        except ValueError:
            return None
        return complex(x, y)
