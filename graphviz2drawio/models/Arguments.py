from argparse import ArgumentParser


class Arguments(ArgumentParser):
    def __init__(self, version):
        super(Arguments, self).__init__(prog="graphviz2drawio")
        self.add_argument("to_convert", metavar="file.dot", help="graphviz file")
        self.add_argument("outfile", help="output file", nargs="?", default=None)
        self.add_argument(
            "--version",
            action="version",
            version="%(prog)s {version}".format(version=version),
        )
        # TODO: prog
