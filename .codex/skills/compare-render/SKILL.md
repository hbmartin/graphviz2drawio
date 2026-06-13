---
name: compare-render
description: Visually verify graphviz2drawio conversion fidelity by rendering a Graphviz source as both native Graphviz PNG and converted draw.io PNG, then inspecting the images. Use when modifying graphviz2drawio conversion or rendering code, updating specs, fixing layout, style, text, edge, or cluster bugs, or answering whether converted output looks right, improved, or regressed. Always perform a visual check before declaring conversion changes done.
---

# Compare Render

## Purpose

Use this repo-specific workflow for `/Users/haroldmartin/Downloads/graphviz2drawio`. Correctness is visual: the draw.io render should match Graphviz's own render, and XML diffs or unit checks can miss visible regressions.

Do not create bundled helper scripts for this skill. Use the repository scripts already present under `scripts/`.

## Core Workflow

1. Work from the repo root:

   ```bash
   cd /Users/haroldmartin/Downloads/graphviz2drawio
   ```

2. Pick 1-3 relevant Graphviz inputs under `test/`. Prefer one small focused case and, when risk is broader, one stress or integration case.

3. Render the comparison:

   ```bash
   ./scripts/compare_render.sh test/directed/hello.gv.txt tmp_render/hello
   ```

   This writes:
   - `<base>_graphviz.png`: Graphviz reference rendered by `dot`
   - `<base>_drawio.png`: converted draw.io XML exported as PNG
   - `<base>.xml`: intermediate draw.io XML

4. Inspect both PNGs with Codex image tooling. Prefer `view_image` and pass absolute paths, for example:

   ```text
   /Users/haroldmartin/Downloads/graphviz2drawio/tmp_render/hello/hello_graphviz.png
   /Users/haroldmartin/Downloads/graphviz2drawio/tmp_render/hello/hello_drawio.png
   ```

5. Compare deliberately:
   - Overall layout: node positions and relative arrangement
   - Node geometry: shapes, sizes, fills, borders, and colors
   - Edges: routing, curvature, attachment points, arrowheads, and direction
   - Labels: text content, placement, font size, and edge-label placement
   - Clusters/subgraphs: bounding boxes and whether they enclose the right nodes

6. Report concrete observations and a clear fidelity verdict. Name specific visible matches or differences; do not summarize as only "looks good".

## Choosing Inputs

| Feature area | Good inputs |
|---|---|
| Minimal smoke test | `test/directed/hello.gv.txt` |
| Node shapes and polygons | `test/directed/fsm.gv.txt`, `test/directed/switch.gv.txt` |
| Clusters and subgraphs | `test/directed/cluster.gv.txt`, `test/directed/compound.gv.txt`, `test/directed/subgraph_multiple.gv.txt` |
| Colors | `test/directed/Twelve_colors.gv.txt` |
| Gradients | `test/gradient/colors.gv.txt`, `test/gradient/radial_angle.gv.txt` |
| Edge routing and curves | `test/undirected/polylines.gv.txt`, `test/undirected/polylines_curved.gv.txt` |
| Ports | `test/directed/port.gv.txt` |
| Labels and multi-labels | `test/directed/multilabel.gv.txt`, `test/directed/tooltip.gv.txt` |
| Records and HTML tables | `test/directed/datastruct.gv.txt`, `test/directed/UML_Class_diagram.gv.txt`, `test/directed/subgraph_with_tables.gv.txt` |
| Radial layouts | `test/twopi/twopi2.gv.txt`, `test/undirected/networkmap_twopi.gv.txt` |
| Large or stress graphs | `test/directed/Linux_kernel_diagram.gv.txt`, `test/directed/world.gv.txt` |

## Broader Regression Checks

When specs changed or the implementation touches shared layout, style, labels, edges, or XML generation, run the textual spec check:

```bash
./scripts/test_specs.sh test specs tmp_out
```

Treat diffs as evidence to inspect, not automatic failure. If the new output is intentionally better, update specs through the repo's normal process.

For changed specs, render before/new/reference trios:

```bash
./scripts/render_specs.sh test specs tmp_render
```

Inspect generated `_new.png`, `_old.png`, and `_reference.png` files with `view_image` before claiming the new render improves fidelity.

## Failure Handling

- If `compare_render.sh` reports missing `dot`, draw.io CLI, or `uv`, report the exact missing dependency and stop the visual verdict.
- If the draw.io PNG is blank or missing, inspect the generated XML before assuming the renderer is wrong.
- Keep generated output in `tmp_render/` or `tmp_out/`; those paths are gitignored and should not be committed.

## Forward-Test Prompts

Use these realistic prompts when validating changes to this skill:

- `Use $compare-render at /Users/haroldmartin/Downloads/graphviz2drawio/.codex/skills/compare-render to check test/directed/cluster.gv.txt and report what differs visually.`
- `Use $compare-render at /Users/haroldmartin/Downloads/graphviz2drawio/.codex/skills/compare-render to investigate whether arrowheads look wrong in test/directed/fsm.gv.txt.`
- `Use $compare-render at /Users/haroldmartin/Downloads/graphviz2drawio/.codex/skills/compare-render to verify edge routing fidelity for test/undirected/polylines.gv.txt and test/undirected/polylines_curved.gv.txt.`
