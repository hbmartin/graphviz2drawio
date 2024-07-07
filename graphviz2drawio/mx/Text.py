from xml.etree.ElementTree import Element

from graphviz2drawio.models import DotAttr
from graphviz2drawio.mx import MxConst

from ..models.Errors import MissingTitleError
from .Styles import Styles


class Text:
    def __init__(
        self,
        text: str,
        anchor: str | None,
        family: str,
        size: float,
        color: str | None,
        *,
        bold: bool,
        italic: bool,
    ) -> None:
        self.anchor = anchor
        self.family = family
        self.size = size
        self.text = text
        self.color = color
        self.bold = bold
        self.italic = italic

    def get_mx_style(self) -> str:
        align = MxConst.CENTER if self.anchor == DotAttr.MIDDLE else MxConst.START
        margin = (
            "margin-top:4px" if self.anchor == DotAttr.MIDDLE else "margin-left:4px"
        )
        rescaled_size = 10.0 * (self.size / 14.0)
        return Styles.TEXT.format(
            align=align,
            margin=margin,
            size=rescaled_size,
            family=self.family or MxConst.DEFAULT_FONT_FAMILY,
            color=self.color or MxConst.DEFAULT_FONT_COLOR,
        )

    def to_simple_value(self) -> str:
        text = self.text
        if self.bold:
            text = f"<b>{text}</b>"
        if self.italic:
            text = f"<i>{text}</i>"
        return text

    @staticmethod
    def from_svg(t: Element) -> "Text":
        text = t.text
        if text is None:
            raise MissingTitleError(t)
        return Text(
            text=text.replace("<", "&lt;").replace(">", "&gt;"),
            anchor=t.attrib.get("text-anchor", None),
            family=t.attrib.get("font-family", MxConst.DEFAULT_FONT_FAMILY),
            size=float(t.attrib.get("font-size", MxConst.DEFAULT_TEXT_SIZE)),
            color=t.attrib.get("fill", None),
            bold=t.get("font-weight", None) == "bold",
            italic=t.get("font-style", None) == "italic",
        )

    def __repr__(self) -> str:
        return self.text
