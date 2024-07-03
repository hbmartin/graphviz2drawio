import html
import re
import xml.etree.ElementTree as ET

from graphviz2drawio import graphviz2drawio

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
    match = re.match(f"<p.*>{check}</p>", html.unescape(value))
    assert match, f"no match found for {value}"


def check_edge(edge, source, target) -> None:
    assert edge.attrib.get("edge")
    assert edge.attrib["source"] == source.attrib["id"]
    assert edge.attrib["target"] == target.attrib["id"]


def check_edge_dir(e, dx, dy) -> None:
    style = [e.split("=") for e in e.attrib["style"].split(";")][:-1]
    style = {e[0]: e[1] for e in style if e}
    x2 = float(style["exitX"])
    x1 = float(style["entryX"])
    y2 = float(style["exitY"])
    y1 = float(style["entryY"])

    assert (x2 - x1) == dx
    assert (y2 - y1) == dy


def test_hello() -> None:
    file = "test/directed/hello.gv.txt"
    xml = graphviz2drawio.convert(file)

    root = ET.fromstring(xml)
    elements = check_xml_top(root)

    hello = elements[2]
    check_style(hello, "ellipse")
    check_value(hello, "Hello")

    world = elements[3]
    check_style(world, "ellipse")
    check_value(world, "World")
    edge = elements[4]
    check_edge(edge, hello, world)
    check_edge_dir(edge, dx=0, dy=1)


def test_hello_rect() -> None:
    file = "test/directed/hello_rect.gv.txt"
    xml = graphviz2drawio.convert(file)

    root = ET.fromstring(xml)
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
    root = ET.fromstring(xml)
    elements = check_xml_top(root)
    check_edge(elements[6], elements[2], elements[3])


def test_polylines() -> None:
    file = "test/undirected/polylines.gv.txt"
    xml = graphviz2drawio.convert(file)

    root = ET.fromstring(xml)
    check_xml_top(root)


def test_cluster() -> None:
    file = "test/directed/cluster.gv.txt"
    xml = graphviz2drawio.convert(file)

    root = ET.fromstring(xml)

    elements = check_xml_top(root)
    contains_cluster = False
    for el in elements:
        if "process" in el.attrib.get("value", ""):
            contains_cluster = True
    assert contains_cluster


def test_convnet() -> None:
    file = "test/directed/convnet.gv.txt"
    xml = graphviz2drawio.convert(file)

    root = ET.fromstring(xml)
    elements = check_xml_top(root)

    assert elements[-1].attrib["value"] == "$$l_t$$"


def test_multilabel() -> None:
    file = "test/directed/multilabel.gv.txt"
    xml = graphviz2drawio.convert(file)

    root = ET.fromstring(xml)
    elements = check_xml_top(root)

    assert elements[-1].attrib["value"] == "c<div>b</div><div>a</div>"


def test_datastruct() -> None:
    file = "test/directed/datastruct.gv.txt"
    xml = graphviz2drawio.convert(file)

    root = ET.fromstring(xml)
    elements = check_xml_top(root)

    assert elements[-1].attrib["source"] == "node12"
    assert elements[-1].attrib["target"] == "node2"


def test_compound() -> None:
    file = "test/directed/compound.gv.txt"
    xml = graphviz2drawio.convert(file)

    root = ET.fromstring(xml)
    elements = check_xml_top(root)
    assert elements[2].attrib["id"] == "clust1"
    assert elements[3].attrib["id"] == "clust2"


# TODO: https://github.com/hbmartin/graphviz2drawio/issues/33
# def test_subgraph():
#     file = "test/directed/subgraph.gv.txt"
#     xml = graphviz2drawio.convert(file)
#     print(xml)
#
#     root = ET.fromstring(xml)
#     elements = check_xml_top(root


# def test_runAll():
#    for f in os.listdir('undirected'):
#        xml = graphviz2drawio.convert(f)
#        print(xml)
