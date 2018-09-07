from .GraphObj import GraphObj


class Edge(GraphObj):
    def __init__(self, sid, gid, fr, to, curve):
        super(Edge, self).__init__(sid, gid)
        self.fr = fr
        self.to = to
        self.curve = curve
        self.style = None
        self.dir = None
        self.arrowtail = None
