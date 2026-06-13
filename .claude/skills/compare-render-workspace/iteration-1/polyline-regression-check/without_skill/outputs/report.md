# Polyline / Curved Edge Regression Check

Date: 2026-06-12
Branch: qc-rebase (clean working tree, HEAD 6371541)

## Task

Verify that recent edge-handling changes have not regressed conversion of the
undirected polyline examples:

- `test/undirected/polylines.gv.txt` (`splines=polyline`)
- `test/undirected/polylines_curved.gv.txt` (`splines=curved`)

## Method

1. Converted both files with `uv run graphviz2drawio <file> -o <out>.xml`.
2. Rendered the original sources natively with `dot -Tpng`.
3. Rendered the converted XML with the `drawio` CLI (`drawio -x -f png -s 2`).
4. Visually compared each graphviz PNG against its draw.io PNG.
5. Inspected the generated mxGraph XML (node/edge counts, edge styles, validity).
6. Ran the relevant automated tests.

## Results

### Conversion

Both files converted without errors or warnings. Both output XMLs are
well-formed (`xmllint` clean).

| File | Nodes expected | Nodes in XML | Edges expected | Edges in XML |
|---|---|---|---|---|
| polylines.gv.txt | 7 | 7 | 14 | 14 |
| polylines_curved.gv.txt | 7 | 7 | 14 | 14 |

All 14 edges (A--B, A--{C,D,E,F,G}, B--{C,D,E,F,G}, G--{C,E,F}) are present in
both outputs.

### Edge styles

- `polylines.xml`: every edge uses `rounded=0` with no `curved` flag, i.e.
  straight polyline segments - correct for `splines=polyline`.
- `polylines_curved.xml`: every edge uses `curved=1` - correct for
  `splines=curved`.
- All edges in both files carry sensible fractional `exitX/exitY` and
  `entryX/entryY` anchors (values in [0,1]), so edges attach to node borders
  rather than floating.

### Visual comparison

**polylines** (`polylines_graphviz.png` vs `polylines_drawio.png`):
Layout matches closely - A/B in the left rank, G/D/E/C/F top-to-bottom in the
right rank. The characteristic vertical "bus" of polyline bend points between
the ranks is reproduced, edge crossings match, and all edges terminate cleanly
on node borders. No missing, duplicated, or stray edges.

**polylines_curved** (`polylines_curved_graphviz.png` vs
`polylines_curved_drawio.png`):
Edges render as smooth curves in draw.io, mirroring graphviz's curved splines:
the small A--B arc on the left, the fan of curves from A and B to the right
rank, and the long G--C / G--E / G--F arcs sweeping around the right-hand
column are all present and routed in the same general shape. Curvature differs
slightly in places (draw.io interpolates its own spline through the waypoints),
but topology, endpoints, and overall routing are faithful. No edges collapsed
to straight lines and none are missing.

### Automated tests

`uv run pytest test/test_graphs.py::test_polylines
test/test_graphs.py::test_polylines_curved test/test_curve.py
test/test_bezier.py -v` - **14/14 passed**, including the two tests that
directly cover these example files.

## Conclusion

**No regression detected.** Both undirected polyline examples still convert
well: correct node/edge counts, correct straight-vs-curved edge styling, valid
XML, passing unit tests, and faithful side-by-side visual renders.

## Artifacts (in this directory)

- `polylines.xml`, `polylines_curved.xml` - converted draw.io files
- `polylines_graphviz.png`, `polylines_curved_graphviz.png` - native graphviz renders
- `polylines_drawio.png`, `polylines_curved_drawio.png` - draw.io renders of the converted files
