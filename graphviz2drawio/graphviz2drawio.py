#!/usr/bin/env python3

from pygraphviz import AGraph

from .models import parse_nodes_edges_clusters
from .mx.MxGraph import MxGraph


def convert(graph_to_convert, layout_prog="dot"):
    if isinstance(graph_to_convert, AGraph):
        graph = graph_to_convert
    else:
        graph = AGraph(graph_to_convert)

    graph_edges = {
        e[0] + "->" + e[1]: list(e.attr.iteritems()) for e in graph.edges_iter()
    }
    graph_nodes = {n: list(n.attr.iteritems()) for n in graph.nodes_iter()}

    svg_graph = graph.draw(prog=layout_prog, format="svg")
    nodes, edges, clusters = parse_nodes_edges_clusters(svg_graph)
    [e.enrich_from_graph(graph_edges[e.gid]) for e in edges]
    [n.enrich_from_graph(graph_nodes[n.gid]) for n in nodes.values()]

    # Put clusters first, so that nodes are drawn in front
    mx_graph = MxGraph(clusters | nodes, edges)
    return mx_graph.value()
