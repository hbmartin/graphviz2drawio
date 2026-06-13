# Polyline / Curved Edge Regression Check

**Date:** 2026-06-12
**Branch:** qc-rebase (clean working tree, HEAD = 6371541)
**Inputs:** `test/undirected/polylines.gv.txt`, `test/undirected/polylines_curved.gv.txt`
**Method:** `./scripts/compare_render.sh` per the `compare-render` skill — graphviz `dot` PNG (ground truth) vs. graphviz2drawio-converted XML rendered by the draw.io CLI, then both PNGs read and compared visually. Converted XML was also diffed against the committed specs in `specs/undirected/`.

## Verdict: No regression found

Both undirected polyline examples still convert well. The draw.io renders closely
match the graphviz ground truth, and the freshly converted XML is byte-identical
to the committed spec files (ignoring unstable mxCell ids):

| Input | Visual match | Spec diff (`specs/undirected/*.xml`) |
|---|---|---|
| polylines.gv.txt (`splines=polyline`) | Good | identical |
| polylines_curved.gv.txt (`splines=curved`) | Good | identical |

## Detailed observations

### polylines (splines=polyline)

- **Layout:** A and B on the left rank, G/D/E/C/F in the right rank, in the same
  vertical order and relative spacing in both renders.
- **Edge routing:** All 14 edges are straight polyline segments with bend points
  collected along the mid-channel vertical line, just as in the graphviz render.
  The characteristic near-vertical "bus" segment in the middle of the drawing is
  reproduced. A--B is a short straight connector between the two left nodes.
- **Nodes/labels:** Box shapes, sizes, black borders, and centered Times labels
  match. No arrowheads in either render (dir=none), correct.
- **Minor differences:** Sub-pixel attachment-point offsets where edges meet node
  borders; line-join rendering at bend points is slightly softer in draw.io.
  Cosmetic only.

### polylines_curved (splines=curved)

- **Edges are still curved** — the conversion emits `curved=1` with Bezier
  waypoint arrays, and the draw.io render shows smooth curves, not straightened
  segments. This was the main regression worry and it is fine.
- **Routing shape matches:** the fan of curves from A and B crossing in the
  mid-channel, the small X-shaped crossing pattern just right of A/B, the short
  arc for A--B hugging the left nodes, and the long arcs along the right column
  for G--C, G--E, G--F (passing near/through D, E, C as graphviz draws them) are
  all reproduced.
- **Minor differences:** curvature is slightly tighter/looser on a few edges
  (draw.io interpolates the waypoints with its own spline), and the G--F arc
  hugs the right column marginally closer than in the graphviz render. Node
  positions, edge endpoints, and overall topology are faithful. Cosmetic only.

## Spec check

```
diff (ids stripped) specs/undirected/polylines.xml        vs fresh conversion -> identical
diff (ids stripped) specs/undirected/polylines_curved.xml vs fresh conversion -> identical
```

Since the converter output is unchanged from the committed specs, whatever
recent edge-handling changes landed have not altered the output for these two
inputs at all — the visual check confirms that output is still a good match for
graphviz.

## Artifacts in this directory

- `polylines_graphviz.png` / `polylines_drawio.png` — side-by-side pair
- `polylines_curved_graphviz.png` / `polylines_curved_drawio.png` — side-by-side pair
- `polylines.xml`, `polylines_curved.xml` — intermediate converted draw.io XML
