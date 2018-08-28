from graphviz2drawio.models import SVG
from graphviz2drawio.models.Rect import Rect
from graphviz2drawio.mx.Shape import Shape
from .Node import Node
from .Text import Text


class NodeFactory:
    def __init__(self, coords):
        self.coords = coords

    def rect_from_svg_points(self, svg):
        points = svg.split(" ")
        assert len(points) == 5
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
        cx = int(attrib["cx"])
        cy = int(attrib["cy"])
        rx = int(attrib["rx"])
        ry = int(attrib["ry"])
        x, y = self.coords.translate(cx, cy)
        return Rect(x=x - rx, y=y - ry, width=rx * 2, height=ry * 2)

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

        if SVG.has(g, "polygon"):
            rect = self.rect_from_svg_points(
                SVG.get_first(g, "polygon").attrib["points"]
            )
            shape = Shape.RECT
        else:
            rect = self.rect_from_ellipse_svg(SVG.get_first(g, "ellipse").attrib)
            shape = Shape.ELLIPSE

        stroke = None
        if "stroke" in g.attrib:
            stroke = g.attrib["stroke"]
        fill = None
        if "fill" in g.attrib:
            fill = g.attrib["fill"]
        return Node(
            sid=g.attrib["id"],
            gid=SVG.get_title(g),
            rect=rect,
            texts=texts,
            fill=fill,
            stroke=stroke,
            shape=shape,
        )
