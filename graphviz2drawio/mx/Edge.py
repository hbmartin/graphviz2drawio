from graphviz2drawio.models import DotAttr
from .GraphObj import GraphObj


class Edge(GraphObj):
    def __init__(self, sid, gid, fr, to, curve, texts):
        super(Edge, self).__init__(sid, gid)
        self.fr = fr
        self.to = to
        self.curve = curve
        self.style = None
        self.dir = None
        self.arrowtail = None
        self.texts = texts

    def curve_start_end(self):
        if self.dir == DotAttr.BACK:
            return self.curve.end, self.curve.start
        else:
            return self.curve.start, self.curve.end
    
    def text_to_mx_value(self):
        value = ""
        last_text = len(self.texts) - 1
        for i, t in enumerate(self.texts):
            style = t.get_mx_style()
            value += f"<p style='{style}'>{t.text}</p>"
            if i != last_text:
                value += "<hr size='1'/>"
        return value
