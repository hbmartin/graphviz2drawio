# Troubleshooting

## `dot` / Graphviz not found

graphviz2drawio uses [PyGraphviz](http://pygraphviz.github.io/), a binding around
the **system** Graphviz installation — installing the Python package alone is not
enough. If you see an `ImportError` for `pygraphviz`, or a runtime error about a
missing `dot` executable, install Graphviz with your package manager first (see
[Getting Started](getting-started.md)), then confirm it is on your `PATH`:

```bash
dot -V
```

## `pygraphviz` fails to build during installation

`pygraphviz` compiles a C extension against the Graphviz development headers, so
those headers must be present *before* you `pip` / `pipx install`. On Debian /
Ubuntu install `graphviz-dev` (or `libgraphviz-dev`); on Fedora install
`graphviz-devel`.

On macOS (Apple Silicon) the Homebrew prefix `/opt/homebrew` is not on the
default compiler search path, so the build can fail with a clang error about a
missing `graphviz/cgraph.h`. Point the compiler at the Homebrew paths:

```bash
brew install graphviz
CFLAGS="-I$(brew --prefix graphviz)/include" \
LDFLAGS="-L$(brew --prefix graphviz)/lib" \
pip install --no-cache-dir --force-reinstall pygraphviz
```

## `UnableToParseGraphError`

This is raised when Graphviz returns no SVG for your graph, which usually means
the layout program could not lay the graph out (a missing layout engine or an
invalid graph). Confirm Graphviz can render the file directly:

```bash
dot -Tsvg yourgraph.dot -o output.svg
```

If that command also fails, the problem is in your graph or your Graphviz
installation rather than in graphviz2drawio.

## Layout program not available

The `-p` / `--program` flag (default `dot`) selects a Graphviz layout engine. If
you pass `neato`, `circo`, `twopi`, `fdp`, etc., that binary must be installed —
most are bundled with Graphviz, but minimal installs may omit some. Verify with:

```bash
neato -V
```

## `UnicodeDecodeError` on input files

graphviz2drawio reads files using your locale encoding by default and
automatically retries as UTF-8 when that fails (a common case on non-UTF-8
Windows systems such as `gbk` / `cp1252`, see
[#105](https://github.com/hbmartin/graphviz2drawio/issues/105)). If decoding
still fails, pass the file's actual encoding explicitly:

```bash
graphviz2drawio --encoding utf-8 yourgraph.dot
```

## Unsupported Python version

graphviz2drawio requires **Python 3.11 or newer**. Check your interpreter with
`python --version`, and prefer [pipx](https://pipx.pypa.io/stable/) for the CLI
so it runs in its own isolated, compatible environment.

## Other conversion errors

Errors such as `MissingTitleError`, `MissingTextError`, or
`CouldNotParsePathError` mean Graphviz produced SVG that the parser did not
expect for your particular graph. Please
[open an issue](https://github.com/hbmartin/graphviz2drawio/issues) and include
your diagram along with your Python and graphviz2drawio versions:

```bash
python --version
graphviz2drawio --version
```
