from collections import OrderedDict
from xml.etree import ElementTree
from graphviz2drawio.mx.EdgeFactory import EdgeFactory
from graphviz2drawio.mx.NodeFactory import NodeFactory
from . import SVG
from .CoordsTranslate import CoordsTranslate
from ..mx.Edge import Edge
from ..mx.Node import Node


def parse_nodes_edges_clusters(
    svg_data: bytes,
) -> tuple[dict[str, Node], list[Edge], dict[str, Node]]:
    root = ElementTree.fromstring(svg_data)[0]

    coords: CoordsTranslate = CoordsTranslate.from_svg_transform(root.attrib["transform"])
    node_factory = NodeFactory(coords)
    edge_factory = EdgeFactory(coords)

    nodes: dict[str, Node] = OrderedDict()
    edges: list[Edge] = []
    clusters: dict[str, Node] = OrderedDict()

    for g in root:
        if SVG.is_tag(g, "g"):
            title = SVG.get_title(g)
            if g.attrib["class"] == "node":
                nodes[title] = node_factory.from_svg(g)
            elif g.attrib["class"] == "edge":
                edges.append(edge_factory.from_svg(g))
            elif g.attrib["class"] == "cluster":
                clusters[title] = node_factory.from_svg(g)

    return nodes, edges, clusters
