# Arrowhead bug triage: FSM example (test/directed/fsm.gv.txt)

## Verdict

**The report does not reproduce on the current code (branch `qc-rebase`, HEAD `6371541`). Arrowheads in the converted draw.io output for the FSM example are correct.**

## What was tested

1. Converted `test/directed/fsm.gv.txt` with the in-repo code:
   `uv run python -m graphviz2drawio test/directed/fsm.gv.txt -o fsm.drawio.xml`
2. Inspected the generated mxGraph XML (edge styles, source/target wiring, geometry).
3. Rendered the graphviz reference (`dot -Tpng`) and the converted file (`drawio -x -f png`, the same engine the draw.io app uses) and compared them visually, including 4x zoomed crops of every edge cluster and both self-loops.
4. Reviewed the arrow-style code path in `graphviz2drawio/mx/Edge.py`.

## Findings

### Edge styles are semantically correct

All 14 edges get the style fragment:

```
endArrow=block;endFill=1;startArrow=none;startFill=0
```

That is the correct draw.io equivalent of graphviz's default for a digraph
(`dir=forward`, `arrowhead=normal`): a single filled triangular arrowhead at the
head end, nothing at the tail. `Edge._get_arrow_shape_and_fill()`
(graphviz2drawio/mx/Edge.py:87-105) derives this from `dir=forward`, which is
set for any directed graph (line 31).

### Connectivity and direction are correct for all 14 edges

Every `source`/`target` pair in the XML was mapped back to node labels and
checked against the .gv source. All 14 edges (LR_0->LR_2, LR_0->LR_1, LR_1->LR_3,
LR_2->LR_6, LR_2->LR_5, LR_2->LR_4, LR_5->LR_7, LR_5->LR_5, LR_6->LR_6, LR_6->LR_5,
LR_7->LR_8, LR_7->LR_5, LR_8->LR_6, LR_8->LR_5) point the right way; no edge is
reversed, so no arrowhead renders at the wrong end.

### Visual comparison confirms it

Side-by-side renders (`fsm_graphviz.png` vs `fsm_drawio.png`) and zoomed crops
(`crop_drawio_*.png`) show:

- All 14 arrowheads are present (none missing, none doubled).
- Each arrowhead sits at the target node's perimeter and points into the node,
  including both self-loops (LR_5 and LR_6) and the long curved LR_8->LR_6 edge.
- Arrowheads are filled black and visually similar in size/shape to graphviz's
  `normal` arrowhead.

### Real (but unrelated) fidelity differences observed

These are geometry differences, not arrowhead problems, and may be what the
reporter actually noticed:

- The self-loops on LR_5 and LR_6 render much flatter/smaller in draw.io than
  in graphviz (a shallow arc rather than a full loop). The arrowhead itself is
  still correctly placed and oriented.
- Minor curve-shape and label-placement differences on a few edges.

### Possible explanation for the report

Arrowhead bugs did exist historically and were fixed:
- `cd2b3ae` "Support invisible nodes and fix arrows (#83)"
- `88d6437` "Fixes for titles with colons, improvement to arrow parsing (#90)"

If the reporter used an older released version (pre-1.0) rather than current
master, they could legitimately have seen wrong arrowheads. On today's code the
FSM example converts with correct arrowheads.

## Artifacts in this directory

| File | Description |
|---|---|
| `fsm.drawio.xml` | Converted draw.io output produced from the repo code |
| `fsm_graphviz.png`, `fsm_graphviz_2x.png` | Graphviz reference renders (dpi-96, dpi-192) |
| `fsm_drawio.png`, `fsm_drawio_4x.png` | draw.io CLI exports of the converted XML (2x, 4x scale) |
| `crop_drawio_lr6_loop.png` | Zoom: LR_6 self-loop + LR_2->LR_4 + LR_8->LR_6 arrowheads |
| `crop_drawio_lr5_loop.png` | Zoom: LR_5 self-loop and the four edges entering LR_5 |
| `crop_drawio_right.png` | Zoom: LR_7/LR_8 cluster (LR_7->LR_8, LR_5<->LR_7, LR_8->LR_5) |
| `crop_drawio_left.png` | Full-graph 2x overview crop |
