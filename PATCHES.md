# graphviz2drawio — Patch Notes

Fork of [hbmartin/graphviz2drawio](https://github.com/hbmartin/graphviz2drawio) with fixes for edge label and multiple-edge conversion failures when Graphviz wraps SVG elements in `<a>` anchor tags.

---

## Background

When a `.dot` graph assigns a `URL` attribute to edges (common in tools like `rqt_graph` for ROS), Graphviz wraps the `<path>` and `<text>` child elements of each edge `<g>` inside an `<a xlink:href="...">` anchor tag:

```xml
<!-- What graphviz2drawio expected -->
<g class="edge">
  <title>...</title>
  <path d="..." />
  <text>label text</text>
</g>

<!-- What Graphviz 2.43+ actually generates when URL is set -->
<g class="edge">
  <title>...</title>
  <g id="a_edge1">
    <a xlink:href="...">
      <path d="..." />       <!-- buried one level deeper -->
    </a>
  </g>
  <g id="a_edge1-label">
    <a xlink:href="...">
      <text>label text</text> <!-- buried one level deeper -->
    </a>
  </g>
</g>
```

The original parser searched only **direct children** of each edge `<g>`, so it never found the `<path>` or `<text>` elements. This caused two symptoms:
- All edges had no curve geometry (positions were wrong)
- All edge labels were empty
- Multiple parallel edges between the same node pair collapsed into one (because without a curve, all parallel edges had the same deduplication key)

---

## Bug 1 — SVG path and text elements not found

**File:** `graphviz2drawio/models/SVG.py`

`get_first` and `findall` used a single-slash XPath selector, which only matches direct children. Changed to double-slash (`//`) for recursive descent, finding elements at any nesting depth.

```python
# BEFORE
def get_first(g: Element, tag: str) -> Element | None:
    return g.find(f"./{NS_SVG}{tag}")

def findall(g: Element, tag: str) -> list[Element]:
    return g.findall(f"./{NS_SVG}{tag}")

# AFTER
def get_first(g: Element, tag: str) -> Element | None:
    return g.find(f".//{NS_SVG}{tag}")

def findall(g: Element, tag: str) -> list[Element]:
    return g.findall(f".//{NS_SVG}{tag}")
```

---

## Bug 2 — Edge labels still empty after Bug 1 fix

**File:** `graphviz2drawio/mx/EdgeFactory.py`

Even after fixing `SVG.py`, edge labels remained empty. `EdgeFactory.from_svg` builds its label list by iterating directly over the children of `g` with `for tag in g` and filtering by `SVG.is_tag(tag, "text")`. This bypasses `SVG.findall` entirely, so the recursive fix in Bug 1 had no effect here.

Changed the labels list comprehension to use `SVG.findall` so it benefits from the recursive search.

```python
# BEFORE
labels: list[Text] = [
    text_from_tag
    for tag in g
    if SVG.is_tag(tag, "text")
    and (text_from_tag := Text.from_svg(tag)) is not None
]

# AFTER
labels: list[Text] = [
    text_from_tag
    for tag in SVG.findall(g, "text")
    if (text_from_tag := Text.from_svg(tag)) is not None
]
```

---

## Summary of changed files

| File | Change |
|---|---|
| `graphviz2drawio/models/SVG.py` | `get_first` and `findall` use `.//{tag}` instead of `./{tag}` |
| `graphviz2drawio/mx/EdgeFactory.py` | Labels list comprehension uses `SVG.findall(g, "text")` instead of iterating `g` directly |

---

## Root cause

This is a Graphviz version compatibility issue. Graphviz began wrapping SVG child elements in `<a>` anchor tags when edges have a `URL` attribute set. The original parser was written against SVG output that did not use this wrapping. The fix is version-agnostic — recursive XPath search works whether or not the `<a>` wrapper is present.
