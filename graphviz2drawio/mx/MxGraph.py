import uuid
from xml.etree import ElementTree as ET

from graphviz2drawio.models import DotAttr
from graphviz2drawio.mx import MxConst
from graphviz2drawio.mx.Styles import Styles


class MxGraph:
    def __init__(self, nodes, edges) -> None:
        self.nodes = nodes
        self.edges = edges
        self.graph = ET.Element(MxConst.GRAPH)
        self.root = ET.SubElement(self.graph, MxConst.ROOT)
        ET.SubElement(self.root, MxConst.CELL, attrib={"id": "0"})
        ET.SubElement(self.root, MxConst.CELL, attrib={"id": "1", "parent": "0"})

        # Add nodes first so edges are drawn on top
        for node in nodes.values():
            self.add_node(node)
        for edge in edges:
            self.add_edge(edge)

    def add_edge(self, edge) -> None:
        source, target = self.get_edge_source_target(edge)
        style = self.get_edge_style(edge, source, target)
        edge_element = ET.SubElement(
            self.root,
            MxConst.CELL,
            attrib={
                "id": edge.sid,
                "style": style,
                "parent": "1",
                "edge": "1",
                "source": source.sid,
                "target": target.sid,
            },
        )

        if edge.label:
            edge_label_element = ET.SubElement(
                self.root,
                MxConst.CELL,
                attrib={
                    "id": uuid.uuid4().hex,
                    "style": "edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];",
                    "parent": edge.sid,
                    "value": edge.label,
                    "vertex": "1",
                    "connectable": "0",
                },
            )
            self.add_mx_geo(edge_label_element)

        if edge.curve.cb is None and len(edge.curve.cbset) == 0:
            self.add_mx_geo(edge_element)
        else:
            self.add_mx_geo_with_points(edge_element, edge.curve)

    def get_edge_source_target(self, edge):
        if edge.dir == DotAttr.BACK:
            return self.nodes[edge.to], self.nodes[edge.fr]
        else:
            return self.nodes[edge.fr], self.nodes[edge.to]

    @staticmethod
    def get_edge_style(edge, source_node, target_node):
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

        start_curve, end_curve = edge.curve_start_end()
        curved = 1 if edge.curve.cb is not None else 0

        return Styles.EDGE.format(
            entry_x=target_node.rect.x_ratio(end_curve.real),
            entry_y=target_node.rect.y_ratio(end_curve.imag),
            exit_x=source_node.rect.x_ratio(start_curve.real),
            exit_y=source_node.rect.y_ratio(start_curve.imag),
            end_arrow=end_arrow,
            dashed=dashed,
            end_fill=end_fill,
            curved=curved,
        )

    def add_node(self, node) -> None:
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
            attrib={
                "id": node.sid,
                "value": node.text_to_mx_value(),
                "style": style,
                "parent": "1",
                "vertex": "1",
            },
        )
        self.add_mx_geo(node_element, node.rect)

    @staticmethod
    def add_mx_geo(element, rect=None) -> None:
        if rect is None:
            ET.SubElement(element, MxConst.GEO, {"as": "geometry"}, relative="1")
        else:
            attributes = rect.to_dict_str()
            attributes["as"] = "geometry"
            ET.SubElement(element, MxConst.GEO, attributes)

    @staticmethod
    def add_mx_geo_with_points(element, curve) -> None:
        geo = ET.SubElement(element, MxConst.GEO, {"as": "geometry"}, relative="1")

        if len(curve.cbset) > 0:
            array = ET.SubElement(geo, MxConst.ARRAY, {"as": "points"})
            for cb in curve.cbset:
                ET.SubElement(array, MxConst.POINT, x=str(cb[0][0]), y=str(cb[0][1]))
                if cb:
                    ET.SubElement(
                        array,
                        MxConst.POINT,
                        x=str(cb[1][0]),
                        y=str(cb[1][1]),
                    )

        # TODO: needs to account for multiple bezier in path
        # array = ET.SubElement(geo, MxConst.ARRAY, {"as": "points"})
        # for i in MxConst.CURVE_INTERVALS:
        #     point = curve.cubic_bezier_coordinates(i)
        #     x, y = MxGraph.x_y_strs(point)
        #     ET.SubElement(array, MxConst.POINT, x=x, y=y)

    @staticmethod
    def x_y_strs(point):
        return str(int(point.real)), str(int(point.imag))

    def value(self) -> str:
        ET.indent(self.graph)
        return ET.tostring(self.graph, encoding="unicode", xml_declaration=True)
