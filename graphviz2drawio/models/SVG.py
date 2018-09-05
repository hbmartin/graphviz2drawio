def get_first(g, tag):
    return g.findall("./{http://www.w3.org/2000/svg}" + tag)[0]


def get_title(g):
    return get_first(g, "title").text


def is_tag(g, tag):
    return g.tag == "{http://www.w3.org/2000/svg}" + tag


def has(g, tag):
    return len(g.findall("./{http://www.w3.org/2000/svg}" + tag)) > 0
