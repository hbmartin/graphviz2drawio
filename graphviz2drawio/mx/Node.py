from . import MxConst
from .MxConst import VERTICAL_ALIGN
from .Styles import Styles
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
        stroke_width: str,
        text_offset: complex | None,
        dashed: bool,
    ) -> None:
        super().__init__(sid, gid)
        self.rect = rect
        self.texts = texts
        self.fill = fill
        self.stroke = stroke
        self.label = None
        self.shape = shape
        self.labelloc = labelloc
        self.stroke_width = stroke_width
        self.text_offset = text_offset
        self.dashed = dashed

    def texts_to_mx_value(self) -> str:
        value = ""
        last_text = len(self.texts) - 1
        for i, t in enumerate(self.texts):
            value += f"<div>{t.get_mx_value()}</div>" if i != 0 else t.get_mx_value()
            if i != last_text:
                value += "<hr size='1'/>"

        return value

    def get_node_style(self) -> str:
        fill = self.fill if self.fill is not None else MxConst.NONE
        stroke = self.stroke if self.stroke is not None else MxConst.NONE
        style_for_shape = Styles.get_for_shape(self.shape)
        dashed = 1 if self.dashed else 0

        attributes = {"fill": fill, "stroke": stroke, "stroke_width": self.stroke_width, "dashed": dashed}
        if (rect := self.rect) is not None and (image_path := rect.image) is not None:
            from graphviz2drawio.mx.image import image_data_for_path

            attributes["image"] = image_data_for_path(image_path)

        attributes["vertical_align"] = VERTICAL_ALIGN.get(self.labelloc, "middle")

        return style_for_shape.format(**attributes)

    def __repr__(self) -> str:
        return f"Node({self.sid}, {self.gid}, {self.fill}, {self.stroke}, {self.shape}, {self.rect})"
