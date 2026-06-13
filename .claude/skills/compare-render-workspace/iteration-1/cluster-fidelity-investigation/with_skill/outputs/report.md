# Cluster fidelity investigation: test/directed/cluster.gv.txt

Comparison of the native graphviz render (`cluster/cluster_graphviz.png`, ground
truth) against the graphviz2drawio conversion rendered by the draw.io CLI
(`cluster/cluster_drawio.png`), produced via `./scripts/compare_render.sh`.
Intermediate converted XML: `cluster/cluster.xml`. Zoomed crops used for the
comparison are in `cluster/` (`crop_*_top.png`, `crop_*_end.png`,
`cluster_drawio_3x.png`).

## What's faithful

- **Cluster bounding boxes**: both clusters are present, sized and positioned
  correctly, and enclose the right nodes (a0-a3 in the grey box, b0-b3 in the
  blue box).
- **Cluster styling**: cluster_0's `style=filled; color=lightgrey` comes through
  as a lightgrey fill with matching (invisible) border; cluster_1's blue,
  unfilled border is correct.
- **Cluster labels**: "process #1" and "process #2" both render at the top of
  their boxes (`verticalAlign=top`), with correct text, font size, and color,
  roughly matching graphviz's top-centered placement.
- **Node attribute inheritance inside clusters**: the per-subgraph
  `node [style=filled,color=white]` and `node [style=filled]` defaults are
  honored -- a-nodes are white-on-white (borderless look on the grey box),
  b-nodes are lightgrey with black borders, exactly as graphviz draws them.
- **Z-order**: clusters are emitted first so nodes/edges draw on top.
- **Topology and layout**: all 13 edges exist with correct direction and
  arrowheads, including the cross-cluster edges (a1->b3, b2->a3), the back
  edge a3->a0 (rendered curved, like graphviz), and edges that cross cluster
  borders. Relative node positions match the dot layout closely.

## What's off

1. **Mdiamond and Msquare degrade to plain shapes** (most visible defect).
   - `start [shape=Mdiamond]` becomes a plain `rhombus` -- the four corner tick
     marks that distinguish an Mdiamond are gone, and the diamond's proportions
     differ slightly (drawio: 75.76x36).
   - `end [shape=Msquare]` becomes a plain square (`aspect=fixed` rect) -- the
     four diagonal corner lines are missing entirely.
   - Root cause: `graphviz2drawio/mx/Shape.py` has no Mdiamond/Msquare/Mcircle
     entries; the converter reconstructs the base polygon from the SVG and
     drops graphviz's extra corner-decoration polylines.

2. **Clusters are decorative rectangles, not draw.io containers.** In
   `cluster.xml` every node has `parent="1"`; `clust1`/`clust2` are ordinary
   vertices placed behind the nodes (see `MxGraph.__init__` in
   `graphviz2drawio/mx/MxGraph.py`, which just calls `add_node` on clusters
   first). Visually fine, but semantically unfaithful: in the draw.io editor,
   dragging a cluster does not move its member nodes, and nodes don't belong
   to the cluster group. graphviz treats clusters as true containment.

3. **Spline edges are flattened to straight segments.** graphviz routes
   start->a0, start->b0, a1->b3, b2->a3, and the ->end edges as gentle bezier
   curves; the conversion emits straight source/target connections (only
   a3->a0 keeps `curved=1`). The layout still reads correctly, but edge
   geometry near the clusters is subtly different -- e.g. start->b0 cuts
   straight through the blue cluster border instead of curving along it.

4. **Minor**: overall canvas/scale is smaller (204x405 vs 299x545 px) and
   vertical whitespace is tighter; a cosmetic difference only since relative
   geometry is preserved.

## Verdict

Cluster handling itself is visually quite faithful for this test: boxes,
fills, border colors, labels, membership, and inherited node styles all match
graphviz. The real fidelity gaps in this file are (a) the M-variant node
shapes losing their corner decorations, (b) the loss of true cluster
containment in the draw.io model, and (c) straight-line edge routing replacing
graphviz splines.
