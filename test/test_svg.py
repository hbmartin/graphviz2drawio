from xml.etree import ElementTree

from graphviz2drawio.models import SVG
from graphviz2drawio.models.commented_tree_builder import COMMENT, CommentedTreeBuilder


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


def test_commented_tree_builder_returns_preserved_comment_element() -> None:
    builder = CommentedTreeBuilder()

    builder.start("svg", {})
    comment = builder.comment("  title  ")
    builder.end("svg")
    root = builder.close()

    assert comment is not None
    assert comment.tag == COMMENT
    assert comment.text == "title"
    assert list(root) == [comment]
