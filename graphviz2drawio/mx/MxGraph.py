from xml.etree import ElementTree as ET

from graphviz2drawio.models import DotAttr
from graphviz2drawio.mx import MxConst
from graphviz2drawio.mx.Shape import Shape
from graphviz2drawio.mx.Styles import Styles


class MxGraph:
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        self.graph = ET.Element(MxConst.GRAPH)
        self.root = ET.SubElement(self.graph, MxConst.ROOT)
        ET.SubElement(self.root, MxConst.CELL, id="0")
        ET.SubElement(self.root, MxConst.CELL, id="1", parent="0")

        for node in nodes.values():
            self.add_node(node)
        self.edge_reposition_x = self.edge_reposition(edges)
        for edge in edges:
            self.add_edge(edge)

    def add_edge(self, edge):
        end_arrow = MxConst.NONE
        end_fill = 1
        dashed = 1 if edge.style == DotAttr.DASHED else 0
        if edge.arrowtail is not None:
            end_arrow = MxConst.BLOCK
            tail = edge.arrowtail
            if edge.arrowtail[0] == DotAttr.NO_FILL:
                end_fill = 0
                tail = edge.arrowtail[1:]
            if tail == DotAttr.DIAMOND:
                end_arrow = MxConst.DIAMOND
        if edge.dir == DotAttr.BACK:
            source = self.nodes[edge.to].sid
            target = self.nodes[edge.fr].sid
        else:
            target = self.nodes[edge.to].sid
            source = self.nodes[edge.fr].sid
        edge_element = ET.SubElement(
            self.root,
            MxConst.CELL,
            id=edge.sid,
            style=Styles.EDGE.format(
                entry_x=self.edge_reposition_x[edge.sid],
                end_arrow=end_arrow,
                dashed=dashed,
                end_fill=end_fill,
            ),
            parent="1",
            edge="1",
            source=source,
            target=target,
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
        fill = (
            node.fill
            if (node.fill is not None and node.fill != "none")
            else MxConst.DEFAUT_FILL
        )
        stroke = node.stroke if node.stroke is not None else MxConst.DEFAUT_STROKE
        style = Styles.NODE.format(fill=fill, stroke=stroke)
        if node.shape == Shape.ELLIPSE:
            style = Shape.ELLIPSE.value + ";" + style
        node_element = ET.SubElement(
            self.root,
            MxConst.CELL,
            id=node.sid,
            value=node.text_to_mx_value(),
            style=style,
            parent="1",
            vertex="1",
        )
        self.add_mx_geo(node_element, node.rect)

    @staticmethod
    def add_mx_geo(element, rect=None):
        if rect is None:
            ET.SubElement(element, MxConst.GEO, {"as": "geometry"}, relative="1")
        else:
            attributes = rect.to_dict_int()
            attributes["as"] = "geometry"
            ET.SubElement(element, MxConst.GEO, attributes)

    def value(self):
        return MxConst.DECLARATION + ET.tostring(self.graph, encoding="unicode")
