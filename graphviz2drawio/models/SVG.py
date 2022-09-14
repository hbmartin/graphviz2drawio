def svg_tag(tag):
    return "{http://www.w3.org/2000/svg}" + tag


def get_first(g, tag):
    target = svg_tag(tag)
    for i in g.iter():
        if i.tag == target:
            return i
    raise RuntimeError(
        f"Failed to find tag ({tag}) in {g}, contains {list(g.iter())}"
    )


def get_title(g):
    return get_first(g, "title").text


def is_tag(g, tag):
    return g.tag == svg_tag(tag)


def has(g, tag):
    try:
        get_first(g, tag)
    except RuntimeError:
        return False
    else:
        return True
