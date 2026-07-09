from __future__ import annotations

import io
from importlib import import_module

graph_obj_module = import_module("graphviz2drawio.mx.GraphObj")
GraphObj = graph_obj_module.GraphObj


def _trace_output(obj, attrs, monkeypatch) -> str:
    stream = io.StringIO()
    monkeypatch.setenv("GRAPHVIZ2DRAWIO_TRACE_ENRICH", "1")
    monkeypatch.setattr(graph_obj_module, "stderr", stream)
    obj.enrich_from_graph(attrs)
    return stream.getvalue()


def test_enrich_from_graph_traces_skip_no_attrs(monkeypatch) -> None:
    obj = GraphObj("sid", "gid")

    output = _trace_output(obj, None, monkeypatch)

    assert "skip-no-attrs" in output


def test_enrich_from_graph_traces_empty_preserve_existing(monkeypatch) -> None:
    obj = GraphObj("sid", "gid")
    obj.shape = "ellipse"

    output = _trace_output(obj, {"shape": ""}, monkeypatch)

    assert obj.shape == "ellipse"
    assert "decision=skip-empty-preserve-existing" in output


def test_enrich_from_graph_traces_blacklisted(
    monkeypatch,
) -> None:
    obj = GraphObj("sid", "gid")
    obj.fill = "#ffffff"

    output = _trace_output(obj, {"fill": "#000000"}, monkeypatch)

    assert obj.fill == "#ffffff"
    assert "decision=skip-blacklisted" in output


def test_enrich_from_graph_traces_shape_none_before_empty_skip(
    monkeypatch,
) -> None:
    obj = GraphObj("sid", "gid")
    obj.shape = "ellipse"

    output = _trace_output(obj, {"shape": "none"}, monkeypatch)

    assert obj.shape == "ellipse"
    assert "decision=skip-shape-none" in output


def test_enrich_from_graph_traces_apply(monkeypatch) -> None:
    obj = GraphObj("sid", "gid")

    output = _trace_output(obj, {"label": "node"}, monkeypatch)

    assert obj.label == "node"
    assert "current=<missing>" in output
    assert "decision=apply" in output
