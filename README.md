# graphviz2drawio

<a href="https://pypi.org/project/graphviz2drawio/"><img src="https://img.shields.io/pypi/v/graphviz2drawio.svg" alt="pypi"></a>
<a href="https://pypi.python.org/pypi/graphviz2drawio/"><img src="https://img.shields.io/pypi/pyversions/graphviz2drawio.svg" /></a>
[![Build Status](https://travis-ci.com/hbmartin/graphviz2drawio.svg?branch=master)](https://travis-ci.com/hbmartin/graphviz2drawio)
[![codecov.io](https://codecov.io/github/hbmartin/graphviz2drawio/coverage.svg?branch=master)](https://codecov.io/github/hbmartin/graphviz2drawio?branch=master)
<a href="https://github.com/ambv/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" /></a>


Convert graphviz (dot) files into draw.io (mxGraph) format

## Getting Started

### Prerequisites

graphviz2drawio requires [Python 3](https://www.python.org/downloads/) and [Graphviz](https://www.graphviz.org/download/)

* On Mac OS these can be installed with [Homebrew](https://brew.sh/):

```
brew update; brew install python3 graphviz
pip3 install pygraphviz --install-option="--include-path=/usr/local/include/graphviz" --install-option="--library-path=/usr/local/lib/graphviz/"
```

**For M1:**
```
brew install graphviz
python -m pip install \
    --global-option=build_ext \
    --global-option="-I$(brew --prefix graphviz)/include/" \
    --global-option="-L$(brew --prefix graphviz)/lib/" \
    pygraphviz
    
```
* On Ubuntu / Debian based Linux, install graphviz using:

```
sudo apt install python3-pip graphviz graphviz-dev
```

If you encounter installation errors you may need to manually install pygraphviz with links to the graphviz libraries

### Installation / Upgrade

```
pip3 install graphviz2drawio --upgrade
```
## Usage
Run the conversion app on your graphviz file

```
graphviz2drawio example.dot
```
You can them import the output XML file into draw.io

## Python Usage
```python
from graphviz2drawio import graphviz2drawio

xml = graphviz2drawio.convert(graph_to_convert)
print(xml)
```
where `graph_to_convert` can be any of a file path, file handle, string of dot language, or PyGraphviz.AGraph object

## Limitations
Please [open an issue](https://github.com/hbmartin/graphviz2drawio/issues) with your dot file to report crashes or incorrectect conversions.

## Built With

* [PyGraphviz](http://pygraphviz.github.io/documentation/pygraphviz-1.4rc1/reference/index.html) - Python interface to Graphviz


## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

### Code Formatting

This project is linted with [pyflakes](https://github.com/PyCQA/pyflakes) and makes strict use of [Black](https://github.com/ambv/black) for code formatting.


## Authors

* [Harold Martin](https://www.linkedin.com/in/harold-martin-98526971/) - harold.martin at gmail
* Jonah Caplan

## License

[GPLv3](LICENSE.md)

