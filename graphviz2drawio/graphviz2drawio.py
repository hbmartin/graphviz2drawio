#!/usr/bin/env python3

from xml.etree import ElementTree
from pygraphviz import AGraph
from .models import SVG
from .models.CoordsTranslate import CoordsTranslate
from .mx.Edge import Edge
from .mx.MxGraph import MxGraph
from .mx.NodeFactory import NodeFactory


def parse(svg_data):
    root = ElementTree.fromstring(svg_data)[0]

    coords = CoordsTranslate.from_svg_transform(root.attrib["transform"])
    node_factory = NodeFactory(coords)
    nodes = {}
    edges = []

    for g in root:
        if SVG.is_tag(g, "g"):
            title = SVG.get_title(g)
            if g.attrib["class"] == "node":
                nodes[title] = node_factory.from_svg(g)
            elif g.attrib["class"] == "edge":
                edges.append(Edge.from_svg(g))

    return nodes, edges


def convert(graph_to_convert, layout_prog="dot"):
    if isinstance(graph_to_convert, AGraph):
        graph = graph_to_convert
    else:
        try:
            graph = AGraph(graph_to_convert)
        except BaseException as e:
            raise ValueError(
                "graph_to_convert must be one of a string, file, or AGraph object"
            ) from e

    graph_edges = {
        e[0] + "->" + e[1]: list37(e.attr.iteritems())
        for e in list37(graph.edges_iter())
    }
    graph_nodes = {n: list37(n.attr.iteritems()) for n in list37(graph.nodes_iter())}

    svg_graph = graph.draw(prog=layout_prog, format="svg")
    nodes, edges = parse(svg_graph)
    [e.enrich_from_graph(graph_edges[e.gid]) for e in edges]
    [n.enrich_from_graph(graph_nodes[n.gid]) for n in nodes.values()]

    mx_graph = MxGraph(nodes, edges)
    return mx_graph.value()


# Workaround for change in iterator behavior in Python 3.7
# https://www.python.org/dev/peps/pep-0479/
def list37(iterator):
    rv = []
    try:
        for i in iterator:
            rv.append(i)
    except RuntimeError:
        pass
    return rv
