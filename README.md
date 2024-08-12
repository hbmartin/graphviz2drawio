# graphviz2drawio

<a href="https://pypi.org/project/graphviz2drawio/"><img src="https://img.shields.io/pypi/v/graphviz2drawio.svg" alt="pypi"></a>
<a href="https://pypi.python.org/pypi/graphviz2drawio/"><img src="https://img.shields.io/pypi/pyversions/graphviz2drawio.svg" /></a>
[![Lint and Test](https://github.com/hbmartin/graphviz2drawio/actions/workflows/lint.yml/badge.svg)](https://github.com/hbmartin/graphviz2drawio/actions/workflows/lint.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: black](https://img.shields.io/badge/🐧-black-000000.svg)](https://github.com/psf/black)
[![CodeFactor](https://www.codefactor.io/repository/github/hbmartin/graphviz2drawio/badge)](https://www.codefactor.io/repository/github/hbmartin/graphviz2drawio)
[![twitter](https://img.shields.io/badge/@hmartin-00aced.svg?logo=twitter&logoColor=black)](https://twitter.com/hmartin)


Convert graphviz (dot) files into draw.io / lucid (mxGraph) format.

## Prerequisites

The graphviz library is required before installing this package.

#### macOS
Python 3 and graphviz can be installed with [Homebrew](https://brew.sh/):

```bash
brew update
brew install python3 graphviz
# In order to build pygraphviz:
export CFLAGS="-I$(brew --prefix graphviz)/include/"                                                   
export LDFLAGS="-L$(brew --prefix graphviz)/lib/"
```

#### Ubuntu / Debian

```bash
sudo apt install python3-pip graphviz graphviz-dev
```

## Installation

It is recommended to use [pipx](https://pipx.pypa.io/stable/) to install and run the CLI tool. If you wish to use the library, you can install with `pip` instead.

```bash
brew install pipx
pipx install graphviz2drawio
# Use pipx upgrade graphviz2drawio to update
```

## Usage
Run the conversion app on your graphviz file

```bash
graphviz2drawio example.dot
```
You can then import the output XML file into draw.io or lucidchart.

## Library Usage
```python
from graphviz2drawio import graphviz2drawio

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

