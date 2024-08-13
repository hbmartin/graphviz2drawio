from argparse import ArgumentParser, FileType
from sys import stdin


class Arguments(ArgumentParser):
    def __init__(self, version: str) -> None:
        super().__init__(
            prog="graphviz2drawio",
            description="Please report problems at: https://github.com/hbmartin/graphviz2drawio/issues",
        )
        self.add_argument(
            "to_convert",
            metavar="file(s).dot",
            help="Path of the graphviz file(s) to convert (or stdin).",
            nargs="*",
            type=FileType("r"),
            default=[stdin],
        )
        self.add_argument(
            "-o",
            "--outfile",
            metavar="file.xml",
            help="Optional path to output XML. "
            "May not be used with multiple input files.",
            nargs="?",
            default=None,
        )
        self.add_argument(
            "--stdout",
            action="store_true",
            help="Print converted output to stdout instead of writing an XML file. "
            "May not be used with multiple input files.",
        )
        self.add_argument(
            "-p",
            "--program",
            help="layout program (defaults to dot)",
            default="dot",
        )
        self.add_argument(
            "--version",
            action="version",
            version=f"%(prog)s {version}",
        )
