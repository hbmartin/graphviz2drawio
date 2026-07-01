from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


def _load_sonar_report() -> object:
    path = (
        Path(__file__).resolve().parents[1]
        / ".codex"
        / "skills"
        / "sonarqube-analysis"
        / "scripts"
        / "sonar_report.py"
    )
    spec = importlib.util.spec_from_file_location("sonar_report", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SONAR_REPORT = _load_sonar_report()


def test_normalized_total_uses_first_valid_candidate() -> None:
    assert SONAR_REPORT.normalized_total(None, 3, 5, fallback=1) == 3


def test_normalized_total_ignores_bool_and_negative_values() -> None:
    bool_candidate = True

    assert SONAR_REPORT.normalized_total(bool_candidate, -1, "7", fallback=4) == 4


class FakeSonarClient:
    def __init__(self, responses: list[dict[str, Any]]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        self.calls.append((path, params))
        return self.responses.pop(0)


def test_fetch_issues_uses_top_level_total_when_paging_total_is_none() -> None:
    client = FakeSonarClient(
        [
            {"issues": [{"key": "one"}], "paging": {"total": None}, "total": 2},
            {"issues": [{"key": "two"}], "paging": {"total": None}, "total": 2},
        ],
    )

    issues = SONAR_REPORT.fetch_issues(client, "project", "branch")

    assert [issue["key"] for issue in issues] == ["one", "two"]
    assert [params["p"] for _, params in client.calls] == [1, 2]


def test_fetch_hotspots_falls_back_to_current_count_when_paging_total_is_none() -> None:
    client = FakeSonarClient(
        [{"hotspots": [{"key": "one"}], "paging": {"total": None}}],
    )

    hotspots = SONAR_REPORT.fetch_hotspots(client, "project", "branch")

    assert hotspots == [{"key": "one"}]
    assert [params["p"] for _, params in client.calls] == [1]
