from collections import OrderedDict
from collections.abc import Iterable
from xml.etree.ElementTree import Element, SubElement, indent, tostring

from ..models import DotAttr
from ..models.Rect import Rect
from . import MxConst
from .Curve import Curve
from .Edge import Edge
from .Node import Node
from .Styles import Styles


class MxGraph:
    def __init__(
        self,
        clusters: OrderedDict[str, Node],
        nodes: OrderedDict[str, Node],
        edges: list[Edge],
        *,
        node_parents: dict[str, str] | None = None,
        cluster_parents: dict[str, str] | None = None,
    ) -> None:
        self.nodes = nodes
        self.edges = edges
        self.node_parents = node_parents or {}
        self.cluster_parents = cluster_parents or {}
        self.clusters_by_gid = {cluster.gid: cluster for cluster in clusters.values()}
        self.graph = Element(MxConst.GRAPH, attrib={"grid": "0"})
        self.root = SubElement(self.graph, MxConst.ROOT)
        SubElement(self.root, MxConst.CELL, attrib={"id": "0"})
        SubElement(self.root, MxConst.CELL, attrib={"id": "1", "parent": "0"})

        # Add nodes first so edges are drawn on top
        for cluster in self._clusters_parent_first(clusters.values()):
            parent = self._parent_cluster_for_cluster(cluster)
            self.add_node(
                cluster,
                parent_id=parent.sid if parent is not None else "1",
                parent_rect=parent.rect if parent is not None else None,
                connectable=False,
            )
        for node in nodes.values():
            parent = self._parent_cluster_for_node(node)
            self.add_node(
                node,
                parent_id=parent.sid if parent is not None else "1",
                parent_rect=parent.rect if parent is not None else None,
            )
        for edge in edges:
            self.add_edge(edge)

    def add_edge(self, edge: Edge) -> None:
        source, target = self.get_edge_source_target(edge)
        reverse_curve = self._should_reverse_curve(edge, source, target)
        exit_xy, entry_xy = self._edge_anchors(
            edge,
            source,
            target,
            reverse_curve=reverse_curve,
        )
        style = edge.get_edge_style(
            exit_xy=exit_xy,
            entry_xy=entry_xy,
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

        self.add_mx_geo_with_points(edge_element, edge.curve, reverse=reverse_curve)

    def get_edge_source_target(self, edge: Edge) -> tuple[Node | None, Node | None]:
        if edge.dir == DotAttr.BACK:
            return self.nodes.get(edge.to), self.nodes.get(edge.fr)
        return self.nodes.get(edge.fr), self.nodes.get(edge.to)

    @staticmethod
    def _edge_anchors(
        edge: Edge,
        source: Node | None,
        target: Node | None,
        *,
        reverse_curve: bool,
    ) -> tuple[tuple[float, float] | None, tuple[float, float] | None]:
        if edge.curve is None:
            return None, None

        curve = edge.curve
        if reverse_curve:
            source_terminal = curve.end
            source_interior = curve.last_interior_point()
            target_terminal = curve.start
            target_interior = curve.first_interior_point()
        else:
            source_terminal = curve.start
            source_interior = curve.first_interior_point()
            target_terminal = curve.end
            target_interior = curve.last_interior_point()

        exit_xy = (
            source.rect.anchor_fraction_along_line(
                source_terminal,
                source_terminal - source_interior,
            )
            if source is not None and source.rect is not None
            else None
        )
        entry_xy = (
            target.rect.anchor_fraction_along_line(
                target_terminal,
                target_terminal - target_interior,
            )
            if target is not None and target.rect is not None
            else None
        )
        return exit_xy, entry_xy

    @staticmethod
    def _should_reverse_curve(
        edge: Edge,
        source: Node | None,
        target: Node | None,
    ) -> bool:
        """Decide whether the curve runs end->start relative to source/target.

        Broader than a plain ``dir == BACK`` swap: the curve's geometry is
        scored against both node assignments so that edges whose stored
        start/end happen to be oriented opposite to the drawio source/target
        get their terminals (and waypoints) reversed. ``dir == BACK`` is only
        the tiebreaker when the geometry is ambiguous (e.g. self-loops).
        """
        if edge.curve is None:
            return False

        normal_score = _orientation_score(
            edge.curve.start,
            source,
        ) + _orientation_score(edge.curve.end, target)
        reverse_score = _orientation_score(
            edge.curve.end,
            source,
        ) + _orientation_score(edge.curve.start, target)
        if normal_score != reverse_score:
            return reverse_score < normal_score
        return edge.dir == DotAttr.BACK

    def add_node(
        self,
        node: Node,
        *,
        parent_id: str = "1",
        parent_rect: Rect | None = None,
        connectable: bool = True,
    ) -> None:
        attrib = {
            "id": node.sid,
            "value": node.texts_to_mx_value(),
            "style": node.get_node_style(),
            "parent": parent_id,
            "vertex": "1",
        }
        if not connectable:
            attrib["connectable"] = "0"
        node_element = SubElement(
            self.root,
            MxConst.CELL,
            attrib=attrib,
        )
        self.add_mx_geo(
            node_element,
            self._relative_rect(node.rect, parent_rect),
            self._relative_text_offset(node.text_offset, parent_rect),
        )

    def _clusters_parent_first(self, clusters: Iterable[Node]) -> list[Node]:
        ordered: list[Node] = []
        emitted: set[str] = set()

        def emit(cluster: Node) -> None:
            if cluster.gid in emitted:
                return
            parent = self._parent_cluster_for_cluster(cluster)
            if parent is not None:
                emit(parent)
            ordered.append(cluster)
            emitted.add(cluster.gid)

        for cluster in clusters:
            emit(cluster)
        return ordered

    def _parent_cluster_for_cluster(self, cluster: Node) -> Node | None:
        return self.clusters_by_gid.get(self.cluster_parents.get(cluster.gid, ""))

    def _parent_cluster_for_node(self, node: Node) -> Node | None:
        return self.clusters_by_gid.get(self.node_parents.get(node.gid, ""))

    @staticmethod
    def _relative_rect(rect: Rect | None, parent_rect: Rect | None) -> Rect | None:
        if rect is None or parent_rect is None:
            return rect
        return Rect(
            x=rect.x - parent_rect.x,
            y=rect.y - parent_rect.y,
            width=rect.width,
            height=rect.height,
            image=rect.image,
        )

    @staticmethod
    def _relative_text_offset(
        text_offset: complex | None,
        parent_rect: Rect | None,
    ) -> complex | None:
        if text_offset is None or parent_rect is None:
            return text_offset
        return text_offset - complex(parent_rect.x, parent_rect.y)

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
            geo = SubElement(
                element,
                MxConst.GEO,
                attrib={"as": "geometry", "relative": "1"},
            )
            SubElement(
                geo,
                MxConst.POINT,
                attrib={
                    "x": str(text_offset.real),
                    "y": str(text_offset.imag),
                    "as": "offset",
                },
            )
        else:
            SubElement(element, MxConst.GEO, attrib={"as": "geometry", "relative": "1"})

    @staticmethod
    def add_mx_geo_with_points(
        element: Element,
        curve: Curve | None,
        *,
        reverse: bool = False,
    ) -> None:
        geo = SubElement(
            element,
            MxConst.GEO,
            attrib={"as": "geometry", "relative": "1"},
        )
        if curve is not None:
            start = curve.end if reverse else curve.start
            end = curve.start if reverse else curve.end
            points = list(reversed(curve.points)) if reverse else curve.points
            SubElement(
                geo,
                MxConst.POINT,
                attrib={
                    "x": _round_coord(start.real),
                    "y": _round_coord(start.imag),
                    "as": "sourcePoint",
                },
            )
            SubElement(
                geo,
                MxConst.POINT,
                attrib={
                    "x": _round_coord(end.real),
                    "y": _round_coord(end.imag),
                    "as": "targetPoint",
                },
            )

            if len(points) != 0:
                array = SubElement(geo, MxConst.ARRAY, {"as": "points"})
                for point in points:
                    SubElement(
                        array,
                        MxConst.POINT,
                        attrib={
                            "x": _round_coord(point.real),
                            "y": _round_coord(point.imag),
                        },
                    )

    def value(self) -> str:
        indent(self.graph)
        return tostring(self.graph, encoding="unicode", xml_declaration=True)

    def __str__(self) -> str:
        return self.value()

    def __repr__(self) -> str:
        return self.value()


def _round_coord(value: float) -> str:
    rounded = round(value, 2)
    if rounded == 0:
        rounded = 0.0
    return str(rounded)


def _orientation_score(point: complex, node: Node | None) -> float:
    if node is None or node.rect is None:
        return 0
    rect = node.rect
    if rect.x <= point.real <= rect.right and rect.y <= point.imag <= rect.bottom:
        return 0
    dx = max(rect.x - point.real, 0, point.real - rect.right)
    dy = max(rect.y - point.imag, 0, point.imag - rect.bottom)
    return (dx * dx) + (dy * dy)
