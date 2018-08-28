from graphviz2drawio.models import DotAttr
from graphviz2drawio.mx import MxConst
from .Styles import Styles


class Text:
    def __init__(self, anchor, family, size, text, color):
        self.anchor = anchor
        self.family = family
        self.size = size
        self.text = text
        self.color = color

    def get_mx_style(self):
        align = MxConst.CENTER if self.anchor == DotAttr.MIDDLE else MxConst.START
        margin = (
            "margin-top:4px;" if self.anchor == DotAttr.MIDDLE else "margin-left:4px;"
        )
        rescaled_size = 10 * ((self.size or MxConst.DEFAULT_TEXT_SIZE) / 14)
        return Styles.TEXT.format(
            align=align,
            margin=margin,
            size=rescaled_size,
            family=self.family or MxConst.DEFAULT_FONT_FAMILY,
            color=self.color,
        )

    @staticmethod
    def from_svg(t):
        return Text(
            text=t.text.replace("<", "&lt;").replace(">", "&gt;"),
            anchor=t.attrib["text-anchor"],
            family=t.attrib["font-family"],
            size=float(t.attrib["font-size"]),
            color=t.attrib["fill"],
        )
