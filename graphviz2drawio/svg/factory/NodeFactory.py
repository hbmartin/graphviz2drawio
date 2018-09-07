from . import FromSvgFactory
from graphviz2drawio.svg import SvgUtils
from graphviz2drawio.mx import MxConst
from graphviz2drawio.models import Node
from graphviz2drawio.models import Rect
from graphviz2drawio.models import Text


class NodeFactory(FromSvgFactory):
    def from_svg(self, g):
        texts = []
        current_text = None
        for t in g:
            if SvgUtils.is_tag(t, "text"):
                if current_text is None:
                    current_text = self.text_from_svg(t)
                else:
                    current_text.text += "<br/>" + t.text
            elif current_text is not None:
                texts.append(current_text)
                current_text = None
        if current_text is not None:
            texts.append(current_text)

        if SvgUtils.has(g, "polygon"):
            rect = self.rect_from_svg_points(
                SvgUtils.get_first(g, "polygon").attrib["points"]
            )
        else:
            rect = self.rect_from_ellipse_svg(SvgUtils.get_first(g, "ellipse").attrib)

        stroke = None
        if SvgUtils.has(g, "polygon"):
            polygon = SvgUtils.get_first(g, "polygon")
            if "stroke" in polygon.attrib:
                stroke = polygon.attrib["stroke"]

        return Node(
            sid=g.attrib["id"],
            gid=SvgUtils.get_title(g),
            rect=rect,
            texts=texts,
            fill=g.attrib.get("fill", None),
            stroke=stroke,
        )

    def rect_from_svg_points(self, svg):
        points = svg.split(" ")
        points = [self.coords.translate(*p.split(",")) for p in points]
        min_x, min_y = points[0]
        width = 0
        height = 0
        for p in points:
            if p[0] < min_x:
                min_x = p[0]
            if p[1] < min_y:
                min_y = p[1]
        for p in points:
            test_width = p[0] - min_x
            test_height = p[1] - min_y
            if test_width > width:
                width = test_width
            if test_height > height:
                height = test_height
        return Rect(x=min_x, y=min_y, width=width, height=height)

    def rect_from_ellipse_svg(self, attrib):
        cx = float(attrib["cx"])
        cy = float(attrib["cy"])
        rx = float(attrib["rx"])
        ry = float(attrib["ry"])
        x, y = self.coords.translate(cx, cy)
        return Rect(x=x - rx, y=y - ry, width=rx * 2, height=ry * 2)

    def text_from_svg(self, t):
        return Text(
            text=t.text.replace("<", "&lt;").replace(">", "&gt;"),
            anchor=t.attrib.get("text-anchor", None),
            family=t.attrib.get("font-family", MxConst.DEFAULT_FONT_FAMILY),
            size=float(t.attrib.get("font-size", MxConst.DEFAULT_TEXT_SIZE)),
            color=t.attrib.get("fill", None),
        )