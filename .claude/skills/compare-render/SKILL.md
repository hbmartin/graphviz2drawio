---
name: compare-render
description: Visually verify graphviz2drawio conversion fidelity by rendering a graphviz source side-by-side as a native graphviz PNG and a converted draw.io PNG, then reading both images to compare. Use this whenever modifying conversion code in graphviz2drawio/ (nodes, edges, styles, text, layout), fixing a rendering or fidelity bug, or whenever the user asks if output "looks right" or "improved" — even if they don't explicitly ask for a visual check. Always verify visually before declaring a conversion change done.
---

# Compare Render: Visual Fidelity Checking

graphviz2drawio converts Graphviz files into draw.io XML. Correctness here is
ultimately *visual*: the draw.io render should look like what graphviz itself
produces. Unit tests and spec diffs can pass while the output looks wrong, so
any change to conversion logic should end with an actual side-by-side look.

## Core workflow

1. **Pick 1–3 relevant test inputs** from `test/` that exercise the feature
   you're changing (see the table below). Prefer a small file plus one
   stress-test file.

2. **Render the "before" state first** if you haven't made changes yet:

   ```bash
   ./scripts/compare_render.sh test/directed/hello.gv.txt tmp_render/before
   ```

   Skip this if the change is already made — the graphviz PNG is the ground
   truth either way, so an after-only comparison is still meaningful.

3. **Make your change, then render "after":**

   ```bash
   ./scripts/compare_render.sh test/directed/hello.gv.txt tmp_render/after
   ```

   This produces `<base>_graphviz.png` (ground truth, rendered by `dot`) and
   `<base>_drawio.png` (your conversion, rendered by the draw.io CLI), plus the
   intermediate `<base>.xml`.

4. **Read both PNGs with the Read tool** and compare them deliberately,
   checking each of:
   - overall layout: node positions and relative arrangement
   - node shapes, sizes, fill and border colors
   - edge routing (straight vs curved, where they attach), arrowheads and
     their direction
   - labels: text content, placement, font size; edge labels especially
   - clusters/subgraphs: bounding boxes present and enclosing the right nodes

5. **Report what you see honestly.** Name specific differences ("the edge
   label sits on top of node B instead of beside the edge") rather than
   "looks good". If something regressed versus the before render or the
   graphviz reference, say so — a failed visual check is a finding, not a
   reason to skip the report.

## Choosing test inputs by feature area

| Feature being changed | Good inputs (under `test/`) |
|---|---|
| Minimal smoke test | `directed/hello.gv.txt` |
| Node shapes / polygons | `directed/fsm.gv.txt`, `directed/switch.gv.txt` |
| Clusters / subgraphs | `directed/cluster.gv.txt`, `directed/compound.gv.txt`, `directed/subgraph_multiple.gv.txt` |
| Colors | `directed/Twelve_colors.gv.txt` |
| Gradients | `gradient/colors.gv.txt`, `gradient/radial_angle.gv.txt` |
| Edge routing / curves | `undirected/polylines.gv.txt`, `undirected/polylines_curved.gv.txt` |
| Ports | `directed/port.gv.txt` |
| Labels / multi-labels | `directed/multilabel.gv.txt`, `directed/tooltip.gv.txt` |
| Records / HTML tables | `directed/datastruct.gv.txt`, `directed/UML_Class_diagram.gv.txt`, `directed/subgraph_with_tables.gv.txt` |
| Radial layouts | `twopi/twopi2.gv.txt`, `undirected/networkmap_twopi.gv.txt` |
| Large/stress graphs | `directed/Linux_kernel_diagram.gv.txt`, `directed/world.gv.txt` |

## Catching regressions beyond the file you're focused on

A fix for one feature frequently shifts output for many graphs. After the
targeted comparison passes:

- **Textual spec check** — converts every test input and diffs against the
  committed expected XML in `specs/` (ignoring unstable ids):

  ```bash
  uv run ./scripts/test_specs.sh test tmp_out
  ```

  Differences are not automatically failures — if the new output is *better*,
  the specs should be updated (see `scripts/generate_specs.sh`). Decide by
  looking, not by diff size.

- **Visual spec check** — renders any spec XMLs you've modified as
  `_new.png` / `_old.png` (HEAD version) / `_reference.png` (graphviz) trios:

  ```bash
  ./scripts/render_specs.sh test specs tmp_render
  ```

  Read the trios for each changed spec to confirm new beats old.

## Practicalities

- Run scripts from the repo root. Output dirs (`tmp_render/`, `tmp_out/`) are
  gitignored — never commit renders.
- The script needs `dot` (`brew install graphviz`) and the draw.io CLI
  (`brew install --cask drawio`); it tells you which is missing.
- The first draw.io CLI invocation can take ~10s while the app cold-starts;
  later runs are faster.
- If the draw.io PNG comes out blank or missing, the converted XML is likely
  malformed — inspect the intermediate `<base>.xml` in the output dir before
  blaming the renderer.
