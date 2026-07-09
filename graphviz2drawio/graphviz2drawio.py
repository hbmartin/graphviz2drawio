import re
from collections.abc import Iterable
from io import TextIOBase
from pathlib import Path

from pygraphviz import AGraph

from .models.Errors import UnableToParseGraphError
from .models.SvgParser import parse_nodes_edges_clusters
from .mx.MxGraph import MxGraph


def convert(
    graph_to_convert: AGraph | str | TextIOBase | Path,
    layout_prog: str = "dot",
) -> str:
    """Convert a Graphviz graph into draw.io/mxGraph XML.

    :param graph_to_convert: Graphviz input as a ``pygraphviz.AGraph``, a DOT
        string, a path-like object, or an open text file handle.
    :param layout_prog: Graphviz layout program to use when rendering the graph
        to SVG before conversion, such as ``dot``, ``neato``, or ``circo``.
    :returns: A draw.io-compatible mxGraph XML string.
    :raises UnableToParseGraphError: If Graphviz does not return SVG output for
        the graph.
    """
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

    node_parents, cluster_parents = _cluster_membership(graph, nodes, clusters)

    # Put clusters first, so that nodes are drawn in front
    mx_graph = MxGraph(
        clusters,
        nodes,
        edges,
        node_parents=node_parents,
        cluster_parents=cluster_parents,
    )
    return mx_graph.value()


def _cluster_membership(
    graph: AGraph,
    nodes: dict[str, object],
    clusters: dict[str, object],
) -> tuple[dict[str, str], dict[str, str]]:
    """Return nearest rendered cluster parent names for nodes and clusters.

    Graphviz's SVG tells us the rendered cluster rectangles, but not which SVG
    nodes are children of those rectangles. PyGraphviz still has the DOT
    subgraph membership, and Graphviz uses the subgraph name as the SVG cluster
    title, so this bridges the two sources of truth.
    """
    rendered_cluster_names = set(clusters)
    rendered_node_names = set(nodes)
    node_parents: dict[str, str] = {}
    cluster_parents: dict[str, str] = {}

    def walk(subgraphs: Iterable[AGraph], parent_cluster: str | None) -> None:
        for subgraph in subgraphs:
            subgraph_name = subgraph.name
            is_rendered_cluster = subgraph_name in rendered_cluster_names
            current_cluster = subgraph_name if is_rendered_cluster else parent_cluster

            if is_rendered_cluster and parent_cluster is not None:
                cluster_parents[subgraph_name] = parent_cluster

            if current_cluster is not None:
                for node in subgraph.nodes():
                    node_name = str(node)
                    if node_name in rendered_node_names:
                        node_parents[node_name] = current_cluster

            walk(subgraph.subgraphs_iter(), current_cluster)

    walk(graph.subgraphs_iter(), None)
    return node_parents, cluster_parents


def _load_pygraphviz_agraph(  # noqa: PLR0911
    graph_to_convert: AGraph | str | TextIOBase | Path,
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
    if isinstance(graph_to_convert, TextIOBase):
        return AGraph(string=graph_to_convert.read())
    # Use builtin type detection which includes:  hasattr(thing, "open")
    return AGraph(graph_to_convert)
