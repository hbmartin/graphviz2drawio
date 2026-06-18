from xml.etree import ElementTree

from graphviz2drawio.models.CoordsTranslate import CoordsTranslate
from graphviz2drawio.mx import Shape
from graphviz2drawio.mx.Node import Node
from graphviz2drawio.mx.NodeFactory import NodeFactory


def _node_from_svg(svg: str) -> Node:
    return NodeFactory(CoordsTranslate(0, 0)).from_svg(
        ElementTree.fromstring(svg),
        labelloc="c",
        gradients={},
    )


def test_url_wrapped_single_ellipse_is_not_double_circle() -> None:
    node = _node_from_svg(
        """
        <g xmlns="http://www.w3.org/2000/svg" id="node1" class="node">
            <title>single</title>
            <a href="https://example.test/single">
                <ellipse fill="none" stroke="black" cx="32.93" cy="-40" rx="32.93" ry="18"/>
            </a>
        </g>
        """,
    )

    assert node.shape == Shape.ELLIPSE


def test_url_wrapped_double_ellipse_is_double_circle() -> None:
    node = _node_from_svg(
        """
        <g xmlns="http://www.w3.org/2000/svg" id="node1" class="node">
            <title>double</title>
            <a href="https://example.test/double">
                <ellipse fill="none" stroke="black" cx="32.93" cy="-40" rx="32.93" ry="18"/>
                <ellipse fill="none" stroke="black" cx="32.93" cy="-40" rx="36.93" ry="22"/>
            </a>
        </g>
        """,
    )

    assert node.shape == Shape.DOUBLE_CIRCLE
