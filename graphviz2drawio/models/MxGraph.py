from xml.etree import ElementTree as ET

from graphviz2drawio.models.Stroke import Stroke
from graphviz2drawio.models.Styles import Styles


class MxGraph:
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        self.graph = ET.Element("mxGraphModel")
        self.root = ET.SubElement(self.graph, "root")
        ET.SubElement(self.root, "mxCell", id="0")
        ET.SubElement(self.root, "mxCell", id="1", parent="0")

        for node in nodes.values():
            self.add_node(node)
        self.edge_reposition_x = self.edge_reposition(edges)
        for edge in edges:
            self.add_edge(edge)

    def add_edge(self, edge):
        end_arrow = "block"
        end_fill = 1
        dashed = 1 if edge.style == Stroke.DASHED.value else 0
        if edge.arrowtail is not None:
            tail = edge.arrowtail
            if edge.arrowtail[0] == "o":
                end_fill = 0
                tail = edge.arrowtail[1:]
            if tail == "diamond":
                end_arrow = "diamond"
        edge_element = ET.SubElement(
            self.root,
            "mxCell",
            id=edge.sid,
            style=Styles.EDGE.format(
                entry_x=self.edge_reposition_x[edge.sid],
                end_arrow=end_arrow,
                dashed=dashed,
                end_fill=end_fill,
            ),
            parent="1",
            edge="1",
            source=self.nodes[edge.fr].sid,
            target=self.nodes[edge.to].sid,
        )
        self.add_mx_geo(edge_element)

    def edge_reposition(self, edges):
        # TODO: this needs to be smarter
        edge_to = {}
        for edge in edges:
            if edge.to not in edge_to:
                edge_to[edge.to] = []
            edge_to[edge.to].append(edge.sid)
        reposition_x = {}
        for edge in edges:
            x_ratio = 0.5
            if len(edge_to[edge.to]) > 1:
                to_x = self.nodes[edge.to].rect.x
                fr_x = self.nodes[edge.fr].rect.x
                if to_x > fr_x:
                    ratio = (to_x - fr_x) / to_x
                    x_ratio = ratio * 0.5
                else:
                    ratio = (fr_x - to_x) / fr_x
                    x_ratio = (ratio * 0.5) + 0.5
            reposition_x[edge.sid] = x_ratio
        return reposition_x

    def add_node(self, node):
        value = ""
        last_text = len(node.texts) - 1
        for i, t in enumerate(node.texts):
            align = "center" if t.anchor == "middle" else "start"
            margin = "margin-top:4px;" if t.anchor == "middle" else "margin-left:4px;"
            value += (
                "<p style='margin:0px;text-align:"
                + align
                + ";"
                + margin
                + "'>"
                + t.text
                + "</p>"
            )
            if i != last_text:
                value += "<hr size='1'/>"
        node_element = ET.SubElement(
            self.root,
            "mxCell",
            id=node.sid,
            value=value,
            style=Styles.NODE.value,
            parent="1",
            vertex="1",
        )
        self.add_mx_geo(node_element, node.rect)

    @staticmethod
    def add_mx_geo(element, rect=None):
        if rect is None:
            ET.SubElement(element, "mxGeometry", {"as": "geometry"}, relative="1")
        else:
            attributes = rect.to_dict_int()
            attributes["as"] = "geometry"
            ET.SubElement(element, "mxGeometry", attributes)

    def value(self):
        declaration = '<?xml version="1.0"?>'
        return declaration + ET.tostring(self.graph, encoding="unicode")
