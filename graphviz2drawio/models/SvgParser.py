from collections import OrderedDict
from xml.etree import ElementTree

from graphviz2drawio.mx.Edge import Edge
from graphviz2drawio.mx.EdgeFactory import EdgeFactory
from graphviz2drawio.mx.Node import Node
from graphviz2drawio.mx.NodeFactory import NodeFactory

from . import SVG
from .CoordsTranslate import CoordsTranslate
from .Errors import MissingTitleError


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
            if title is None:
                raise MissingTitleError(g)
            if g.attrib["class"] == "node":
                nodes[title] = node_factory.from_svg(g)
            elif g.attrib["class"] == "edge":
                # We need to merge edges with the same source and target
                # GV represents multiple labels with multiple edges
                # even when they are visually along the same edge
                edge = edge_factory.from_svg(g)
                if (existing_edge := edges.get(edge.key_for_label)) is not None:
                    existing_edge.label += f"<div>{edge.label}</div>"
                else:
                    edges[edge.key_for_label] = edge
            elif g.attrib["class"] == "cluster":
                clusters[title] = node_factory.from_svg(g)

    return nodes, list(edges.values()), clusters
