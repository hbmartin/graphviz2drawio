from argparse import ArgumentParser


class Arguments(ArgumentParser):
    def __init__(self, version: str) -> None:
        super().__init__(
            prog="graphviz2drawio",
            description="Please report issues at: https://github.com/hbmartin/graphviz2drawio/issues",
        )
        self.add_argument(
            "to_convert",
            metavar="file.dot",
            help="Path of the graphviz file to convert.",
        )
        self.add_argument(
            "outfile",
            metavar="outfile.xml",
            help="Optional path to output XML. "
            "If more than one file is given, they will be treated as input files.",
            nargs="*",
            default=None,
        )
        self.add_argument(
            "--stdout",
            action="store_true",
            help="Print converted XML to stdout instead of writing a file.",
        )
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
