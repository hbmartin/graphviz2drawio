from collections import OrderedDict
from xml.etree.ElementTree import Element, SubElement, indent, tostring

from graphviz2drawio.models import DotAttr, Rect
from graphviz2drawio.mx import MxConst
from graphviz2drawio.mx.Curve import Curve
from graphviz2drawio.mx.Edge import Edge
from graphviz2drawio.mx.Node import Node
from graphviz2drawio.mx.Styles import Styles


class MxGraph:
    def __init__(self, nodes: OrderedDict[str, Node], edges: list[Edge]) -> None:
        self.nodes = nodes
        self.edges = edges
        self.graph = Element(MxConst.GRAPH)
        self.root = SubElement(self.graph, MxConst.ROOT)
        SubElement(self.root, MxConst.CELL, attrib={"id": "0"})
        SubElement(self.root, MxConst.CELL, attrib={"id": "1", "parent": "0"})

        # Add nodes first so edges are drawn on top
        for node in nodes.values():
            self.add_node(node)
        for edge in edges:
            self.add_edge(edge)

    def add_edge(self, edge: Edge) -> None:
        source, target = self.get_edge_source_target(edge)
        style = self.get_edge_style(edge, source.rect, target.rect)
        edge_element = SubElement(
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

        if len(edge.labels) > 0:
            edge_label_element = SubElement(
                self.root,
                MxConst.CELL,
                attrib={
                    "id": f"label_{edge.sid}",
                    "style": Styles.EDGE_LABEL.value,
                    "parent": edge.sid,
                    "value": edge.value_for_labels(),
                    "vertex": "1",
                    "connectable": "0",
                },
            )
            self.add_mx_geo(edge_label_element)

        self.add_mx_geo_with_points(edge_element, edge.curve)

    def get_edge_source_target(self, edge: Edge) -> tuple[Node, Node]:
        if edge.dir == DotAttr.BACK:
            return self.nodes[edge.to], self.nodes[edge.fr]
        return self.nodes[edge.fr], self.nodes[edge.to]

    @staticmethod
    def get_edge_style(
        edge: Edge,  # pytype: disable=invalid-annotation
        source_geo: Rect | None,
        target_geo: Rect | None,
    ) -> str:
        end_arrow = MxConst.BLOCK
        end_fill = 1
        dashed = 1 if edge.line_style == DotAttr.DASHED else 0
        if edge.arrowtail is not None:
            tail = edge.arrowtail
            if edge.arrowtail[0] == DotAttr.NO_FILL:
                end_fill = 0
                tail = edge.arrowtail[1:]
            if tail == DotAttr.DIAMOND:
                end_arrow = MxConst.DIAMOND
        if edge.curve is not None:
            style = Styles.EDGE.format(
                end_arrow=end_arrow,
                dashed=dashed,
                end_fill=end_fill,
            ) + (MxConst.CURVED if edge.curve.is_bezier else MxConst.SHARP)

            if source_geo is not None:
                exit_x, exit_y = source_geo.relative_location_along_perimeter(
                    edge.curve.start,
                )
                style += f"exitX={exit_x};exitY={exit_y};"
            if target_geo is not None:
                entry_x, entry_y = target_geo.relative_location_along_perimeter(
                    edge.curve.end,
                )
                style += f"entryX={entry_x};entryY={entry_y};"

            return style

        return Styles.EDGE.format(
            end_arrow=end_arrow,
            dashed=dashed,
            end_fill=end_fill,
        )

    def add_node(self, node: Node) -> None:
        fill = node.fill if node.fill is not None else MxConst.NONE
        stroke = node.stroke if node.stroke is not None else MxConst.NONE
        style_for_shape = Styles.get_for_shape(node.shape)

        attributes = {"fill": fill, "stroke": stroke}
        if (rect := node.rect) is not None and (image_path := rect.image) is not None:
            from graphviz2drawio.mx.image import image_data_for_path

            attributes["image"] = image_data_for_path(image_path)

        style: str = style_for_shape.format(**attributes)

        node_element = SubElement(
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
            SubElement(element, MxConst.GEO, attrib={"as": "geometry", "relative": "1"})
        else:
            attributes = rect.to_dict_str()
            attributes["as"] = "geometry"
            SubElement(element, MxConst.GEO, attributes)

    @staticmethod
    def add_mx_geo_with_points(element: Element, curve: Curve | None) -> None:
        geo = SubElement(
            element,
            MxConst.GEO,
            attrib={"as": "geometry", "relative": "1"},
        )
        if curve is not None:
            SubElement(
                geo,
                MxConst.POINT,
                attrib={
                    "x": str(curve.start.real),
                    "y": str(curve.start.imag),
                    "as": "sourcePoint",
                },
            )
            SubElement(
                geo,
                MxConst.POINT,
                attrib={
                    "x": str(curve.end.real),
                    "y": str(curve.end.imag),
                    "as": "targetPoint",
                },
            )

            if len(curve.points) != 0:
                array = SubElement(geo, MxConst.ARRAY, {"as": "points"})
                for point in curve.points:
                    SubElement(
                        array,
                        MxConst.POINT,
                        attrib={
                            "x": str(point.real),
                            "y": str(point.imag),
                        },
                    )

    @staticmethod
    def x_y_strs(point: complex) -> tuple[str, str]:
        return str(int(point.real)), str(int(point.imag))

    def value(self) -> str:
        indent(self.graph)
        return tostring(self.graph, encoding="unicode", xml_declaration=True)

    def __str__(self) -> str:
        return self.value()

    def __repr__(self) -> str:
        return self.value()
