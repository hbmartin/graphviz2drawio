from xml.etree.ElementTree import Element

NS_SVG = "{http://www.w3.org/2000/svg}"


def svg_tag(tag):
    return f"{NS_SVG}{tag}"


def get_first(g: Element, tag: str) -> Element | None:
    return g.find(f"./{NS_SVG}{tag}")


def get_title(g: Element) -> str:
    return get_first(g, "title").text


def get_text(g: Element) -> str | None:
    if (text_el := get_first(g, "text")) is not None:
        return text_el.text
    return None


def is_tag(g, tag):
    return g.tag == svg_tag(tag)
