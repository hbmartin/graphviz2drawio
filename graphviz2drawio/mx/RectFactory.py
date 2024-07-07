from graphviz2drawio.models.CoordsTranslate import CoordsTranslate
from graphviz2drawio.models.Rect import Rect


def rect_from_svg_points(coords: CoordsTranslate, svg: str) -> Rect:
    """Don't use this function.

    It will be replaced by accurately returning the shape of the SVG.
    """
    points: list[tuple[float, float]] = [
        coords.translate(*p.split(",")) for p in svg.split(" ")
    ]
    min_x, min_y = points[0]
    width = 0.0
    height = 0.0
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


def rect_from_image(coords: CoordsTranslate, attrib: dict[str, str]) -> Rect:
    x, y = coords.translate(attrib["x"], attrib["y"])

    return Rect(
        width=float(attrib["width"].strip("px")),
        height=float(attrib["height"].strip("px")),
        x=x,
        y=y,
    )


def rect_from_ellipse_svg(coords: CoordsTranslate, attrib: dict[str, str]) -> Rect:
    cx = float(attrib["cx"])
    cy = float(attrib["cy"])
    rx = float(attrib["rx"])
    ry = float(attrib["ry"])
    x, y = coords.translate(cx, cy)
    return Rect(x=x - rx, y=y - ry, width=rx * 2, height=ry * 2)
