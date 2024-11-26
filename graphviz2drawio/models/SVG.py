from xml.etree.ElementTree import Element
import xml.etree.ElementTree as ET
import re

NS_SVG = "{http://www.w3.org/2000/svg}"


def parse_svg_path(path_data):
    # Extract all numbers from the path data
    numbers = list(map(float, re.findall(r'-?\d+\.?\d*', path_data)))

    # Separate x and y coordinates
    x_coords = numbers[0::2]  # Every other value starting from index 0
    y_coords = numbers[1::2]  # Every other value starting from index 1
    # Calculate the bounding box
    min_x = min(x_coords)
    max_x = max(x_coords)
    min_y = min(y_coords)
    max_y = max(y_coords)

    width = max_x - min_x
    height = max_y - min_y

    # Single x and y as the center of the bounding box
    single_x = (min_x + max_x) / 2
    single_y = (min_y + max_y) / 2

    return single_x, single_y, width, height

def svg_tag(tag: str) -> str:
    return f"{NS_SVG}{tag}"


def get_first(g: Element, tag: str) -> Element | None:

    return g.find(f"./{NS_SVG}{tag}")


def findall(g: Element, tag: str) -> list[Element]:
    return g.findall(f"./{NS_SVG}{tag}")


def get_title(g: Element) -> str | None:
    if (title_el := get_first(g, "title")) is not None:
        return title_el.text  # pytype: disable=attribute-error
    return None


def get_text(g: Element) -> str | None:
    if (text_el := get_first(g, "text")) is not None:
        return text_el.text
    return None

def get_d(g: Element) -> str | None:
    polygon_str = ET.tostring(g, encoding='unicode')
    # Regular expression to find the <ns0:polygon> tag
    polygon_elements = re.findall(r'<ns0:path[^>]*>', polygon_str)

    # Join the results (in case there are multiple matches)
    polygon_str = ''.join(polygon_elements)
    match = re.search(r'd="([^"]+)"', polygon_str)
    # If a match is found, format it as a dictionary
    if match:
        points = match.group(1)
        x_coords, y_coords, width, height = parse_svg_path(points)
        return x_coords, y_coords, width, height

def is_tag(g: Element, tag: str) -> bool:
    return g.tag == svg_tag(tag)
