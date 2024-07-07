from graphviz2drawio.models import DotAttr

from .Curve import Curve
from .GraphObj import GraphObj
from .Text import Text


class Edge(GraphObj):
    """An edge connecting two nodes in the graph."""

    def __init__(
        self,
        sid: str,
        fr: str,
        to: str,
        curve: Curve | None,
        labels: list[Text],
    ) -> None:
        super().__init__(sid=sid, gid=f"{fr}->{to}")
        self.fr = fr
        self.to = to
        self.curve = curve
        self.line_style = None
        self.dir = None
        self.arrowtail = None
        self.labels = labels

    def curve_start_end(self):
        if self.dir == DotAttr.BACK:
            return self.curve.end, self.curve.start
        return self.curve.start, self.curve.end

    def text_to_mx_value(self):
        value = ""
        last_text = len(self.labels) - 1
        for i, t in enumerate(self.labels):
            style = t.get_mx_style()
            value += "<p style='" + style + "'>" + t.text + "</p>"
            if i != last_text:
                value += "<hr size='1'/>"
        return value

    @property
    def key_for_label(self) -> str:
        return f"{self.gid}-{self.curve}"

    def __repr__(self) -> str:
        return (
            f"{self.fr}->{self.to}: "
            f"{self.labels}, {self.line_style}, {self.dir}, {self.arrowtail}"
        )
