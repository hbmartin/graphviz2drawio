import reprlib
from os import getenv
from sys import stderr

_blacklist_attrs = ["fill"]
_TRACE_ENRICH_ENV = "GRAPHVIZ2DRAWIO_TRACE_ENRICH"
_MISSING = object()


class GraphObj:
    def __init__(self, sid: str, gid: str) -> None:
        self.sid = sid
        self.gid = gid

    # This method is intentionally documenting a weird compatibility layer,
    # not a clean model API. By the time it runs, the Node or Edge has already
    # been built from Graphviz's SVG output. That SVG-derived object is the
    # source of truth for rendered geometry and for many concrete visual facts:
    # node rectangles/ellipses, edge curves, parsed text objects, stroke/fill
    # colors after Graphviz has resolved color names, gradients, opacity, and
    # the default directedness that EdgeFactory inferred from graph type.
    #
    # The attrs argument is the *raw* DOT attribute dictionary from pygraphviz
    # for the matching source node or edge. It contains information that the SVG
    # either does not preserve in a directly reusable form, or preserves only
    # after expanding/inheriting/defaulting it. This is why the merge looks like
    # a blunt attribute override instead of a tidy translation step: the later
    # mxGraph serializers read Python attributes by name, so copying "shape",
    # "dir", "arrowhead", "arrowtail", "labelloc", etc. onto the existing
    # object can change downstream style selection without a separate mapping.
    # It also copies many attributes that are not consumed today; those become
    # inert dynamic fields on the instance. That dynamic field behavior is part
    # of the current looseness and should be removed only with a replacement
    # that names every supported DOT-to-mxGraph input explicitly.
    #
    # Precedence is deliberately asymmetrical:
    #
    # 1. A non-empty DOT value wins, even when the object already has a value
    #    parsed from SVG. Examples seen in the specs include node shape changing
    #    from the SVG factory's generic "rect"/"ellipse" guess to DOT shapes
    #    such as "box", "circle", or "Mdiamond", and edge dir changing from
    #    the directed graph default of "forward" to explicit "back" or "none".
    #
    # 2. An empty DOT value does *not* erase an existing non-None value. This
    #    protects useful SVG-derived/default values from pygraphviz dictionaries
    #    that contain empty strings for unset inherited/default attributes. The
    #    most visible cases are blank node "shape", blank edge "dir", and blank
    #    node "labelloc"; without this guard, nodes would lose their detected
    #    shape/labelloc and directed edges could lose their arrow direction.
    #    If the field is missing or currently None, the empty string is still
    #    assigned, preserving the old behavior where "known but blank" differs
    #    from "not present on the object".
    #
    # 3. "fill" is blacklisted because SVG parsing has already resolved the
    #    rendered fill into the Node.fill field, including color normalization,
    #    opacity adjustment, gradients, and image handling. Raw DOT fill-ish
    #    values are not equivalent to the mxGraph fillColor value this project
    #    serializes. Other related DOT attributes, such as "fillcolor" and
    #    "style", are still copied because later code may inspect them or a
    #    future refactor may need to account for them explicitly.
    #
    # 4. "shape=none" is ignored. Graphviz uses it to suppress a node's shape,
    #    but by this point the SVG parser may still have useful geometry/text
    #    placement. Blindly storing "none" as Node.shape would route style
    #    lookup through Styles.NODE and can lose the concrete shape inferred
    #    from the rendered SVG.
    #
    # Edges add one more layer of fragility before this method is called:
    # convert() has to match SVG edge objects back to pygraphviz edge attrs by a
    # synthetic key made from "from->to-label". If that key misses, attrs is
    # None and this method leaves the SVG-derived edge alone. That is common for
    # some generated or split-label cases, and the trace hook below exists to
    # make those misses and every apply/skip decision visible while refactoring:
    #
    #     GRAPHVIZ2DRAWIO_TRACE_ENRICH=1 uv run ./scripts/test_specs.sh \
    #         test tmp_out/mac_enrich_trace mac
    #
    # The long-term direction should be a typed, whitelisted merge that says
    # which DOT attributes affect mxGraph output and which are metadata. Until
    # then, this method is the compatibility boundary between "what Graphviz
    # rendered into SVG" and "what the original DOT explicitly requested".
    def enrich_from_graph(self, attrs: dict | None) -> None:
        if attrs is None:
            _trace_enrich(self, None, _MISSING, _MISSING, "skip-no-attrs")
            return
        for k, v in attrs.items():
            current_value = self.__dict__.get(k, _MISSING)
            if v == "" and current_value is not _MISSING and current_value is not None:
                _trace_enrich(
                    self,
                    k,
                    v,
                    current_value,
                    "skip-empty-preserve-existing",
                )
                continue
            if k in _blacklist_attrs:
                _trace_enrich(self, k, v, current_value, "skip-blacklisted")
                continue
            if k == "shape" and v == "none":
                _trace_enrich(self, k, v, current_value, "skip-shape-none")
                continue
            self.__setattr__(k, v)
            _trace_enrich(self, k, v, current_value, "apply")


def _trace_enrich(
    graph_obj: GraphObj,
    attr: str | None,
    value: object,
    current_value: object,
    decision: str,
) -> None:
    if getenv(_TRACE_ENRICH_ENV) is None:
        return

    target = (
        f"{graph_obj.__class__.__name__}"
        f"(sid={graph_obj.sid!r}, gid={graph_obj.gid!r})"
    )
    if attr is None:
        stderr.write(f"[enrich_from_graph] {target} {decision}\n")
        return

    stderr.write(
        "[enrich_from_graph] "
        f"{target} attr={attr!r} value={reprlib.repr(value)} "
        f"current={_format_trace_value(current_value)} decision={decision}\n",
    )


def _format_trace_value(value: object) -> str:
    if value is _MISSING:
        return "<missing>"
    return reprlib.repr(value)
