from svg import path as svg_path

from ..models.CoordsTranslate import CoordsTranslate
from ..models.Errors import CouldNotParsePathError
from ..models.Rect import Rect


def rect_from_svg_path(coords: CoordsTranslate, path_d: str) -> Rect:
    parsed_path: svg_path.Path = svg_path.parse_path(path_d)
    if len(parsed_path) == 0 or not isinstance(parsed_path[0], svg_path.Move):
        raise CouldNotParsePathError
    start: svg_path.Move = parsed_path.pop(0)
    min_x = start.start.real
    min_y = start.start.imag
    max_x = start.start.real
    max_y = start.start.imag

    # Note that this loop may not be accurate since it does not calculate
    # the Bezier curve based on the control points
    for e in parsed_path:
        min_x = min(min_x, e.start.real, e.end.real)
        min_y = min(min_y, e.start.imag, e.end.imag)
        max_x = max(max_x, e.start.real, e.end.real)
        max_y = max(max_y, e.start.imag, e.end.imag)

    (x, y) = coords.translate(min_x, min_y)

    return Rect(x=x, y=y, width=max_x - min_x, height=max_y - min_y)


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
        min_x = min(p[0], min_x)
        min_y = min(p[1], min_y)
    for p in points:
        test_width = p[0] - min_x
        test_height = p[1] - min_y
        width = max(test_width, width)
        height = max(test_height, height)
    return Rect(x=min_x, y=min_y, width=width, height=height)


def rect_from_image(coords: CoordsTranslate, attrib: dict[str, str]) -> Rect:
    x, y = coords.translate(attrib["x"], attrib["y"])

    return Rect(
        width=float(attrib["width"].strip("px")),
        height=float(attrib["height"].strip("px")),
        x=x,
        y=y,
        image=attrib["{http://www.w3.org/1999/xlink}href"],
    )


def rect_from_ellipse_svg(coords: CoordsTranslate, attrib: dict[str, str]) -> Rect:
    cx = float(attrib["cx"])
    cy = float(attrib["cy"])
    rx = float(attrib["rx"])
    ry = float(attrib["ry"])
    x, y = coords.translate(cx, cy)
    return Rect(x=x - rx, y=y - ry, width=rx * 2, height=ry * 2)
