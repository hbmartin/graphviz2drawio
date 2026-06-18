# How Conversion Works

graphviz2drawio does not implement its own graph layout. Instead it lets
Graphviz do what it does best — compute an aesthetically pleasing layout — and
then translates that result into the mxGraph XML that draw.io and Lucidchart
understand. The whole pipeline lives in
{py:func}`~graphviz2drawio.graphviz2drawio.convert`.

## The pipeline

### 1. Load the graph into PyGraphviz

Whatever you pass in — a file path, a dot string, a file handle, or an existing
`AGraph` — is normalized into a single `pygraphviz.AGraph` object. (Internally
this is handled by `_load_pygraphviz_agraph`, which also works around a
PyGraphviz quirk where dot strings beginning with a comment are mistaken for
filenames.)

### 2. Capture the original dot attributes

Before layout, the converter walks the graph's edges and nodes and records their
dot attributes (labels, colors, styles, and so on) into lookup dictionaries.
Graphviz's rendered SVG loses some of this semantic information, so it is kept
aside to be reattached later.

### 3. Lay the graph out as SVG

```python
svg_graph = graph.draw(prog=layout_prog, format="svg")
```

`layout_prog` defaults to `dot` but can be any Graphviz engine (`neato`,
`twopi`, `fdp`, …). Graphviz computes absolute coordinates, edge routing, and
shape geometry and returns SVG. If nothing comes back, the converter raises
{py:class}`~graphviz2drawio.models.Errors.UnableToParseGraphError`.

### 4. Parse the SVG into geometric objects

```python
nodes, edges, clusters = parse_nodes_edges_clusters(
    svg_data=svg_graph,
    is_directed=graph.directed,
)
```

{py:func}`~graphviz2drawio.models.SvgParser.parse_nodes_edges_clusters` reads the
SVG and extracts node shapes and text, edge paths (including Bézier curves), and
cluster/subgraph rectangles into `Node`, `Edge`, and cluster objects.

### 5. Re-enrich with the original dot attributes

Each parsed `Edge` and `Node` is matched back to the attributes captured in
step 2 via `enrich_from_graph`, so styling and labels declared in the dot source
survive the round-trip through SVG.

### 6. Build the mxGraph XML

```python
mx_graph = MxGraph(clusters, nodes, edges)
return mx_graph.value()
```

{py:class}`~graphviz2drawio.mx.MxGraph.MxGraph` assembles the final draw.io /
Lucidchart XML document. Clusters are emitted first so that nodes are drawn in
front of them. The returned string is ready to be written to a `.xml` file or
imported directly into draw.io.

## Where the work happens

| Stage | Module |
| --- | --- |
| Orchestration | `graphviz2drawio.graphviz2drawio` |
| SVG parsing | `graphviz2drawio.models.SvgParser` |
| Node construction | `graphviz2drawio.mx.NodeFactory` |
| Edge construction | `graphviz2drawio.mx.EdgeFactory` |
| Curve geometry | `graphviz2drawio.mx.CurveFactory` |
| mxGraph assembly | `graphviz2drawio.mx.MxGraph` |

See the [API Reference](../modules.rst) for the full module documentation.
