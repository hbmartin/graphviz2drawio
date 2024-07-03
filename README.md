# graphviz2drawio

<a href="https://pypi.org/project/graphviz2drawio/"><img src="https://img.shields.io/pypi/v/graphviz2drawio.svg" alt="pypi"></a>
<a href="https://pypi.python.org/pypi/graphviz2drawio/"><img src="https://img.shields.io/pypi/pyversions/graphviz2drawio.svg" /></a>
[![Lint and Test](https://github.com/hbmartin/graphviz2drawio/actions/workflows/lint.yml/badge.svg)](https://github.com/hbmartin/graphviz2drawio/actions/workflows/lint.yml)
[![Code style: black](https://img.shields.io/badge/🐧️-black-000000.svg)](https://github.com/psf/black)
[![twitter](https://img.shields.io/badge/@hmartin-00aced.svg?logo=twitter&logoColor=black)](https://twitter.com/hmartin)


Convert graphviz (dot) files into draw.io (mxGraph) format.

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
pipx install -U graphviz2drawio
```

## Usage
Run the conversion app on your graphviz file

```bash
graphviz2drawio example.dot
```
You can then import the output XML file into draw.io

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

## Roadmap to [0.4](https://github.com/hbmartin/graphviz2drawio/milestone/2)
- [ ] Improved Bezier curve support
- [ ] Subgraph conversion #33
- [ ] Invisible node handling for edges #67
- [ ] Implementation for outstanding TODOs in code
- [ ] Image / tooltip support #49
- [ ] Text on edge alignment #59 
- [ ] Text alignment inside of shape
- [ ] Support for node with `path` shape #47
- [ ] Run ruff in CI
- [ ] Publish api docs to GH pages
- [ ] Restore codecov to test GHA

## Roadmap to 1.0
- [ ] Complete test suite for all graphviz examples
- [ ] Migrate to uv/hatch for packaging and dep mgmt
- [ ] Port layout/orientation
- [ ] Possible to screenshot test with [maxGraph](https://github.com/maxGraph/maxGraph?tab=readme-ov-file) ?

## License

© [Harold Martin](https://www.linkedin.com/in/harold-martin-98526971/) - released under [GPLv3](LICENSE.md)

