from xml.etree import ElementTree

from graphviz2drawio.mx.NodeFactory import NodeFactory
from .CoordsTranslate import CoordsTranslate
from graphviz2drawio.mx.Edge import Edge


def parse(svg_data):
    root = ElementTree.fromstring(svg_data)[0]

    coords = CoordsTranslate.from_svg_transform(root.attrib["transform"])
    node_factory = NodeFactory(coords)
    nodes = {}
    edges = []

    for g in root:
        if is_tag(g, "g"):
            title = get_title(g)
            if g.attrib["class"] == "node":
                nodes[title] = node_factory.from_svg(g)
            elif g.attrib["class"] == "edge":
                edges.append(Edge.from_svg(g))

    return nodes, edges


def get_first(g, tag):
    return g.findall("./{http://www.w3.org/2000/svg}" + tag)[0]


def get_title(g):
    return get_first(g, "title").text


def is_tag(g, tag):
    return g.tag == "{http://www.w3.org/2000/svg}" + tag


def has(g, tag):
    return len(g.findall("./{http://www.w3.org/2000/svg}" + tag)) > 0
