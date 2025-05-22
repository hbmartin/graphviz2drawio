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
    graph = _load_pygraphviz_agraph(graph_to_convert)

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


def _load_pygraphviz_agraph(  # noqa: PLR0911
    graph_to_convert: AGraph | str | TextIOBase | Path | TextIO,
) -> AGraph:
    if isinstance(graph_to_convert, AGraph):
        return graph_to_convert
    if isinstance(graph_to_convert, str):
        if graph_to_convert.endswith((".dot", ".gv", ".txt")):
            return AGraph(filename=graph_to_convert)
        if graph_to_convert.endswith(("}", "}\n")):
            return AGraph(string=graph_to_convert)
        # This fixes a pygraphviz bug where a string beginning with a comment
        # is mistakenly identified as a filename.
        # https://github.com/pygraphviz/pygraphviz/issues/536
        pattern = re.compile(
            pattern=r"^(?=(\s*))\1(strict)?(?=(\s*))\3(graph|digraph)[^{]*{",
            flags=re.MULTILINE,
        )
        if pattern.search(graph_to_convert):
            # graph_to_convert was a graph / dot string
            return AGraph(string=graph_to_convert)
        return AGraph(filename=graph_to_convert)
    # pyrefly: ignore  # missing-attribute
    if hasattr(graph_to_convert, "read") and callable(graph_to_convert.read):
        return AGraph(string=graph_to_convert.read())
    # Use builtin type detection which includes:  hasattr(thing, "open")
    return AGraph(graph_to_convert)
