from xml.etree.ElementTree import Element

def svg_tag(tag):
    return "{http://www.w3.org/2000/svg}" + tag


def get_first(g: Element, tag: str) -> Element:
    target = svg_tag(tag)
    for i in g.iter():
        if i.tag == target:
            return i
    raise RuntimeError(
        f"Failed to find tag ({tag}) in {g}, contains {[i for i in g.iter()]}"
    )


def get_title(g: Element) -> str:
    return get_first(g, "title").text

  
def get_text(g: Element) -> str | None:
    try:
        text_el = get_first(g, "text")
    except IndexError:
        return None
    else:
        return text_el.text


def is_tag(g, tag):
    return g.tag == svg_tag(tag)


def has(g, tag):
    try:
        get_first(g, tag)
    except RuntimeError:
        return False
    else:
        return True
