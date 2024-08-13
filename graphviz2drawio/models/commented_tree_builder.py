from html import unescape
from xml.etree import ElementTree

COMMENT = "comment"


class CommentedTreeBuilder(ElementTree.TreeBuilder):
    """A TreeBuilder that preserves comments.

    Port forwarding or other stylistic information may be included
    in the <g> tag's <title>, so we prefer to use the preceding
    comment to determine the node's/edge's title instead.
    See `prev_comment` usage in SvgParser.
    """

    def __init__(self):
        super().__init__()
        self.was_root_set = False

    def start(self, tag, attrs):
        super().start(tag, attrs)
        self.was_root_set = True

    def comment(self, data):
        if not self.was_root_set:
            return
        self.start(COMMENT, {})
        self.data(unescape(data.strip()))
        self.end(COMMENT)
