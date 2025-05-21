#!/usr/bin/env python3

import sys
from argparse import Namespace
from io import TextIOWrapper
from pathlib import Path
from sys import stderr

from .graphviz2drawio import convert
from .models import Arguments
from .version import __version__

DEFAULT_TEXT = "\033[0m"
RED_TEXT = "\033[91m"
BOLD = "\033[1m"

UTF8 = "utf-8"


def _gv_filename_to_xml(filename: str) -> str:
    return ".".join(filename.split(".")[:-1]) + ".xml"


def _write_stderr_message(to_convert: str) -> None:
    stderr.write(f"{RED_TEXT}{BOLD}Error converting {to_convert}\n")
    stderr.write("Please open a report at\n")
    stderr.write("https://github.com/hbmartin/graphviz2drawio/issues\n")
    stderr.write("and include your diagram and the following information:\n\n")
    stderr.write(DEFAULT_TEXT)
    stderr.write(f"Python: {sys.version}, g2d: {__version__}\n")


def _convert_file(
    to_convert: Path | TextIOWrapper,
    program: str,
    encoding: str,
    outfile: str | None,
) -> None:
    output: str | None = None
    try:
        if isinstance(to_convert, TextIOWrapper):
            output = convert(to_convert, program)
        elif isinstance(to_convert, Path):
            with to_convert.open(encoding=encoding) as contents:
                output = convert(contents.read(), program)
    except UnicodeDecodeError:
        if encoding != UTF8 and isinstance(to_convert, Path):
            # Attempt to automatically recover for file. Chinese Windows systems in
            # particular often use other encodings e.g. gbk, cp950, cp1252, etc. but
            # the actual dot files are still UTF-8 encoded
            # https://github.com/hbmartin/graphviz2drawio/issues/105
            return _convert_file(to_convert, program, UTF8, outfile)

        _write_stderr_message(str(to_convert))
        raise

    except Exception:
        _write_stderr_message(str(to_convert))
        raise

    if output is None:
        _write_stderr_message(str(to_convert))
        return None

    if outfile is None:
        print(output)
        return None

    out_path = Path(outfile)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(output)
    stderr.write("Converted file: " + outfile + "\n")
    return None


def main() -> None:
    args = Arguments(__version__).parse_args()  # pytype: disable=not-callable

    in_files: list[TextIOWrapper]
    out_files: list[str | None]

    _validate_args(args)

    if args.stdout and args.outfile is not None:
        sys.stderr.write(f"Writing to {args.outfile} (ignoring stdout)\n")

    if len(args.to_convert) == 1:
        in_files = args.to_convert
        out_files = _determine_single_output(args)
    else:
        in_files = args.to_convert
        out_files = [_gv_filename_to_xml(in_file.name) for in_file in args.to_convert]

    for in_file, out_file in zip(in_files, out_files, strict=True):
        _convert_file(
            to_convert=in_file,
            program=args.program,
            encoding=args.encoding,
            outfile=out_file,
        )


def _determine_single_output(args: Namespace) -> list[str | None]:
    out_files: list[str | None]
    if args.to_convert[0] == sys.stdin:
        out_files = [args.outfile] if args.outfile is not None else [None]
    elif args.outfile is not None:
        out_files = [args.outfile]
    elif args.stdout:
        out_files = [None]
    else:
        out_files = [_gv_filename_to_xml(args.to_convert[0].name)]
    return out_files


def _validate_args(args: Namespace) -> None:
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
        Arguments(__version__).print_help()  # pytype: disable=not-callable
        sys.exit(1)


if __name__ == "__main__":
    main()
