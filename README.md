# graphviz2drawio

<a href="https://pypi.org/project/graphviz2drawio/"><img src="https://img.shields.io/pypi/v/graphviz2drawio.svg" alt="pypi"></a>
<a href="https://pypi.python.org/pypi/graphviz2drawio/"><img src="https://img.shields.io/pypi/pyversions/graphviz2drawio.svg" /></a>
[![Lint and Test](https://github.com/hbmartin/graphviz2drawio/actions/workflows/lint.yml/badge.svg)](https://github.com/hbmartin/graphviz2drawio/actions/workflows/lint.yml)
[![codecov.io](https://codecov.io/github/hbmartin/graphviz2drawio/coverage.svg?branch=master)](https://codecov.io/github/hbmartin/graphviz2drawio?branch=master)
[![Code style: black](https://img.shields.io/badge/🐧️-black-000000.svg)](https://github.com/psf/black)
[![Checked with pytype](https://img.shields.io/badge/🦆-pytype-437f30.svg)](https://google.github.io/pytype/)
[![twitter](https://img.shields.io/badge/@hmartin-00aced.svg?logo=twitter&logoColor=black)](https://twitter.com/hmartin)


Convert graphviz (dot) files into draw.io (mxGraph) format.

## Roadmap for 0.3 release (as of July 2, 2024)

- [x] Migrate from Travis to GHA for CI
- [ ] Migrate from Make to GHA for release
- [ ] Fix "cb" bug
- [x] Add support for clusters
- [x] Add support for edge labels
- [ ] Address or triage all open issues
- [ ] Merge or close all outstanding PRs
- [x] Upgrade to latest pygraphviz
- [ ] Upgrade to latest svg.path
- [ ] Add tests for all new features
- [ ] Reformat for most recent black style
- [ ] Publish release docs to GH pages

## Getting Started

### Prerequisites

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

## CLI Installation

It is recommended to use [pipx](https://pipx.pypa.io/stable/) to install and run the CLI tool. If you wish to use the library, you can install with `pip` instead.

```bash
brew install pipx
pipx install -U graphviz2drawio
```

## Usage
Run the conversion app on your graphviz file

```
graphviz2drawio example.dot
```
You can them import the output XML file into draw.io

## Library Usage
```python
from graphviz2drawio import graphviz2drawio

xml = graphviz2drawio.convert(graph_to_convert)
print(xml)
```
where `graph_to_convert` can be any of a file path, file handle, string of dot language, or PyGraphviz.AGraph object

## Limitations
Please [open an issue](https://github.com/hbmartin/graphviz2drawio/issues) with your dot file to report crashes or incorrect conversions.

## Built With

* [PyGraphviz](http://pygraphviz.github.io/documentation/pygraphviz-1.4rc1/reference/index.html) - Python interface to Graphviz
* [svg.path](https://github.com/regebro/svg.path) - SVG path objects and parser


## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Developing

```bash
git clone git@github.com:hbmartin/graphviz2drawio.git
cd graphviz2drawio
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Replace with the actual path to your dot files
python -m graphviz2drawio test/directed/hello.gv.txt
```

## Roadmap to 1.0 release
- [ ] Complete test suite for official graphviz examples
- [ ] Migrate to uv/hatch for packaging and dep mgmt
- [ ] Bezier curve support
- [ ] Port layout
- [ ] Implementation for other outstanding TODOs

## License

[GPLv3](LICENSE.md)

