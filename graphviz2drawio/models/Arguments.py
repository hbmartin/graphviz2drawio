from argparse import ArgumentParser


class Arguments(ArgumentParser):
    def __init__(self, version: str) -> None:
        super().__init__(prog="graphviz2drawio")
        self.add_argument("to_convert", metavar="file.dot", help="graphviz file")
        output = self.add_mutually_exclusive_group()
        output.add_argument("outfile", help="output file", nargs="?", default=None)
        output.add_argument("--stdout", action="store_true", help="print xml to stdout")
        self.add_argument(
            "--version",
            action="version",
            version=f"%(prog)s {version}",
        )
        self.add_argument(
            "-p",
            "--program",
            help="layout program (defaults to dot)",
            default="dot",
        )
