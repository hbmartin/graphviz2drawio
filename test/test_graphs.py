import pytest
from graphviz2drawio import graphviz2drawio
import xml.etree.ElementTree as ET
import re
import html

num_cells_offset = 2


def check_xml_top(root):
    graph = root.findall('.')
    assert len(graph) == 1
    graph = graph[0]
    assert graph.tag == 'mxGraphModel'
    return graph.findall('./root/*')

def check_style(e, check):
    assert check in e.attrib['style']

def check_value(e, check):
    value = e.attrib['value']
    match = re.match(r'<p.*>%s</p>' % check, html.unescape(value))
    assert match, 'no match found for %s' % value

def check_edge(e, source, target):
    assert e.attrib.get('edge')
    assert e.attrib['source'] == source.attrib['id']
    assert e.attrib['target'] == target.attrib['id']


def test_hello():
    file = './directed/hello.gv.txt'
    xml = graphviz2drawio.convert(file)
    print(xml)

    root = ET.fromstring(xml)
    elements = check_xml_top(root)

    hello = elements[2]
    check_style(hello, 'ellipse')
    check_value(hello, 'Hello')

    world = elements[3]
    check_style(world, 'ellipse')
    check_value(world, 'World')
    edge = elements[4]
    check_edge(edge, hello, world)
