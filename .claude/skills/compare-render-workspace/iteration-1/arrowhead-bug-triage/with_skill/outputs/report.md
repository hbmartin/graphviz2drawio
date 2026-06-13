# Arrowhead bug triage: FSM example (test/directed/fsm.gv.txt)

## Verdict

**The report does not reproduce on the current code (branch `qc-rebase`).**
Arrowheads in the converted draw.io output for the FSM example are present,
filled, and point in the correct direction on all 14 edges, matching the
native graphviz render.

## Method

Followed the `compare-render` skill:

1. Rendered ground truth and conversion side by side:
   `./scripts/compare_render.sh test/directed/fsm.gv.txt .../outputs/fsm`
   producing `fsm/fsm_graphviz.png` (dot), `fsm/fsm_drawio.png` (graphviz2drawio +
   draw.io CLI), and the intermediate `fsm/fsm.xml`.
2. Inspected the generated XML edge styles and source/target pairs.
3. Read both PNGs at full size, then cropped and 4x-upscaled the four densest
   arrowhead regions from each render and compared the pairs.

## Evidence

### XML check (fsm/fsm.xml)

- Every one of the 14 edges carries
  `endArrow=block;endFill=1;startArrow=none;startFill=0` — the correct
  mapping for graphviz's default `normal` (filled) directed arrowhead.
- All 14 source/target pairs match the `.gv` edge directions exactly,
  including the bidirectional LR_5/LR_7 pair, the LR_8 -> LR_6 and
  LR_8 -> LR_5 back-edges, and both self-loops (LR_6 -> LR_6, LR_5 -> LR_5).

### Visual check (4x zoom crops, drawio `d_*` vs graphviz `g_*`)

| Region | Files | Result |
|---|---|---|
| LR_6: self-loop, incoming from LR_2 and LR_8, outgoing to LR_5 | `fsm/d_LR6_area.png` vs `fsm/g_LR6_area.png` | Self-loop arrowhead present and pointing into the node; LR_8 -> LR_6 arrowhead points left into LR_6; all match graphviz |
| LR_5: self-loop plus 4 incoming and 2 outgoing edges (busiest node) | `fsm/d_LR5_area.png` vs `fsm/g_LR5_area.png` | All arrowheads present; S(b) points into LR_7, S(a) points back into LR_5 — directions correct |
| LR_8: incoming S(b) from LR_7, outgoing edges to LR_6/LR_5 | `fsm/d_LR8_area.png` vs `fsm/g_LR8_area.png` | Arrowhead attaches at the doublecircle boundary, same as graphviz |
| LR_0: outgoing SS(B), SS(S) | `fsm/d_LR0_area.png` vs `fsm/g_LR0_area.png` | Arrowheads at LR_2 and LR_1, correct direction |

The remaining two edges (LR_2 -> LR_4 `S(A)`, LR_1 -> LR_3 `S($end)`) are
clearly visible with correct arrowheads in the full-size renders.

### Minor (non-defect) differences observed

- draw.io's `block` arrowhead is slightly wider/stubbier than graphviz's
  `normal` arrowhead — a cosmetic renderer difference, not a wrong, missing,
  or reversed arrow.
- Overall layout, node shapes (including doublecircle accepting states),
  labels, and edge routing match graphviz closely.

## Likely explanation for the report

Arrowhead handling was fixed in earlier commits (`cd2b3ae` "Support invisible
nodes and fix arrows" (#83) and `88d6437` "improvement to arrow parsing"
(#90)). The report was probably made against a version predating those fixes,
or observed in a different viewer/zoom. As of HEAD it is not reproducible.

## Files

- `fsm/fsm_graphviz.png` — ground-truth render (dot)
- `fsm/fsm_drawio.png` — converted render (draw.io CLI)
- `fsm/fsm.xml` — intermediate converted XML
- `fsm/d_*.png` / `fsm/g_*.png` — 4x zoom crop pairs used for comparison
