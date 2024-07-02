# graphviz2drawio

<a href="https://pypi.org/project/graphviz2drawio/"><img src="https://img.shields.io/pypi/v/graphviz2drawio.svg" alt="pypi"></a>
<a href="https://pypi.python.org/pypi/graphviz2drawio/"><img src="https://img.shields.io/pypi/pyversions/graphviz2drawio.svg" /></a>
[![Lint and Test](https://github.com/hbmartin/graphviz2drawio/actions/workflows/lint.yml/badge.svg)](https://github.com/hbmartin/graphviz2drawio/actions/workflows/lint.yml)
[![codecov.io](https://codecov.io/github/hbmartin/graphviz2drawio/coverage.svg?branch=master)](https://codecov.io/github/hbmartin/graphviz2drawio?branch=master)
<a href="https://github.com/ambv/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" /></a>


Convert graphviz (dot) files into draw.io (mxGraph) format

## Getting Started

### Prerequisites

graphviz2drawio requires [Python 3](https://www.python.org/downloads/) and [Graphviz](https://www.graphviz.org/download/)

* On mac OS you MUST install and configure the graphviz binary. This can be installed with [Homebrew](https://brew.sh/):

```
brew update; brew install python3 graphviz
pip3 install pygraphviz
```

If you encounter build errors you may need to point pygraphviz with links to the graphviz libraries

```
export CFLAGS="-I$(brew --prefix graphviz)/include/"                                                   
export LDFLAGS="-L$(brew --prefix graphviz)/lib/"
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


## Authors

* [Harold Martin](https://www.linkedin.com/in/harold-martin-98526971/) - harold.martin at gmail
* Jonah Caplan

## License

[GPLv3](LICENSE.md)

