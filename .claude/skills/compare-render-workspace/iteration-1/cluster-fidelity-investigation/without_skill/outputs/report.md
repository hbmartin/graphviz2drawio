# Cluster Fidelity Investigation: graphviz2drawio vs native graphviz

**Input:** `test/directed/cluster.gv.txt` (classic two-cluster "process #1 / process #2" digraph with `Mdiamond` start and `Msquare` end nodes)

**Method:**
1. Rendered native reference with `dot -Tpng` / `-Tsvg` (graphviz, homebrew).
2. Converted with `uv run python -m graphviz2drawio test/directed/cluster.gv.txt`.
3. Exported the resulting `.drawio` to PNG with the `drawio` CLI (1x and 2x scale).
4. Compared images visually and inspected the generated mxGraph XML against the graphviz SVG coordinates.

**Artifacts in this directory:**
- `cluster_graphviz.png` / `cluster_graphviz.svg` — native graphviz render
- `cluster_converted.drawio` — converter output
- `cluster_drawio.png` / `cluster_drawio_2x.png` — draw.io render of the converted file
- `side_by_side.png` — native (left) vs converted (right)

---

## What is faithful

- **Cluster geometry is exact.** `clust1` (90 x 292.5) and `clust2` (74 x 292.5) match the SVG cluster polygons point-for-point (modulo the constant 4px canvas offset). Node positions/sizes are likewise carried over from the dot layout.
- **Cluster styling is correct.** `cluster_0`: `fillColor=lightgrey; strokeColor=lightgrey` (graphviz `style=filled; color=lightgrey` renders fill and border in the same color — matched). `cluster_1`: `strokeColor=blue; fillColor=none` — matched.
- **Cluster labels** ("process #1", "process #2") are preserved with the right font (Times, 14px), placed top-center inside the box, same as graphviz.
- **Per-cluster node defaults are applied correctly:** a0-a3 are white-filled with white stroke (so they show no outline on the grey background, exactly like graphviz); b0-b3 get the default lightgrey fill with black stroke.
- **Completeness and z-order:** all 10 nodes and all 13 edges are present; clusters are emitted first so nodes/edges draw on top, matching graphviz painting order. Even the subtle 2px x-stagger of b0/b1/b2 from the dot layout is preserved.

## What's off

1. **Clusters are decorative rectangles, not draw.io containers.** In `cluster_converted.drawio`, `clust1`/`clust2` are plain vertices and every node has `parent="1"` (the root layer), not the cluster cell. Consequences in draw.io: dragging a cluster box does not move its member nodes, members aren't semantically grouped, and the container collapse/expand affordance is unavailable. This is the biggest semantic infidelity — graphviz treats clusters as true subgraphs.

2. **`Mdiamond` (start) degrades to a plain rhombus.** Graphviz draws the diamond plus four short tick polylines near the corners (visible in `cluster_graphviz.svg`). The converter maps it to bare `rhombus;` (see `graphviz2drawio/mx/Styles.py`, `DIAMOND = "rhombus;"`), so the M-decorations are lost. Size is exact (75.76 x 36), shape detail is not.

3. **`Msquare` (end) degrades to a plain square.** Graphviz renders a square with diagonal corner notches (four `<polyline>` corner cuts). The converted cell is just an `aspect=fixed;` rectangle with no shape — all corner detail lost; it reads as a generic box.

4. **The a3 -> a0 back-edge escapes its cluster.** Graphviz routes this spline entirely inside cluster_0 (leftmost spline x = 12.89 vs. box edge x = 8 in SVG coords; cluster routing constraints keep edges inside). The converter approximates the 4-segment cubic spline with only two waypoints plus `curved=1`; in the rendered output the curve visibly bulges out past the left border of the grey box and crosses the cluster boundary twice. The curve's shape is also flatter/more lopsided than graphviz's symmetric arc.

5. **Minor edge-entry angle differences.** e.g. b2 -> a3 attaches at a3's exact top-right corner (`entryX=1.0; entryY=0.0`) and approaches horizontally, where graphviz enters diagonally along the ellipse's upper-right arc. Similar small deviations on start -> a0 / start -> b0. Connections use fixed exit/entry fractions, so endpoints are close but approach angles differ slightly.

6. **Cosmetic:** draw.io's `endArrow=block` arrowheads are noticeably wider than graphviz's slim arrows, and overall whitespace/margins are slightly tighter in the draw.io export.

## Verdict

For this test case the converter is **geometrically very faithful** — cluster boxes, fills, border colors, labels, node styles inherited from cluster defaults, and the dot layout all come through correctly. The gaps are (a) **structural**: clusters are not real draw.io containers, so the grouping semantics evaporate on edit; (b) **shape fidelity**: the M-variant node shapes (`Mdiamond`, `Msquare`) lose their distinguishing decorations; and (c) **spline approximation**: the curved back-edge inside cluster_0 is reduced to a two-waypoint curve that leaks outside the cluster boundary graphviz had kept it within.
