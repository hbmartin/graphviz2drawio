from collections import OrderedDict
from xml.etree.ElementTree import Element, SubElement, indent, tostring

from graphviz2drawio.models import DotAttr
from graphviz2drawio.models.Rect import Rect
from graphviz2drawio.mx import MxConst
from graphviz2drawio.mx.Curve import Curve
from graphviz2drawio.mx.Edge import Edge
from graphviz2drawio.mx.Node import Node
from graphviz2drawio.mx.Styles import Styles
from graphviz2drawio.models import SVG


class MxGraph:
    def __init__(
        self,
        clusters: OrderedDict[str, Node],
        nodes: OrderedDict[str, Node],
        edges: list[Edge],
        
    ) -> None:
        self.nodes = nodes
        self.edges = edges
        self.graph = Element(MxConst.GRAPH, attrib={"grid": "0"})
        self.root = SubElement(self.graph, MxConst.ROOT)
        SubElement(self.root, MxConst.CELL, attrib={"id": "0"})
        SubElement(self.root, MxConst.CELL, attrib={"id": "1", "parent": "0"})
        # Add nodes first so edges are drawn on top
        for cluster in clusters.values():
            self.add_node(cluster)
        for node in nodes.values():
            self.add_node(node)
        for edge in edges:
            self.add_edge(edge)

    def add_edge(self, edge: Edge) -> None:
        source, target = self.get_edge_source_target(edge)
        style = edge.get_edge_style(
            source_geo=source.rect if source is not None else None,
            target_geo=target.rect if target is not None else None,
        )

        attrib = {
            "id": edge.sid,
            "style": style,
            "parent": "1",
            "edge": "1",
        }
        if source is not None:
            attrib["source"] = source.sid
        if target is not None:
            attrib["target"] = target.sid

        edge_element = SubElement(
            self.root,
            MxConst.CELL,
            attrib=attrib,
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

    def get_edge_source_target(self, edge: Edge) -> tuple[Node | None, Node | None]:
        if edge.dir == DotAttr.BACK:
            return self.nodes.get(edge.to), self.nodes.get(edge.fr)
        return self.nodes.get(edge.fr), self.nodes.get(edge.to)

    def add_node(self, node: Node) -> None:
        node_element = SubElement(
            self.root,
            MxConst.CELL,
            attrib={
                "id": node.sid,
                "value": node.texts_to_mx_value(),
                "style": node.get_node_style(),
                "parent": "1",
                "vertex": "1",
            },
        )
        self.add_mx_geo(node_element, node.rect, node.text_offset)

    @staticmethod
    def add_mx_geo(
        element: Element,
        rect: Rect | None = None,
        text_offset: complex | None = None,
    ) -> None:
        if rect is not None:
            attributes = rect.to_dict_str()
            attributes["as"] = "geometry"
            SubElement(element, MxConst.GEO, attributes)
        elif text_offset is not None:
            # Calculate width and height based on text_offset
            width = abs(text_offset.real) * 0.25  # Example calculation
            height = abs(text_offset.imag) * 0.25  # Example calculation
            x = str(text_offset.real / 2) 
            y = str(text_offset.imag / 2)
            geo = SubElement(
                element,
                MxConst.GEO,
                attrib={
                    "relative": "1",
                    "x": x,
                    "y": y,
                    "width": str(width),
                    "height": str(height),
                    "as": "geometry"
                },
            )
        else:
            SubElement(element, MxConst.GEO, attrib={"as": "geometry", "relative": "1"})

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

    def value(self) -> str:
        indent(self.graph)
        return tostring(self.graph, encoding="unicode", xml_declaration=True)

    def __str__(self) -> str:
        return self.value()

    def __repr__(self) -> str:
        return self.value()