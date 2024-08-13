_blacklist_attrs = ["fill"]


class GraphObj:

    def __init__(self, sid: str, gid: str) -> None:
        self.sid = sid
        self.gid = gid

    def enrich_from_graph(self, attrs: dict) -> None:
        for k, v in attrs.items():
            if v == "" and k in self.__dict__ and self.__dict__[k] is not None:
                continue
            if k in _blacklist_attrs:
                continue
            self.__setattr__(k, v)
