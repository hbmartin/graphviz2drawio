from sys import stderr

from .graphviz2drawio import convert
from .models import Arguments
from .version import __version__


def main() -> None:

    args = Arguments(__version__).parse_args()

    if not args.stdout:
        stderr.write("This is beta software, please report issues to:\n")
        stderr.write("https://github.com/hbmartin/graphviz2drawio/issues\n")

    try:
        output = convert(args.to_convert, args.program)
    except BaseException:
        stderr.write("Something went wrong, please report\n")
        stderr.write(
            "An automatic crash report can be sent to the developer (no personal or graph information)\n",
        )
        permission = input("Type 'no' to cancel report, press enter to send: ")
        if permission != "no":
            from raven import Client

            client = Client(
                dsn="https://f1fce21b51864819a26ea116ff4e5b7f:9f61501e4891465ea53e0416e5f402b1@sentry.io/1266157",
                release=__version__,
            )
            client.captureException()
        raise

    if args.stdout:
        print(output)
        return

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
