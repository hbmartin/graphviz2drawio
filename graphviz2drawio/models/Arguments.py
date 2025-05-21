import sys
from argparse import ArgumentParser
from locale import getpreferredencoding
from pathlib import Path
from sys import stdin
from typing import TextIO


class NonOpeningFileType:
    def __call__(self, string: str) -> TextIO | Path:
        # the special argument "-" means sys.std{in,out}
        if string == "-":
            return sys.stdin
        return Path(string)


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
            type=NonOpeningFileType(),
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
            help="Layout program (defaults to dot)",
            default="dot",
        )
        self.add_argument(
            "--encoding",
            "-e",
            type=str,
            default=getpreferredencoding(do_setlocale=False).lower(),
            help="Encoding to use when opening files (default: %(default)s)",
        )
        self.add_argument(
            "--version",
            action="version",
            version=f"%(prog)s {version}",
        )
