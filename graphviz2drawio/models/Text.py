from graphviz2drawio.gv import GvAttr
from graphviz2drawio.mx import MxConst
from graphviz2drawio.mx.Styles import Styles


class Text:
    def __init__(self, anchor, family, size, text, color):
        self.anchor = anchor
        self.family = family
        self.size = size
        self.text = text
        self.color = color

    def get_mx_style(self):
        align = MxConst.CENTER if self.anchor == GvAttr.MIDDLE else MxConst.START
        # TODO: add right
        margin = (
            "margin-top:4px;" if self.anchor == GvAttr.MIDDLE else "margin-left:4px;"
        )
        rescaled_size = 10.0 * (self.size / 14.0)
        return Styles.TEXT.format(
            align=align,
            margin=margin,
            size=rescaled_size,
            family=self.family or MxConst.DEFAULT_FONT_FAMILY,
            color=self.color or MxConst.DEFAULT_FONT_COLOR,
        )
