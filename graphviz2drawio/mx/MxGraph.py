from xml.etree import ElementTree as ET

from graphviz2drawio.models import DotAttr
from graphviz2drawio.mx import MxConst
from graphviz2drawio.mx.Styles import Styles


class MxGraph:
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
        self.graph = ET.Element(MxConst.GRAPH)
        self.root = ET.SubElement(self.graph, MxConst.ROOT)
        ET.SubElement(self.root, MxConst.CELL, id="0")
        ET.SubElement(self.root, MxConst.CELL, id="1", parent="0")

        for edge in edges:
            self.add_edge(edge)
        for node in nodes.values():
            self.add_node(node)

    def add_edge(self, edge):
        end_arrow = MxConst.BLOCK
        end_fill = 1
        dashed = 1 if edge.style == DotAttr.DASHED else 0
        if edge.arrowtail is not None:
            tail = edge.arrowtail
            if edge.arrowtail[0] == DotAttr.NO_FILL:
                end_fill = 0
                tail = edge.arrowtail[1:]
            if tail == DotAttr.DIAMOND:
                end_arrow = MxConst.DIAMOND

        if edge.dir == DotAttr.BACK:
            source_node = self.nodes[edge.to]
            target_node = self.nodes[edge.fr]
            start_curve = edge.curve.end
            end_curve = edge.curve.start
        else:
            source_node = self.nodes[edge.fr]
            target_node = self.nodes[edge.to]
            start_curve = edge.curve.start
            end_curve = edge.curve.end

        source = source_node.sid
        target = target_node.sid
        exit_x = source_node.rect.x_ratio(start_curve.real)
        exit_y = source_node.rect.y_ratio(start_curve.imag)
        entry_x = target_node.rect.x_ratio(end_curve.real)
        entry_y = target_node.rect.y_ratio(end_curve.imag)

        style = Styles.EDGE.format(
            entry_x=entry_x,
            entry_y=entry_y,
            exit_x=exit_x,
            exit_y=exit_y,
            end_arrow=end_arrow,
            dashed=dashed,
            end_fill=end_fill,
        )
        if edge.curve.cb is not None:
            style = "edgeStyle=orthogonalEdgeStyle;curved=1;" + style

        edge_element = ET.SubElement(
            self.root,
            MxConst.CELL,
            id=edge.sid,
            style=style,
            parent="1",
            edge="1",
            source=source,
            target=target,
        )
        if edge.curve.cb is None:
            self.add_mx_geo(edge_element)
        else:
            self.add_mx_geo_with_points(edge_element, edge.curve)

    def add_node(self, node):
        fill = (
            node.fill
            if (node.fill is not None and node.fill != "none")
            else MxConst.DEFAULT_FILL
        )
        stroke = node.stroke if node.stroke is not None else MxConst.DEFAULT_STROKE

        style = Styles.get_for_shape(node.shape).format(fill=fill, stroke=stroke)

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
            attributes = rect.to_dict_str()
            attributes["as"] = "geometry"
            ET.SubElement(element, MxConst.GEO, attributes)

    @staticmethod
    def add_mx_geo_with_points(element, curve):
        geo = ET.SubElement(element, MxConst.GEO, {"as": "geometry"}, relative="1")
        # TODO: needs to account for multiple bezier in path
        # array = ET.SubElement(geo, MxConst.ARRAY, {"as": "points"})
        # for i in MxConst.CURVE_INTERVALS:
        #     point = curve.cubic_bezier_coordinates(i)
        #     x, y = MxGraph.x_y_strs(point)
        #     ET.SubElement(array, MxConst.POINT, x=x, y=y)

    @staticmethod
    def x_y_strs(point):
        return str(int(point.real)), str(int(point.imag))

    def value(self):
        return MxConst.DECLARATION + ET.tostring(self.graph, encoding="unicode")
