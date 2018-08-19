from sys import stderr
from .graphviz2drawio import convert
from .models import Arguments
from .version import __version__


def main():
    args = Arguments(__version__).parse_args()
    stderr.write("This is alpha software, please report issues to:\n")
    stderr.write("https://github.com/hbmartin/graphviz2drawio/issues\n")
    output = convert(args.to_convert)
    if args.outfile is not None:
        outfile = args.outfile
    else:
        base = args.to_convert.split(".")
        outfile = ".".join(base[:-1] + ["xml"])
    with open(outfile, "w") as fd:
        fd.write(output)
    stderr.write("Converted file: " + outfile + "\n")


if __name__ == "__main__":
    main()
