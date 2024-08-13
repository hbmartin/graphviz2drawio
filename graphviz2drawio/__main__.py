import pathlib
import sys
from io import TextIOWrapper
from sys import stderr

from .graphviz2drawio import convert
from .models import Arguments
from .version import __version__

DEFAULT_TEXT = "\033[0m"
RED_TEXT = "\033[91m"
BOLD = "\033[1m"


def _gv_filename_to_xml(filename: str) -> str:
    return ".".join(filename.split(".")[:-1]) + ".xml"


def _convert_file(to_convert: TextIOWrapper, program: str, outfile: str | None) -> None:
    try:
        output = convert(to_convert.read(), program)
    except BaseException:
        stderr.write(f"{RED_TEXT}{BOLD}Error converting {to_convert}\n")
        stderr.write("Please open a report at\n")
        stderr.write("https://github.com/hbmartin/graphviz2drawio/issues\n")
        stderr.write("and include your diagram and the following error:\n\n")
        stderr.write(DEFAULT_TEXT)
        stderr.write(f"Python: {sys.version}, g2d: {__version__}\n")
        raise
    finally:
        to_convert.close()

    if outfile is None:
        print(output)
        return

    pathlib.Path(outfile).write_text(output)
    stderr.write("Converted file: " + outfile + "\n")


def main() -> None:
    args = Arguments(__version__).parse_args()  # pytype: disable=not-callable

    in_files: list[str]
    out_files: list[str | None]

    if len(args.to_convert) > 1 and args.stdout:
        print("Only one file can be converted when using --stdout")
        sys.exit(1)
    if len(args.to_convert) > 1 and args.outfile is not None:
        print("Only one file can be converted when specifying an output file")
        sys.exit(1)
    if len(args.to_convert) == 0 or (
        len(args.to_convert) == 1
        and args.to_convert[0] == sys.stdin
        and sys.stdin.isatty()
    ):
        Arguments(__version__).print_help()
        sys.exit(1)

    if args.stdout and args.outfile is not None:
        sys.stdout.write(f"Writing to {args.outfile} (ignoring stdout)\n")

    if len(args.to_convert) == 1:
        in_files = args.to_convert
        if args.to_convert[0] == sys.stdin:
            out_files = [args.outfile] if args.outfile is not None else [None]
        elif args.outfile is not None:
            out_files = [args.outfile]
        elif args.stdout:
            out_files = [None]
        else:
            out_files = [_gv_filename_to_xml(args.to_convert[0].name)]
    else:
        in_files = args.to_convert
        out_files = [_gv_filename_to_xml(in_file.name) for in_file in args.to_convert]

    for in_file, out_file in zip(in_files, out_files, strict=True):
        _convert_file(in_file, args.program, out_file)


if __name__ == "__main__":
    main()
