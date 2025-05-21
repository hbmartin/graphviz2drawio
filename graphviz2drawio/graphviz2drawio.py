import re
from io import TextIOBase
from pathlib import Path
from typing import TextIO

from pygraphviz import AGraph

from .models.Errors import UnableToParseGraphError
from .models.SvgParser import parse_nodes_edges_clusters
from .mx.MxGraph import MxGraph


def convert(
    graph_to_convert: AGraph | str | TextIOBase | Path | TextIO,
    layout_prog: str = "dot",
) -> str:
    if isinstance(graph_to_convert, AGraph):
        graph = graph_to_convert
    elif isinstance(graph_to_convert, str):
        # This fixes a pygraphviz bug where a string beginning with a comment
        # is mistakenly identified as a filename.
        # https://github.com/pygraphviz/pygraphviz/issues/536
        pattern = re.compile(
            r"(?:\s*(?:/\*[^*]*\*+(?:[^/*][^*]*\*+)*/|//[^\r\n]*|\#[^\r\n]*)\s*)*\s*(strict)?\s*(graph|digraph).*?\{.*\}\s*",
            re.DOTALL | re.MULTILINE | re.VERBOSE,
        )
        if pattern.match(graph_to_convert):
            graph = AGraph(string=graph_to_convert)
        else:
            graph = AGraph(filename=graph_to_convert)
    elif hasattr(graph_to_convert, "read"):
        graph = AGraph(string=graph_to_convert.read())
    else:
        # Use builtin type detection which includes:  hasattr(thing, "open")
        graph = AGraph(graph_to_convert)

    graph_edges: dict[str, dict] = {
        f"{e[0]}->{e[1]}-"
        # pyrefly: ignore  # missing-attribute
        + (e.attr.get("xlabel") or e.attr.get("label") or ""): e.attr.to_dict()
        for e in graph.edges_iter()
    }

    # pyrefly: ignore  # missing-attribute
    graph_nodes: dict[str, dict] = {n: n.attr.to_dict() for n in graph.nodes_iter()}

    svg_graph: bytes | None = graph.draw(prog=layout_prog, format="svg")

    if svg_graph is None:
        raise UnableToParseGraphError(graph)

    nodes, edges, clusters = parse_nodes_edges_clusters(
        svg_data=svg_graph,
        is_directed=graph.directed,
    )

    for e in edges:
        e.enrich_from_graph(
            graph_edges.get(e.key_for_enrichment)
            or graph_edges.get(e.key_for_enrichment.split("\\n")[0]),
        )
    for n in nodes.values():
        n.enrich_from_graph(graph_nodes[n.gid])

    # Put clusters first, so that nodes are drawn in front
    mx_graph = MxGraph(clusters, nodes, edges)
    return mx_graph.value()
