class Text:
    def __init__(self, anchor, family, size, text):
        self.anchor = anchor
        self.family = family
        self.size = size
        self.text = text

    @staticmethod
    def from_svg(t):
        return Text(
            text=t.text,
            anchor=t.attrib["text-anchor"],
            family=t.attrib["font-family"],
            size=t.attrib["font-size"],
        )
