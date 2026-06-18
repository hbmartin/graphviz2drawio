# graphviz2drawio

[![PyPI - Version](https://img.shields.io/pypi/v/graphviz2drawio)](https://pypi.org/project/graphviz2drawio/)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/graphviz2drawio/badges/version.svg)](https://anaconda.org/conda-forge/graphviz2drawio)
[![homebrew version](https://img.shields.io/homebrew/v/graphviz2drawio)](https://formulae.brew.sh/formula/graphviz2drawio)
[![Lint and Test](https://github.com/hbmartin/graphviz2drawio/actions/workflows/lint.yml/badge.svg)](https://github.com/hbmartin/graphviz2drawio/actions/workflows/lint.yml)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/hbmartin/graphviz2drawio)
[![CodeFactor](https://www.codefactor.io/repository/github/hbmartin/graphviz2drawio/badge)](https://www.codefactor.io/repository/github/hbmartin/graphviz2drawio)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=hbmartin_graphviz2drawio&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=hbmartin_graphviz2drawio)

Convert graphviz (dot) files to draw.io / lucid (mxGraph) format. Beautiful and editable graphs in your favorite editor.

## Installation

### macOS

graphviz2drawio can be installed with [Homebrew](https://brew.sh/):

```bash
brew install graphviz2drawio
```

### Linux

It is recommended to use [pipx](https://pipx.pypa.io/stable/) to install and run the CLI tool. If you wish to use the library, you can install with `pip` instead.

Note that the graphviz library is required before installing this package.

#### Ubuntu / Debian

```bash
sudo apt update
sudo apt install pipx graphviz graphviz-dev
pipx install graphviz2drawio
# To update: pipx upgrade graphviz2drawio
```

#### Fedora

```bash
sudo dnf install pipx
pipx ensurepath
pipx install graphviz2drawio
# To update: pipx upgrade graphviz2drawio
```

### Anaconda

```bash
conda install conda-forge::graphviz2drawio
```

## Usage

Run the conversion app on your graphviz file. For example, the command below will create converted files `example1.xml` and `example2.xml`.

```bash
graphviz2drawio example1.dot example2.dot
```

Alternatively, you can specify the output file (but only if there is a single input file)

```bash
graphviz2drawio example.dot -o /path/to/somewhere/new_name.xml
```

Output can also be sent to stdout by using the `--stdout` flag.

Graphs can be piped in from stdin and sent to stdout (default) or to a file with `-o ...`.

## Library Usage

```python
from graphviz2drawio import graphviz2drawio

graph_to_convert = ...
xml = graphviz2drawio.convert(graph_to_convert)
print(xml)
```

where `graph_to_convert` can be any of a file path, file handle, string of dot language, or PyGraphviz.AGraph object

## Troubleshooting

### `dot` / Graphviz not found

graphviz2drawio uses [PyGraphviz](http://pygraphviz.github.io/), which is a
binding around the **system** Graphviz installation — installing the Python
package alone is not enough. If you see an `ImportError` for `pygraphviz`, or a
runtime error about a missing `dot` executable, install Graphviz with your
package manager first (see [Installation](#installation)), then confirm it is on
your `PATH`:

```bash
dot -V
```

### `pygraphviz` fails to build during installation

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

### `UnableToParseGraphError`

This is raised when Graphviz returns no SVG for your graph, which usually means
the layout program could not lay the graph out (a missing layout engine or an
invalid graph). Confirm Graphviz can render the file directly:

```bash
dot -Tsvg yourgraph.dot -o /dev/null
```

If that command also fails, the problem is in your graph or your Graphviz
installation rather than in graphviz2drawio.

### Layout program not available

The `-p` / `--program` flag (default `dot`) selects a Graphviz layout engine. If
you pass `neato`, `circo`, `twopi`, `fdp`, etc., that binary must be installed —
most are bundled with Graphviz, but minimal installs may omit some. Verify with:

```bash
neato -V
```

### `UnicodeDecodeError` on input files

graphviz2drawio reads files using your locale encoding by default and
automatically retries as UTF-8 when that fails (a common case on non-UTF-8
Windows systems such as `gbk` / `cp1252`, see
[#105](https://github.com/hbmartin/graphviz2drawio/issues/105)). If decoding
still fails, pass the file's actual encoding explicitly:

```bash
graphviz2drawio --encoding utf-8 yourgraph.dot
```

### Unsupported Python version

graphviz2drawio requires **Python 3.10 or newer**. Check your interpreter with
`python --version`, and prefer [pipx](https://pipx.pypa.io/stable/) for the CLI
so it runs in its own isolated, compatible environment.

### Other conversion errors

Errors such as `MissingTitleError`, `MissingTextError`, or
`CouldNotParsePathError` mean Graphviz produced SVG that the parser did not
expect for your particular graph. Please
[open an issue](https://github.com/hbmartin/graphviz2drawio/issues) and include
your diagram along with your Python and graphviz2drawio versions:

```bash
python --version
graphviz2drawio --version
```

## Built With

* [PyGraphviz](http://pygraphviz.github.io/documentation/pygraphviz-1.4rc1/reference/index.html) - Python interface to Graphviz
* [svg.path](https://github.com/regebro/svg.path) - SVG path objects and parser

## Contributing

Pull requests and issue reports are welcome. For major changes, please open an issue first to discuss what you would like to change.

To see architectural and process diagrams please visit [the deepwiki page](https://deepwiki.com/hbmartin/graphviz2drawio)

Thanks to all the people who have contributed to this project!

[![Profile images of all the contributors](https://contrib.rocks/image?repo=hbmartin/graphviz2drawio)](https://github.com/hbmartin/graphviz2drawio/graphs/contributors)

### Development Setup

[uv](https://docs.astral.sh/uv/) is used for packaging and dependency management.

```bash
git clone git@github.com:hbmartin/graphviz2drawio.git
cd graphviz2drawio
uv sync
# Replace with the actual path to your dot files
uv run python -m graphviz2drawio test/directed/hello.gv.txt
```

On macOS (Apple Silicon), `pygraphviz` compiles a C extension against Graphviz,
and Homebrew's `/opt/homebrew` is not on the default compiler search path. If
`uv sync` fails to build `pygraphviz` (clang error about missing
`graphviz/cgraph.h`), install Graphviz and rebuild that package with the
Homebrew paths:

```bash
brew install graphviz
CFLAGS="-I$(brew --prefix graphviz)/include" \
LDFLAGS="-L$(brew --prefix graphviz)/lib" \
uv sync --reinstall-package pygraphviz
```

#### Spec tests

Spec XMLs are stored separately for macOS and Linux because graph layout depends
on platform font metrics. The spec test runner automatically compares against
`specs/mac/` on macOS and `specs/linux/` on Linux.

The scripts invoke `python3` directly, so run the native (macOS) variants
through `uv run` so they resolve to the project venv. The `spec_env.sh` variants
run inside Docker and already have the venv on `PATH`.

```bash
uv run ./scripts/test_specs.sh test/ tmp_out/
./scripts/spec_env.sh ./scripts/test_specs.sh test/ tmp_out/
uv run ./scripts/generate_specs.sh test/ specs/mac/
./scripts/spec_env.sh ./scripts/generate_specs.sh test/ specs/linux/
```

## Roadmap
* Support compatible [arrows](https://graphviz.org/docs/attr-types/arrowType/)
* Support [multiple edges](https://graphviz.org/Gallery/directed/switch.html)
* Support [edges with links](https://graphviz.org/Gallery/directed/pprof.html)

## Legal

© [Harold Martin](https://www.linkedin.com/in/harold-martin-98526971/) - released under [GPLv3](LICENSE.md)

diagrams.net is a trademark and draw.io is a registered trademark of JGraph Limited.
