from .GraphObj import GraphObj


class Node(GraphObj):
    def __init__(self, sid, gid, rect, texts):
        super(Node, self).__init__(sid, gid)
        self.rect = rect
        self.texts = texts
        self.label = None
        self.shape = None
