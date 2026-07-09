import html
import re
from pathlib import Path
from types import SimpleNamespace
from xml.etree import ElementTree

import pytest
from pygraphviz import AGraph

# pyrefly: ignore  # missing-module-attribute
from graphviz2drawio import graphviz2drawio
from graphviz2drawio.models.Rect import Rect

num_cells_offset = 2


def check_xml_top(root):
    graph = root.findall(".")
    assert len(graph) == 1
    graph = graph[0]
    assert graph.tag == "mxGraphModel"
    return graph.findall("./root/*")


def check_style(e, check) -> None:
    assert check in e.attrib["style"]


def check_value(e, check) -> None:
    value = e.attrib["value"]
    match = re.match(f"<font.*>{check}</font>", html.unescape(value))
    assert match, f"no match found for {value}"


def check_edge(edge, source, target) -> None:
    assert edge.attrib.get("edge")
    assert edge.attrib["source"] == source.attrib["id"]
    assert edge.attrib["target"] == target.attrib["id"]


def cell_map(elements):
    return {element.attrib["id"]: element for element in elements}


def cells_by_plain_label(elements):
    return {
        re.sub(r"<[^>]+>", "", html.unescape(element.attrib.get("value", ""))): element
        for element in elements
        if element.attrib.get("vertex") == "1"
        and element.attrib.get("id", "").startswith("node")
    }


def geometry(cell):
    return cell.find("mxGeometry").attrib


def check_edge_dir(e, dx, dy) -> None:
    style = [e.split("=") for e in e.attrib["style"].split(";")][:-1]
    style = {e[0]: e[1] for e in style if e}
    x2 = float(style["exitX"])
    x1 = float(style["entryX"])
    y2 = float(style["exitY"])
    y1 = float(style["entryY"])

    assert (x2 - x1) == pytest.approx(dx)
    assert (y2 - y1) == pytest.approx(dy)


def test_hello() -> None:
    file = "test/directed/hello.gv.txt"
    xml = graphviz2drawio.convert(file)

    root = ElementTree.fromstring(xml)
    elements = check_xml_top(root)

    hello = elements[2]
    check_style(hello, "ellipse")
    check_value(hello, "Hello")

    world = elements[3]
    check_style(world, "ellipse")
    check_value(world, "World")
    edge = elements[4]
    check_edge(edge, hello, world)


def test_hello_after_reading_content_with_comment() -> None:
    content_with_comment = Path("test/directed/hello.gv.txt").read_text()
    xml = graphviz2drawio.convert(content_with_comment)

    root = ElementTree.fromstring(xml)
    elements = check_xml_top(root)

    hello = elements[2]
    check_style(hello, "ellipse")
    check_value(hello, "Hello")

    world = elements[3]
    check_style(world, "ellipse")
    check_value(world, "World")
    edge = elements[4]
    check_edge(edge, hello, world)


def test_hello_rect() -> None:
    file = "test/directed/hello_rect.gv.txt"
    xml = graphviz2drawio.convert(file)

    root = ElementTree.fromstring(xml)
    elements = check_xml_top(root)

    hello = elements[2]
    check_value(hello, "Hello")
    assert "ellipse" not in hello.attrib["style"]

    world = elements[3]
    check_value(world, "World")
    assert "ellipse" not in world.attrib["style"]


def test_port() -> None:
    file = "test/directed/port.gv.txt"
    xml = graphviz2drawio.convert(file)
    root = ElementTree.fromstring(xml)
    elements = check_xml_top(root)
    check_edge(elements[6], elements[2], elements[3])


def test_polylines() -> None:
    file = "test/undirected/polylines.gv.txt"
    xml = graphviz2drawio.convert(file)

    root = ElementTree.fromstring(xml)
    check_xml_top(root)
    assert "curved" not in xml
    assert "rounded=0" in xml


def test_polylines_curved() -> None:
    file = "test/undirected/polylines_curved.gv.txt"
    xml = graphviz2drawio.convert(file)

    root = ElementTree.fromstring(xml)
    check_xml_top(root)

    assert "curved=1" in xml


def test_cluster() -> None:
    file = "test/directed/cluster.gv.txt"
    xml = graphviz2drawio.convert(file)

    root = ElementTree.fromstring(xml)

    elements = check_xml_top(root)
    cells = cell_map(elements)
    contains_cluster = False
    for el in elements:
        if "process" in el.attrib.get("value", ""):
            contains_cluster = True
    assert contains_cluster
    assert cells["clust1"].attrib["connectable"] == "0"
    assert cells["clust2"].attrib["connectable"] == "0"
    assert cells["node1"].attrib["parent"] == "clust1"
    assert cells["node4"].attrib["parent"] == "clust1"
    assert cells["node5"].attrib["parent"] == "clust2"
    assert cells["node8"].attrib["parent"] == "clust2"
    assert cells["node10"].attrib["parent"] == "1"
    assert cells["edge1"].attrib["parent"] == "1"

    node1_geometry = geometry(cells["node1"])
    clust1_geometry = geometry(cells["clust1"])
    assert 0 <= float(node1_geometry["x"]) < float(clust1_geometry["width"])
    assert 0 <= float(node1_geometry["y"]) < float(clust1_geometry["height"])


def test_cluster_multi_member() -> None:
    # A node referenced by two clusters is only rendered inside one of them by
    # Graphviz; it must be parented to that cluster, not the last one to
    # mention it.
    file = "test/directed/cluster_multi_member.gv.txt"
    xml = graphviz2drawio.convert(file)

    root = ElementTree.fromstring(xml)
    cells = cell_map(check_xml_top(root))

    check_value(cells["node1"], "x")
    assert cells["node1"].attrib["parent"] == "clust1"
    assert cells["node2"].attrib["parent"] == "clust1"
    assert cells["node3"].attrib["parent"] == "clust2"

    x_geometry = geometry(cells["node1"])
    clust1_geometry = geometry(cells["clust1"])
    assert 0 <= float(x_geometry["x"]) < float(clust1_geometry["width"])
    assert 0 <= float(x_geometry["y"]) < float(clust1_geometry["height"])


def test_cluster_special_names() -> None:
    # Node names that need XML escaping still round-trip from DOT membership
    # through the SVG titles into cluster parenting.
    file = "test/directed/cluster_special_names.gv.txt"
    xml = graphviz2drawio.convert(file)

    root = ElementTree.fromstring(xml)
    cells = cell_map(check_xml_top(root))

    check_value(cells["node1"], "a & b")
    check_value(cells["node2"], "c<d>")
    assert cells["node1"].attrib["parent"] == "clust1"
    assert cells["node2"].attrib["parent"] == "clust1"
    assert cells["node3"].attrib["parent"] == "clust1"
    assert cells["node4"].attrib["parent"] == "1"


def test_fdpclust_nested_clusters() -> None:
    file = "test/undirected/fdpclust.gv.txt"
    xml = graphviz2drawio.convert(file)

    root = ElementTree.fromstring(xml)
    elements = check_xml_top(root)
    cells = cell_map(elements)
    labels = cells_by_plain_label(elements)

    inner_parent = labels["C"].attrib["parent"]
    outer_parent = labels["a"].attrib["parent"]
    sibling_parent = labels["d"].attrib["parent"]

    assert inner_parent != "1"
    assert labels["D"].attrib["parent"] == inner_parent
    assert cells[inner_parent].attrib["parent"] == outer_parent
    assert cells[inner_parent].attrib["connectable"] == "0"

    assert outer_parent != "1"
    assert labels["b"].attrib["parent"] == outer_parent
    assert cells[outer_parent].attrib["parent"] == "1"

    assert sibling_parent != "1"
    assert sibling_parent != outer_parent
    assert labels["f"].attrib["parent"] == sibling_parent
    assert cells[sibling_parent].attrib["parent"] == "1"

    assert labels["e"].attrib["parent"] == "1"
    assert labels["clusterB"].attrib["parent"] == "1"
    assert labels["clusterC"].attrib["parent"] == "1"

    inner_geometry = geometry(cells[inner_parent])
    outer_geometry = geometry(cells[outer_parent])
    assert 0 <= float(inner_geometry["x"]) < float(outer_geometry["width"])
    assert 0 <= float(inner_geometry["y"]) < float(outer_geometry["height"])


def test_cluster_membership_skips_cluster_without_rect() -> None:
    graph = AGraph(string="digraph G { subgraph cluster_0 { a } }")
    nodes = {"a": SimpleNamespace(rect=Rect(10, 10, 5, 5))}
    clusters = {"cluster_0": SimpleNamespace(rect=None)}

    node_parents, cluster_parents = graphviz2drawio._cluster_membership(  # noqa: SLF001
        graph,
        nodes,
        clusters,
    )

    assert node_parents == {}
    assert cluster_parents == {}


def test_cluster_membership_uses_rendered_ancestor_for_no_rect_cluster() -> None:
    graph = AGraph(
        string=(
            "digraph G {"
            "  subgraph cluster_parent {"
            "    subgraph cluster_missing {"
            "      subgraph cluster_inner { a }"
            "      b"
            "    }"
            "  }"
            "}"
        ),
    )
    nodes = {
        "a": SimpleNamespace(rect=Rect(25, 25, 5, 5)),
        "b": SimpleNamespace(rect=Rect(50, 50, 5, 5)),
    }
    clusters = {
        "cluster_parent": SimpleNamespace(rect=Rect(0, 0, 100, 100)),
        "cluster_missing": SimpleNamespace(rect=None),
        "cluster_inner": SimpleNamespace(rect=Rect(20, 20, 20, 20)),
    }

    node_parents, cluster_parents = graphviz2drawio._cluster_membership(  # noqa: SLF001
        graph,
        nodes,
        clusters,
    )

    assert node_parents["a"] == "cluster_inner"
    assert node_parents["b"] == "cluster_parent"
    assert cluster_parents == {"cluster_inner": "cluster_parent"}


def test_cells_by_plain_label_collapses_duplicate_labels() -> None:
    """Document a known limitation of the ``cells_by_plain_label`` test helper.

    The helper keys cells by their rendered plain-text label, so two distinct
    node cells that render the same text collapse to a single dict entry
    (last-wins on insertion). Membership assertions built on this helper are
    therefore only reliable for graphs whose visible labels are unique; a graph
    with duplicate labels would silently drop a node and could mask a
    regression. This test pins that behavior so the assumption is explicit.
    """
    model = ElementTree.fromstring(
        """
        <root>
          <mxCell id="node_first" vertex="1" value="&lt;font&gt;dup&lt;/font&gt;" />
          <mxCell id="node_second" vertex="1" value="&lt;font&gt;dup&lt;/font&gt;" />
          <mxCell id="node_unique" vertex="1" value="&lt;font&gt;solo&lt;/font&gt;" />
        </root>
        """,
    )
    elements = list(model)

    labels = cells_by_plain_label(elements)

    # Both "dup" cells are real, distinct vertices...
    assert (
        len(
            {
                e.attrib["id"]
                for e in elements
                if e.attrib["value"].endswith("dup</font>")
            },
        )
        == 2
    )
    # ...but they collapse to one entry, and the last one inserted wins.
    assert set(labels) == {"dup", "solo"}
    assert labels["dup"].attrib["id"] == "node_second"


def test_convnet() -> None:
    file = "test/directed/convnet.gv.txt"
    xml = graphviz2drawio.convert(file)

    root = ElementTree.fromstring(xml)
    elements = check_xml_top(root)

    assert (
        elements[-1].attrib["value"]
        == "<font style='font-size: 14.0px;' face='Times,serif' color='#000000'>$$l_t$$</font>"
    )
    assert "doubleEllipse" in xml
    assert "steelblue1" not in xml


def test_multilabel() -> None:
    file = "test/directed/multilabel.gv.txt"
    xml = graphviz2drawio.convert(file)

    root = ElementTree.fromstring(xml)
    elements = check_xml_top(root)

    assert (
        elements[-1].attrib["value"]
        == "<font style='font-size: 14.0px;' face='Times,serif' color='#000000'>c</font><div><font style='font-size: 14.0px;' face='Times,serif' color='#000000'>b</font></div><div><font style='font-size: 14.0px;' face='Times,serif' color='#000000'>a</font></div>"
    )


def test_datastruct() -> None:
    file = "test/directed/datastruct.gv.txt"
    xml = graphviz2drawio.convert(file)

    root = ElementTree.fromstring(xml)
    elements = check_xml_top(root)

    assert elements[-1].attrib["source"] == "node12"
    assert elements[-1].attrib["target"] == "node2"

    cell_ids = [element.attrib["id"] for element in elements]
    assert len(cell_ids) == len(set(cell_ids))
    assert all(
        not element.attrib["id"].isdecimal()
        for element in elements
        if element.attrib.get("edge") == "1"
    )


def test_compound() -> None:
    file = "test/directed/compound.gv.txt"
    xml = graphviz2drawio.convert(file)

    root = ElementTree.fromstring(xml)
    elements = check_xml_top(root)
    cells = cell_map(elements)
    labels = cells_by_plain_label(elements)

    first_parent = labels["a"].attrib["parent"]
    second_parent = labels["e"].attrib["parent"]

    assert first_parent != "1"
    assert labels["b"].attrib["parent"] == first_parent
    assert labels["c"].attrib["parent"] == first_parent
    assert labels["d"].attrib["parent"] == first_parent
    assert cells[first_parent].attrib["parent"] == "1"
    assert cells[first_parent].attrib["connectable"] == "0"

    assert second_parent != "1"
    assert second_parent != first_parent
    assert labels["f"].attrib["parent"] == second_parent
    assert labels["g"].attrib["parent"] == second_parent
    assert cells[second_parent].attrib["parent"] == "1"
    assert cells[second_parent].attrib["connectable"] == "0"

    assert labels["h"].attrib["parent"] == "1"


def test_subgraph_and_colors():
    file = "test/directed/subgraph_multiple.gv.txt"
    xml = graphviz2drawio.convert(file)

    root = ElementTree.fromstring(xml)
    cells = cell_map(check_xml_top(root))
    assert "fillColor=none" in xml
    assert "strokeColor=black" in xml
    assert "clust1" in xml
    assert "clust2" in xml
    assert cells["node1"].attrib["parent"] == "clust1"
    assert cells["node2"].attrib["parent"] == "clust1"
    assert cells["node3"].attrib["parent"] == "clust2"
    assert cells["node4"].attrib["parent"] == "clust2"


def test_title_with_colon():
    file = "test/directed/bazel.gv.txt"
    xml = graphviz2drawio.convert(file)

    root = ElementTree.fromstring(xml)
    check_xml_top(root)
    assert "//absl/random:random&lt;/font&gt;" in xml


def test_invisible():
    file = "test/directed/invisible.gv.txt"
    xml = graphviz2drawio.convert(file)

    root = ElementTree.fromstring(xml)
    check_xml_top(root)
    assert ';exitX=1.000;exitY=0.584;"' in xml
