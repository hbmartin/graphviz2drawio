#!/usr/bin/env python3

from collections import OrderedDict
from typing import IO

from pygraphviz import AGraph

from .models.SvgParser import parse_nodes_edges_clusters
from .mx.MxGraph import MxGraph


def convert(graph_to_convert: AGraph | str | IO, layout_prog: str = "dot") -> str:
    if isinstance(graph_to_convert, AGraph):
        graph = graph_to_convert
    else:
        graph = AGraph(graph_to_convert)

    graph_edges: dict[str, dict] = {
        f"{e[0]}->{e[1]}-"
        + (e.attr.get("xlabel") or e.attr.get("label") or ""): e.attr.to_dict()
        for e in graph.edges_iter()
    }
    graph_nodes: dict[str, dict] = {n: n.attr.to_dict() for n in graph.nodes_iter()}

    svg_graph = graph.draw(prog=layout_prog, format="svg")

    nodes, edges, clusters = parse_nodes_edges_clusters(
        svg_data=svg_graph,
        is_directed=graph.directed,
    )

    for e in edges:
        e.enrich_from_graph(graph_edges[e.key_for_enrichment])
    for n in nodes.values():
        n.enrich_from_graph(graph_nodes[n.gid])

    # Put clusters first, so that nodes are drawn in front
    mx_graph = MxGraph(OrderedDict(list(clusters.items()) + list(nodes.items())), edges)
    return mx_graph.value()
