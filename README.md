# graphviz2drawio

[![Build Status](https://travis-ci.com/hbmartin/graphviz2drawio.svg?branch=master)](https://travis-ci.com/hbmartin/graphviz2drawio)


Convert graphviz (dot) files into draw.io (mxGraph) format

## Getting Started

### Prerequisites

graphviz2drawio requires [Python 3](https://www.python.org/downloads/) and [Graphviz](https://www.graphviz.org/download/)

* On Mac OS these can be installed with [Homebrew](https://brew.sh/):

```
brew update; brew install python3 graphviz
```
* On Ubuntu / Debian based Linux, install graphviz using:

```
sudo apt install graphviz graphviz-dev
```

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

This project makes strict use of Black for code formatting. See the [Black page](https://github.com/ambv/black) for details.


## Authors

* [Harold Martin](https://www.linkedin.com/in/harold-martin-98526971/) - harold.martin at gmail
* Jonah Caplan

## License

[GPL](LICENSE.md)

