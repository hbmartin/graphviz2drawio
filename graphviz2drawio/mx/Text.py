from typing import Optional
from xml.etree.ElementTree import Element

from graphviz2drawio.mx import MxConst

from .Styles import Styles


class Text:
    def __init__(
        self,
        text: str,
        family: str,
        size: float,
        color: str | None,
        *,
        bold: bool,
        italic: bool,
    ) -> None:
        self.family = family
        self.size = size
        self.text = text
        self.color = color
        self.bold = bold
        self.italic = italic

    def get_mx_value(self) -> str:
        open_tags = ""
        close_tags = ""
        if self.bold:
            open_tags = "<b>"
            close_tags = "</b>"
        if self.italic:
            open_tags = "<i>" + open_tags
            close_tags += "</i>"
        return Styles.TEXT_VALUE.format(
            text=self.text,
            size=self.size or "14",
            family=self.family or MxConst.DEFAULT_FONT_FAMILY,
            color=self.color or MxConst.DEFAULT_FONT_COLOR,
            open_tags=open_tags,
            close_tags=close_tags,
        )

    @staticmethod
    def from_svg(t: Element) -> Optional["Text"]:
        text = t.text
        if text is None or text.strip() == "":
            return None
        return Text(
            text=text.replace("<", "&lt;").replace(">", "&gt;"),
            family=t.attrib.get("font-family", MxConst.DEFAULT_FONT_FAMILY),
            size=float(t.attrib.get("font-size", MxConst.DEFAULT_TEXT_SIZE)),
            color=t.attrib.get("fill", MxConst.DEFAULT_FONT_COLOR),
            bold=t.get("font-weight", None) == "bold",
            italic=t.get("font-style", None) == "italic",
        )

    def __repr__(self) -> str:
        return self.text
