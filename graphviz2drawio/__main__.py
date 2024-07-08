import pathlib
import sys
from sys import stderr

from .graphviz2drawio import convert
from .models import Arguments
from .version import __version__

DEFAULT_TEXT = "\033[0m"
RED_TEXT = "\033[91m"
BOLD = "\033[1m"


def _gv_filename_to_xml(filename: str) -> str:
    return ".".join(filename.split(".")[:-1]) + ".xml"


def _convert_file(to_convert: str, program: str, outfile: str | None) -> None:
    try:
        output = convert(to_convert, program)
    except BaseException:
        stderr.write(f"{RED_TEXT}{BOLD}Error converting {to_convert}\n")
        stderr.write("https://github.com/hbmartin/graphviz2drawio/issues\n")
        stderr.write("Please include an example of your diagram and the following:\n\n")
        stderr.write(DEFAULT_TEXT)
        stderr.write(f"Python: {sys.version}, g2d: {__version__}\n")
        raise

    if outfile is None:
        print(output)
        return

    pathlib.Path(outfile).write_text(output)
    stderr.write("Converted file: " + outfile + "\n")


def main() -> None:
    args = Arguments(__version__).parse_args()  # pytype: disable=not-callable

    if args.outfile is None or len(args.outfile) == 0:
        in_files = [args.to_convert]
        out_files = [_gv_filename_to_xml(args.to_convert) if not args.stdout else None]
    elif len(args.outfile) == 1:
        in_files = [args.to_convert]
        out_files = args.outfile
    else:
        in_files = [args.to_convert, *args.outfile]
        out_files = [_gv_filename_to_xml(args.to_convert)] + [
            _gv_filename_to_xml(f) for f in args.outfile
        ]

    for in_file, out_file in zip(in_files, out_files, strict=True):
        _convert_file(in_file, args.program, out_file)


if __name__ == "__main__":
    main()
