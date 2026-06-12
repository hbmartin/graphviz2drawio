from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("graphviz2drawio")
except PackageNotFoundError:
    __version__ = "0.0.0"

if __name__ == "__main__":
    print(__version__)
