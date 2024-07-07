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

    @property
    def key_for_label(self) -> str:
        return f"{self.gid}-{self.curve}-{self.dir}"

    def __repr__(self) -> str:
        return (
            f"{self.fr}->{self.to}: "
            f"{self.labels}, {self.line_style}, {self.dir}, {self.arrowtail}"
        )

    def value_for_labels(self) -> str:
        text = ""
        for i, label in enumerate(self.labels):
            if i == 0:
                text += label.to_simple_value()
            else:
                text += f"<div>{label.to_simple_value()}</div>"
        return text
