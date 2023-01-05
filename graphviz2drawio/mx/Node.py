from .GraphObj import GraphObj


class Node(GraphObj):
    def __init__(self, sid, gid, rect, texts, fill, stroke, shape):
        super(Node, self).__init__(sid, gid)
        self.rect = rect
        self.texts = texts
        self.fill = fill
        self.stroke = stroke
        self.label = None
        self.shape = shape

    def text_to_mx_value(self):
        value = ""
        last_text = len(self.texts) - 1
        for i, t in enumerate(self.texts):
            style = t.get_mx_style()
            value += "<p style='" + style + "'>" + t.text + "</p>"
            if i != last_text:
                value += "<hr size='1'/>"
        return value
