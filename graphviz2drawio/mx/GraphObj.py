_whitelist_attrs = ["dir"]


class GraphObj:

    def __init__(self, sid, gid) -> None:
        self.sid = sid
        self.gid = gid

    def enrich_from_graph(self, attrs) -> None:
        for k, v in attrs:
            if (
                k not in _whitelist_attrs
                and k in self.__dict__
                and self.__dict__[k] is not None
            ):
                continue
            self.__setattr__(k, v)
