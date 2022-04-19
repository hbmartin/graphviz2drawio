from graphviz2drawio.models import DotAttr
from .GraphObj import GraphObj


class Edge(GraphObj):
    def __init__(self, sid, gid, fr, to, curve, label):
        super(Edge, self).__init__(sid, gid)
        self.fr = fr
        self.to = to
        self.curve = curve
        self.style = None
        self.dir = None
        self.arrowtail = None
        self.label = label

    def curve_start_end(self):
        if self.dir == DotAttr.BACK:
            return self.curve.end, self.curve.start
        else:
            return self.curve.start, self.curve.end
