from xml.etree import ElementTree
from . import SVG
from .CoordsTranslate import CoordsTranslate
from graphviz2drawio.mx.Edge import Edge
from graphviz2drawio.mx.NodeFactory import NodeFactory


class SvgParser:
    def __init__(self, svg_data):
        super(SvgParser, self).__init__()
        self.svg_data = svg_data

    def get_nodes_and_edges(self):
        root = ElementTree.fromstring(self.svg_data)[0]

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
