# graphviz2drawio

<a href="https://pypi.org/project/graphviz2drawio/"><img src="https://img.shields.io/pypi/v/graphviz2drawio.svg" alt="pypi"></a>
<a href="https://pypi.python.org/pypi/graphviz2drawio/"><img src="https://img.shields.io/pypi/pyversions/graphviz2drawio.svg" /></a>
[![Lint and Test](https://github.com/hbmartin/graphviz2drawio/actions/workflows/lint.yml/badge.svg)](https://github.com/hbmartin/graphviz2drawio/actions/workflows/lint.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: black](https://img.shields.io/badge/🐧-black-000000.svg)](https://github.com/psf/black)
[![CodeFactor](https://www.codefactor.io/repository/github/hbmartin/graphviz2drawio/badge)](https://www.codefactor.io/repository/github/hbmartin/graphviz2drawio)
[![twitter](https://img.shields.io/badge/@hmartin-00aced.svg?logo=twitter&logoColor=black)](https://twitter.com/hmartin)


Convert graphviz (dot) files into draw.io / lucid (mxGraph) format.

## Installation

### macOS
graphviz2drawio can be installed with [Homebrew](https://brew.sh/):

```bash
brew install hbmartin/graphviz2drawio/graphviz2drawio
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

## Usage
Run the conversion app on your graphviz file. For example, the command below will create converted files `example1.xml` and `example2.xml`.

```bash
graphviz2drawio example1.dot example2.dot
```

Alternately, you can specify the output file (but only if there is a single input file)

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

## Built With

* [PyGraphviz](http://pygraphviz.github.io/documentation/pygraphviz-1.4rc1/reference/index.html) - Python interface to Graphviz
* [svg.path](https://github.com/regebro/svg.path) - SVG path objects and parser


## Contributing

Pull requests and issue reports are welcome. For major changes, please open an issue first to discuss what you would like to change.

Thanks to all the people who have helped make this project succesful!

[![Profile images of all the contributors](https://contrib.rocks/image?repo=hbmartin/graphviz2drawio)](https://github.com/hbmartin/graphviz2drawio/graphs/contributors)


### Development Setup

```bash
git clone git@github.com:hbmartin/graphviz2drawio.git
cd graphviz2drawio
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Replace with the actual path to your dot files
python -m graphviz2drawio test/directed/hello.gv.txt
```

## Roadmap to 0.5
- [ ] Migrate to uv/hatch for packaging and dep mgmt
- [ ] Turn on master branch protection
- [ ] Text alignment inside of shape
- [ ] Port layout/orientation
- [ ] Support for fill gradient

## License

© [Harold Martin](https://www.linkedin.com/in/harold-martin-98526971/) - released under [GPLv3](LICENSE.md)

