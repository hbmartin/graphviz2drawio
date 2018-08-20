from . import SVG
from .GraphObj import GraphObj


class Edge(GraphObj):
    def __init__(self, sid, gid, fr, to):
        super(Edge, self).__init__(sid, gid)
        self.fr = fr
        self.to = to
        self.style = None
        self.dir = None
        self.arrowtail = None

    @staticmethod
    def from_svg(g):
        gid = SVG.get_title(g)
        fr, to = gid.split("->")
        return Edge(sid=g.attrib["id"], gid=gid, fr=fr, to=to)
