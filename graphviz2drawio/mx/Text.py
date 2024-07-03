from graphviz2drawio.models import DotAttr
from graphviz2drawio.mx import MxConst

from .Styles import Styles


class Text:
    def __init__(self, anchor, family, size, text, color) -> None:
        self.anchor = anchor
        self.family = family
        self.size = size
        self.text = text
        self.color = color

    def get_mx_style(self):
        align = MxConst.CENTER if self.anchor == DotAttr.MIDDLE else MxConst.START
        # TODO: add right
        margin = (
            "margin-top:4px;" if self.anchor == DotAttr.MIDDLE else "margin-left:4px;"
        )
        rescaled_size = 10.0 * (self.size / 14.0)
        return Styles.TEXT.format(
            align=align,
            margin=margin,
            size=rescaled_size,
            family=self.family or MxConst.DEFAULT_FONT_FAMILY,
            color=self.color or MxConst.DEFAULT_FONT_COLOR,
        )

    @staticmethod
    def from_svg(t):
        return Text(
            text=t.text.replace("<", "&lt;").replace(">", "&gt;"),
            anchor=t.attrib.get("text-anchor", None),
            family=t.attrib.get("font-family", MxConst.DEFAULT_FONT_FAMILY),
            size=float(t.attrib.get("font-size", MxConst.DEFAULT_TEXT_SIZE)),
            color=t.attrib.get("fill", None),
        )
