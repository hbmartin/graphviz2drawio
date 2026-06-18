from xml.etree import ElementTree

from graphviz2drawio.models import SVG


def test_findall_only_returns_direct_children() -> None:
    root = ElementTree.fromstring(
        """
        <svg xmlns="http://www.w3.org/2000/svg">
            <text>direct</text>
            <g>
                <text>nested</text>
            </g>
        </svg>
        """,
    )

    text_values = [element.text for element in SVG.findall(root, "text")]

    assert text_values == ["direct"]


def test_findall_recursive_returns_nested_descendants() -> None:
    root = ElementTree.fromstring(
        """
        <svg xmlns="http://www.w3.org/2000/svg">
            <g>
                <a href="https://example.test">
                    <text>wrapped</text>
                </a>
            </g>
        </svg>
        """,
    )

    text_values = [element.text for element in SVG.findall_recursive(root, "text")]

    assert text_values == ["wrapped"]
