from ..models.Rect import Rect
from .GraphObj import GraphObj
from .Text import Text


class Node(GraphObj):
    def __init__(
        self,
        sid: str,
        gid: str,
        rect: Rect | None,
        texts: list[Text],
        fill: str | None,
        stroke: str | None,
        shape: str,
        labelloc: str,
    ) -> None:
        super().__init__(sid, gid)
        self.rect = rect
        self.texts = texts
        self.fill = fill
        self.stroke = stroke
        self.label = None
        self.shape = shape
        self.labelloc = labelloc

    def texts_to_mx_value(self) -> str:
        value = ""
        last_text = len(self.texts) - 1
        for i, t in enumerate(self.texts):
            if i != 0:
                value += "<div>" + t.get_mx_value() + "</div>"
            else:
                value += t.get_mx_value()

            if i != last_text:
                value += "<hr size='1'/>"

        return value

    def __repr__(self) -> str:
        return f"Node({self.sid}, {self.gid}, {self.fill}, {self.stroke}, {self.shape})"
