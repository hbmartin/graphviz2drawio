import sys
from pathlib import Path

import pytest

from graphviz2drawio import __main__ as cli


def test_main_adds_context_note_on_single_file_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dot_file = tmp_path / "bad.dot"
    xml_file = tmp_path / "bad.xml"
    dot_file.write_text("digraph { bad }", encoding="utf-8")

    def fail_convert(_graph: str, _program: str) -> str:
        msg = "conversion failed"
        raise ValueError(msg)

    monkeypatch.setattr(cli, "convert", fail_convert)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["graphviz2drawio", dot_file.name])

    with pytest.raises(ValueError) as exc_info:
        cli.main()

    notes = exc_info.value.__notes__
    assert len(notes) == 1
    assert f"input={dot_file.name}" in notes[0]
    assert "program=dot" in notes[0]
    assert "encoding=" in notes[0]
    assert f"output={xml_file.name}" in notes[0]


def test_main_converts_remaining_files_before_exception_group(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    good_file = tmp_path / "good.dot"
    bad_file = tmp_path / "bad.dot"
    worse_file = tmp_path / "worse.dot"
    good_file.write_text("digraph { good }", encoding="utf-8")
    bad_file.write_text("digraph { bad }", encoding="utf-8")
    worse_file.write_text("digraph { worse }", encoding="utf-8")

    def convert_or_fail(graph: str, _program: str) -> str:
        if "good" in graph:
            return "<mxGraphModel />"
        msg = "conversion failed"
        raise ValueError(msg)

    monkeypatch.setattr(cli, "convert", convert_or_fail)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "graphviz2drawio",
            good_file.name,
            bad_file.name,
            worse_file.name,
        ],
    )

    with pytest.raises(ExceptionGroup) as exc_info:
        cli.main()

    assert (tmp_path / "good.xml").read_text(encoding="utf-8") == "<mxGraphModel />"
    assert len(exc_info.value.exceptions) == 2
    notes = [
        note
        for exc in exc_info.value.exceptions
        for note in getattr(exc, "__notes__", [])
    ]
    assert any(f"input={bad_file.name}" in note for note in notes)
    assert any(f"input={worse_file.name}" in note for note in notes)
