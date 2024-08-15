import re
from collections import OrderedDict
from collections.abc import Iterable
from math import isclose
from xml.etree import ElementTree

from graphviz2drawio.mx.Edge import Edge
from graphviz2drawio.mx.EdgeFactory import EdgeFactory
from graphviz2drawio.mx.Node import Gradient, Node
from graphviz2drawio.mx.NodeFactory import NodeFactory

from ..mx.Curve import LINE_TOLERANCE
from ..mx.utils import adjust_color_opacity
from . import SVG
from .commented_tree_builder import COMMENT, CommentedTreeBuilder
from .CoordsTranslate import CoordsTranslate
from .Errors import MissingTitleError


def parse_nodes_edges_clusters(
    svg_data: bytes,
    *,
    is_directed: bool,
) -> tuple[OrderedDict[str, Node], list[Edge], OrderedDict[str, Node]]:
    root = ElementTree.fromstring(
        svg_data,
        parser=ElementTree.XMLParser(target=CommentedTreeBuilder()),
    )[0]

    coords = CoordsTranslate.from_svg_transform(root.attrib["transform"])
    node_factory = NodeFactory(coords)
    edge_factory = EdgeFactory(coords=coords, is_directed=is_directed)

    nodes: OrderedDict[str, Node] = OrderedDict()
    edges: OrderedDict[str, Edge] = OrderedDict()
    clusters: OrderedDict[str, Node] = OrderedDict()
    gradients = dict[str, Gradient]()

    prev_comment = None
    for g in root:
        if g.tag == COMMENT:
            prev_comment = g.text
        elif SVG.is_tag(g, "defs"):
            for gradient in _extract_gradients(g):
                gradients[gradient[0]] = gradient[1:]
        elif SVG.is_tag(g, "g"):
            title = prev_comment or SVG.get_title(g)
            if title is None:
                raise MissingTitleError(g)
            if (defs := SVG.get_first(g, "defs")) is not None:
                for gradient in _extract_gradients(defs):
                    gradients[gradient[0]] = gradient[1:]
            if g.attrib["class"] == "node":
                nodes[title] = node_factory.from_svg(
                    g,
                    labelloc="c",
                    gradients=gradients,
                )
            elif g.attrib["class"] == "edge":
                # We need to merge edges with the same source and target
                # GV represents multiple labels with multiple edges
                # even when they are visually along the same edge
                edge = edge_factory.from_svg(g, title)
                if (existing_edge := edges.get(edge.key_for_label)) is not None and len(
                    edge.labels,
                ) > 0:
                    existing_edge.labels.extend(edge.labels)
                else:
                    edges[edge.key_for_label] = edge
            elif g.attrib["class"] == "cluster":
                clusters[title] = node_factory.from_svg(
                    g,
                    labelloc="t",
                    gradients=gradients,
                )

    return nodes, list(edges.values()), clusters


_stop_color_re = re.compile(r"stop-color:([^;]+);")
_stop_opacity_re = re.compile(r"stop-opacity:([^;]+);")


def _extract_stop_color(stop: ElementTree.Element) -> str | None:
    if (color := _stop_color_re.search(stop.attrib["style"])) is not None:
        if (opacity := _stop_opacity_re.search(stop.attrib["style"])) is not None:
            return adjust_color_opacity(color.group(1), float(opacity.group(1)))
        return color.group(1)
    return None


def _extract_gradients(
    defs: ElementTree.Element,
) -> Iterable[tuple[str, str, str, str]]:
    for radial_gradient in SVG.findall(defs, "radialGradient"):
        stops = SVG.findall(radial_gradient, "stop")
        start_color = _extract_stop_color(stops[0])
        end_color = _extract_stop_color(stops[-1])
        if start_color is None or end_color is None:
            continue
        yield (
            radial_gradient.attrib["id"],
            start_color,
            end_color,
            "radial",
        )
    for linear_gradient in SVG.findall(defs, "linearGradient"):
        stops = SVG.findall(linear_gradient, "stop")

        start_color = _extract_stop_color(stops[0])
        end_color = _extract_stop_color(stops[-1])
        if start_color is None or end_color is None:
            continue

        y1 = float(linear_gradient.attrib["y1"])
        y2 = float(linear_gradient.attrib["y2"])

        gradient_direction = "north"
        if isclose(y1, y2, rel_tol=LINE_TOLERANCE):
            x1 = float(linear_gradient.attrib["y1"])
            x2 = float(linear_gradient.attrib["y2"])
            gradient_direction = "east" if x1 < x2 else "west"
        elif y1 < y2:
            gradient_direction = "south"

        yield (
            linear_gradient.attrib["id"],
            start_color,
            end_color,
            gradient_direction,
        )
