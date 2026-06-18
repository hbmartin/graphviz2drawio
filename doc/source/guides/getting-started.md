# Getting Started

graphviz2drawio converts [Graphviz](https://graphviz.org/) (dot) graphs into the
[draw.io](https://www.drawio.com/) / Lucidchart (mxGraph) XML format, so you get
beautiful, automatically laid-out graphs that remain fully editable in your
favorite diagram editor.

## Installation

graphviz2drawio depends on a **system** Graphviz installation (via PyGraphviz),
so install Graphviz first, then the package.

### macOS

```bash
brew install graphviz2drawio
```

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install pipx graphviz graphviz-dev
pipx install graphviz2drawio
```

### Fedora

```bash
sudo dnf install pipx graphviz graphviz-devel
pipx ensurepath
pipx install graphviz2drawio
```

### Anaconda

```bash
conda install conda-forge::graphviz2drawio
```

Run into build or `dot`-not-found errors? See the
[Troubleshooting](troubleshooting.md) guide.

## Command-line usage

Convert one or more dot files. Each input `example.dot` produces `example.xml`
alongside it:

```bash
graphviz2drawio example1.dot example2.dot
```

Choose the output path (only valid with a single input file):

```bash
graphviz2drawio example.dot -o /path/to/new_name.xml
```

Send output to stdout, or pipe a graph in from stdin:

```bash
graphviz2drawio example.dot --stdout
cat example.dot | graphviz2drawio -o example.xml
```

Pick a different Graphviz layout engine with `-p` / `--program` (default `dot`):

```bash
graphviz2drawio --program neato example.dot
```

## Library usage

The package exposes a single {py:func}`~graphviz2drawio.graphviz2drawio.convert`
function that returns the mxGraph XML as a string:

```python
from graphviz2drawio import graphviz2drawio

xml = graphviz2drawio.convert("example.dot")
print(xml)
```

`convert()` is flexible about its input — it accepts any of:

```python
from io import StringIO
from pathlib import Path

import pygraphviz

# A file path (str or Path)
graphviz2drawio.convert("example.dot")
graphviz2drawio.convert(Path("example.dot"))

# A string of dot language
graphviz2drawio.convert("digraph { a -> b }")

# An open file handle
with open("example.dot") as handle:
    graphviz2drawio.convert(handle)

# A pre-built PyGraphviz AGraph
graphviz2drawio.convert(pygraphviz.AGraph("digraph { a -> b }"))
```

Select the layout engine with the second argument, mirroring the CLI's
`--program` flag:

```python
graphviz2drawio.convert("example.dot", "neato")
```

To learn what happens between dot input and mxGraph output, read
[How Conversion Works](how-conversion-works.md).
