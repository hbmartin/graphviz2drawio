from xml.etree.ElementTree import Element


def get_first(g: Element, tag: str) -> Element:
    return g.findall("./{http://www.w3.org/2000/svg}" + tag)[0]


def get_title(g: Element) -> str:
    return get_first(g, "title").text


def get_text(g: Element) -> str | None:
    try:
        text_el = get_first(g, "text")
        return text_el.text
    except IndexError:
        return None


def is_tag(g: Element, tag: str) -> bool:
    return g.tag == "{http://www.w3.org/2000/svg}" + tag


def has(g: Element, tag: str) -> bool:
    return len(g.findall("./{http://www.w3.org/2000/svg}" + tag)) > 0
