from collections import OrderedDict
from xml.etree import ElementTree

from graphviz2drawio.models import DotAttr
from graphviz2drawio.models.Rect import Rect
from graphviz2drawio.mx.Curve import Curve
from graphviz2drawio.mx.Edge import Edge
from graphviz2drawio.mx.MxGraph import MxGraph
from graphviz2drawio.mx.Node import Node


def test_anchor_on_perimeter():
    rect = Rect(0, 0, 10, 10)

    anchor = rect.anchor_fraction_along_line(0 + 5j, -1 + 0j)

    assert anchor == (0, 0.5)


def test_anchor_arrowhead_gap_projects_forward_to_rect():
    rect = Rect(0, 0, 10, 10)

    anchor = rect.anchor_fraction_along_line(-2 + 5j, 1 + 0j)

    assert anchor == (0, 0.5)


def test_anchor_inside_rect_projects_backward_to_nearest_side():
    rect = Rect(0, 0, 10, 10)

    anchor = rect.anchor_fraction_along_line(2 + 5j, 1 + 0j)

    assert anchor == (0, 0.5)


def test_anchor_skips_when_line_misses_rect():
    rect = Rect(0, 0, 10, 10)

    assert rect.anchor_fraction_along_line(-5 - 5j, 1 + 0j) is None


def test_anchor_skips_when_hit_is_too_far():
    rect = Rect(0, 0, 10, 10)

    assert rect.anchor_fraction_along_line(-20 + 5j, 1 + 0j) is None


def test_anchor_skips_zero_direction():
    rect = Rect(0, 0, 10, 10)

    assert rect.anchor_fraction_along_line(0 + 5j, 0j) is None


def test_anchor_clamps_eps_to_edge():
    rect = Rect(0, 0, 10, 10)

    anchor = rect.anchor_fraction_along_line(5 - 1e-7j, 0 + 1j)

    assert anchor == (0.5, 0)


def test_mxgraph_dir_back_uses_swapped_curve_ends_for_anchors():
    edge = _edge(
        Curve(
            start=10 + 5j,
            end=100 + 5j,
            is_bezier=False,
            points=[30 + 5j, 80 + 5j],
        ),
    )
    edge.dir = DotAttr.BACK

    root = _graph_root(edge)
    edge_cell = root.find(".//*[@id='edge1']")
    source_point = root.find(".//*[@as='sourcePoint']")
    target_point = root.find(".//*[@as='targetPoint']")

    assert edge_cell.attrib["source"] == "node_b"
    assert edge_cell.attrib["target"] == "node_a"
    assert "exitX=0.000;exitY=0.500;" in edge_cell.attrib["style"]
    assert "entryX=1.000;entryY=0.500;" in edge_cell.attrib["style"]
    assert source_point.attrib["x"] == "100.0"
    assert target_point.attrib["x"] == "10.0"


def test_mxgraph_reverses_undirected_curve_to_match_source_target_geometry():
    edge = _edge(
        Curve(
            start=100 + 5j,
            end=10 + 5j,
            is_bezier=False,
            points=[80 + 5j, 30 + 5j],
        ),
        is_directed=False,
    )

    root = _graph_root(edge)
    source_point = root.find(".//*[@as='sourcePoint']")
    target_point = root.find(".//*[@as='targetPoint']")
    waypoints = root.findall(".//Array[@as='points']/mxPoint")

    assert source_point.attrib["x"] == "10.0"
    assert target_point.attrib["x"] == "100.0"
    assert [point.attrib["x"] for point in waypoints] == ["30.0", "80.0"]


def test_anchor_and_waypoint_rounding_in_xml():
    edge = _edge(
        Curve(
            start=10.126 + 5.678j,
            end=100.126 + 5.678j,
            is_bezier=False,
            points=[30.1234 + 5.6789j, 80.1234 + 5.6789j],
        ),
    )

    root = _graph_root(edge)
    edge_cell = root.find(".//*[@id='edge1']")
    source_point = root.find(".//*[@as='sourcePoint']")
    waypoint = root.find(".//Array[@as='points']/mxPoint")

    assert "exitY=0.568;" in edge_cell.attrib["style"]
    assert source_point.attrib["x"] == "10.13"
    assert source_point.attrib["y"] == "5.68"
    assert waypoint.attrib["x"] == "30.12"
    assert waypoint.attrib["y"] == "5.68"


def _graph_root(edge: Edge) -> ElementTree.Element:
    graph = MxGraph(
        OrderedDict(),
        OrderedDict(
            [
                ("a", _node("node_a", "a", Rect(0, 0, 10, 10))),
                ("b", _node("node_b", "b", Rect(100, 0, 10, 10))),
            ],
        ),
        [edge],
    )
    return ElementTree.fromstring(graph.value())


def _node(sid: str, gid: str, rect: Rect) -> Node:
    return Node(
        sid=sid,
        gid=gid,
        rect=rect,
        texts=[],
        fill="none",
        stroke="black",
        shape="box",
        labelloc="c",
        stroke_width="1",
        text_offset=None,
        dashed=False,
    )


def _edge(curve: Curve, *, is_directed: bool = True) -> Edge:
    return Edge(
        sid="edge1",
        fr="a",
        to="b",
        is_directed=is_directed,
        curve=curve,
        line_style=None,
        labels=[],
        stroke="black",
        stroke_width="1",
    )
