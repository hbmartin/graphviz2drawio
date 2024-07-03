from collections import OrderedDict
from xml.etree import ElementTree

from graphviz2drawio.mx.EdgeFactory import EdgeFactory
from graphviz2drawio.mx.NodeFactory import NodeFactory

from ..mx.Edge import Edge
from ..mx.Node import Node
from . import SVG
from .CoordsTranslate import CoordsTranslate


def parse_nodes_edges_clusters(
    svg_data: bytes,
) -> tuple[OrderedDict[str, Node], list[Edge], OrderedDict[str, Node]]:
    root = ElementTree.fromstring(svg_data)[0]

    coords = CoordsTranslate.from_svg_transform(root.attrib["transform"])
    node_factory = NodeFactory(coords)
    edge_factory = EdgeFactory(coords)

    nodes: OrderedDict[str, Node] = OrderedDict()
    edges: OrderedDict[str, Edge] = OrderedDict()
    clusters: OrderedDict[str, Node] = OrderedDict()

    for g in root:
        if SVG.is_tag(g, "g"):
            title = SVG.get_title(g)
            if g.attrib["class"] == "node":
                nodes[title] = node_factory.from_svg(g)
            elif g.attrib["class"] == "edge":
                edge = edge_factory.from_svg(g)
                if existing_edge := edges.get(edge.key_for_label):
                    existing_edge.label += f"<div>{edge.label}</div>"
                else:
                    edges[edge.key_for_label] = edge
            elif g.attrib["class"] == "cluster":
                clusters[title] = node_factory.from_svg(g)

    return nodes, list(edges.values()), clusters
