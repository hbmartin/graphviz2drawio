from typing import TypeAlias

from ..models.Rect import Rect
from .GraphObj import GraphObj
from .MxConst import VERTICAL_ALIGN
from .Styles import Styles
from .Text import Text

Gradient: TypeAlias = tuple[str, str | None, str]


class Node(GraphObj):
    def __init__(
        self,
        sid: str,
        gid: str,
        rect: Rect | None,
        texts: list[Text],
        fill: str | Gradient,
        stroke: str,
        shape: str,
        labelloc: str,
        stroke_width: str,
        text_offset: complex | None,
        *,
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
        style_for_shape = Styles.get_for_shape(self.shape)
        dashed = 1 if self.dashed else 0
        additional_styling = ""

        attributes = {
            "stroke": self.stroke,
            "stroke_width": self.stroke_width,
            "dashed": dashed,
        }
        if type(self.fill) is str:
            attributes["fill"] = self.fill
        elif type(self.fill) is tuple:
            attributes["fill"] = self.fill[0]
            additional_styling += (
                f"gradientColor={self.fill[1]};gradientDirection={self.fill[2]};"
            )

        if (rect := self.rect) is not None and (image_path := rect.image) is not None:
            from graphviz2drawio.mx.image import image_data_for_path

            attributes["image"] = image_data_for_path(image_path)

        attributes["vertical_align"] = VERTICAL_ALIGN.get(self.labelloc, "middle")

        return style_for_shape.format(**attributes) + additional_styling

    def __repr__(self) -> str:
        return (
            f"Node({self.sid}, {self.gid}, {self.fill}, {self.stroke}, {self.shape}, "
            f"{self.rect})"
        )
