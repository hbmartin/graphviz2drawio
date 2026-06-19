#!/usr/bin/env python3
"""Summarize SonarQube Cloud findings without printing credentials."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_METRICS = ",".join(  # noqa: FLY002
    [
        "alert_status",
        "bugs",
        "vulnerabilities",
        "code_smells",
        "coverage",
        "duplicated_lines_density",
        "ncloc",
        "sqale_rating",
        "reliability_rating",
        "security_rating",
        "security_review_rating",
        "new_bugs",
        "new_vulnerabilities",
        "new_code_smells",
        "new_security_hotspots",
        "new_security_hotspots_reviewed",
        "new_duplicated_lines_density",
        "new_lines",
    ],
)
QUOTE_PAIR_LENGTH = 2
SONAR_SEVERITY_ORDER = ["BLOCKER", "CRITICAL", "MAJOR", "MINOR", "INFO"]


def load_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if path.is_file():
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            value = value.strip()
            if (
                len(value) >= QUOTE_PAIR_LENGTH
                and value[0] == value[-1]
                and value[0] in ("'", '"')
            ):
                value = value[1:-1]
            env[key] = value

    for key in [
        "SONAR_HOST_URL",
        "SONAR_ORG",
        "SONAR_PROJECT_KEY",
        "SONAR_BRANCH",
        "SONAR_TOKEN",
    ]:
        if not env.get(key) and os.environ.get(key):
            env[key] = os.environ[key]

    return env


class SonarClient:
    def __init__(self, host: str, token: str) -> None:
        self.host = host.rstrip("/")
        if not self.host.startswith(("http://", "https://")):
            msg = "SONAR_HOST_URL must start with http:// or https://"
            raise ValueError(msg)
        self.token = token

    def get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        query = urllib.parse.urlencode(params, doseq=True)
        auth_bytes = f"{self.token}:".encode()
        auth_header = base64.b64encode(auth_bytes).decode("utf-8")
        request = urllib.request.Request(  # noqa: S310
            f"{self.host}{path}?{query}",
            headers={"Authorization": f"Basic {auth_header}"},
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
                return json.load(response)
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            msg = f"Sonar API error {error.code} for {path}: {body}"
            raise SystemExit(msg) from error
        except urllib.error.URLError as error:
            msg = f"Sonar API connection error for {path}: {error.reason}"
            raise SystemExit(msg) from error
        except json.JSONDecodeError as error:
            msg = f"Failed to parse JSON response from Sonar API for {path}: {error}"
            raise SystemExit(msg) from error


def issue_path(issue: dict[str, Any]) -> str:
    component = issue.get("component") or ""
    return component.split(":", 1)[1] if ":" in component else component


def issue_sort_key(issue: dict[str, Any]) -> tuple[int, str, int]:
    severity = issue.get("severity") or "INFO"
    severity_index = (
        SONAR_SEVERITY_ORDER.index(severity)
        if severity in SONAR_SEVERITY_ORDER
        else len(SONAR_SEVERITY_ORDER)
    )
    return severity_index, issue_path(issue), issue.get("line") or 0


def first_impact(issue: dict[str, Any]) -> dict[str, str]:
    impacts = issue.get("impacts") or []
    return impacts[0] if impacts else {}


def fetch_issues(
    client: SonarClient,
    project: str,
    branch: str,
    extra: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    page = 1
    params: dict[str, Any] = {
        "componentKeys": project,
        "branch": branch,
        "resolved": "false",
        "ps": 500,
        "additionalFields": "_all",
    }
    if extra:
        params.update(extra)

    while True:
        data = client.get("/api/issues/search", {**params, "p": page})
        page_issues = data.get("issues") or []
        if not page_issues:
            return issues
        issues.extend(page_issues)
        total = (data.get("paging") or {}).get(
            "total",
            data.get("total", len(issues)),
        )
        if len(issues) >= total:
            return issues
        page += 1


def fetch_hotspots(
    client: SonarClient,
    project: str,
    branch: str,
) -> list[dict[str, Any]]:
    hotspots: list[dict[str, Any]] = []
    page = 1
    while True:
        data = client.get(
            "/api/hotspots/search",
            {"projectKey": project, "branch": branch, "p": page, "ps": 500},
        )
        page_hotspots = data.get("hotspots") or []
        if not page_hotspots:
            return hotspots
        hotspots.extend(page_hotspots)
        total = (data.get("paging") or {}).get("total", len(hotspots))
        if len(hotspots) >= total:
            return hotspots
        page += 1


def measure_value(measure: dict[str, Any]) -> str | None:
    if "value" in measure:
        return measure["value"]
    periods = measure.get("periods") or []
    if periods:
        return periods[0].get("value")
    return None


def summarize(args: argparse.Namespace) -> dict[str, Any]:
    env = load_env(Path(args.env))
    missing = [key for key in ["SONAR_HOST_URL", "SONAR_TOKEN"] if not env.get(key)]
    if not args.project and not env.get("SONAR_PROJECT_KEY"):
        missing.append("SONAR_PROJECT_KEY")
    if missing:
        msg = f"Missing required env keys: {', '.join(missing)}"
        raise SystemExit(msg)

    branch = args.branch or env.get("SONAR_BRANCH") or "trunk"
    project = args.project or env["SONAR_PROJECT_KEY"]
    client = SonarClient(env["SONAR_HOST_URL"], env["SONAR_TOKEN"])

    project_info = client.get("/api/components/show", {"component": project})
    branches = client.get("/api/project_branches/list", {"project": project})
    quality_gate = client.get(
        "/api/qualitygates/project_status",
        {"projectKey": project, "branch": branch},
    )
    analyses = client.get(
        "/api/project_analyses/search",
        {"project": project, "branch": branch, "ps": 5},
    )
    measures = client.get(
        "/api/measures/component",
        {"component": project, "branch": branch, "metricKeys": DEFAULT_METRICS},
    )

    issue_filter: dict[str, Any] = {}
    if args.new_code:
        issue_filter["sinceLeakPeriod"] = "true"
    if args.bugs and args.security:
        issue_filter["types"] = "BUG,VULNERABILITY"
    elif args.bugs:
        issue_filter["types"] = "BUG"
    elif args.security:
        issue_filter["types"] = "VULNERABILITY"

    issues = fetch_issues(client, project, branch, issue_filter)
    new_issues = fetch_issues(client, project, branch, {"sinceLeakPeriod": "true"})
    risk_issues = [
        issue
        for issue in issues
        if issue.get("type") in {"BUG", "VULNERABILITY"}
        or issue.get("severity") in {"BLOCKER", "CRITICAL"}
    ]
    hotspots = fetch_hotspots(client, project, branch)
    project_component = project_info.get("component") or {}
    branch_items = branches.get("branches") or []
    quality_gate_status = quality_gate.get("projectStatus") or {}
    analysis_items = analyses.get("analyses") or []
    measure_items = (measures.get("component") or {}).get("measures") or []

    return {
        "project": project_component,
        "branch": branch,
        "branches": branch_items,
        "quality_gate": quality_gate_status,
        "analyses": analysis_items,
        "measures": {
            measure["metric"]: measure_value(measure) for measure in measure_items
        },
        "issues": {
            "total": len(issues),
            "by_type": Counter(issue.get("type") for issue in issues),
            "by_severity": Counter(issue.get("severity") for issue in issues),
            "by_quality": Counter(
                first_impact(issue).get("softwareQuality") for issue in issues
            ),
            "top_rules": Counter(issue.get("rule") for issue in issues).most_common(
                args.top,
            ),
            "top_files": Counter(issue_path(issue) for issue in issues).most_common(
                args.top,
            ),
            "risk": sorted(
                risk_issues,
                key=issue_sort_key,
            )[: args.top],
        },
        "new_code": {
            "total": len(new_issues),
            "by_type": Counter(issue.get("type") for issue in new_issues),
            "by_severity": Counter(issue.get("severity") for issue in new_issues),
            "top_rules": Counter(issue.get("rule") for issue in new_issues).most_common(
                args.top,
            ),
            "top_files": Counter(issue_path(issue) for issue in new_issues).most_common(
                args.top,
            ),
            "issues": sorted(
                new_issues,
                key=lambda issue: (issue_path(issue), issue.get("line") or 0),
            )[: args.top],
        },
        "hotspots": {
            "total": len(hotspots),
            "by_status": Counter(hotspot.get("status") for hotspot in hotspots),
            "items": hotspots[: args.top],
        },
    }


def counter_to_dict(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): value for key, value in counter.items() if key is not None}


def json_safe(value: Any) -> Any:  # noqa: ANN401
    if isinstance(value, Counter):
        return counter_to_dict(value)
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    return value


def render_markdown(report: dict[str, Any]) -> str:  # noqa: PLR0915
    lines: list[str] = []
    project = report["project"]
    latest = report["analyses"][0] if report["analyses"] else {}
    measures = report["measures"]
    project_name = project.get("name", project.get("key", "project"))
    duplication = measures.get("duplicated_lines_density", "unknown")

    lines.append(f"# SonarQube Report: {project_name}")
    lines.append("")
    lines.append(f"- Project key: `{project.get('key')}`")
    lines.append(f"- Branch: `{report['branch']}`")
    lines.append(f"- Latest analysis: `{latest.get('date', 'unknown')}`")
    lines.append(f"- Quality gate: `{report['quality_gate'].get('status', 'unknown')}`")
    lines.append(f"- NCLOC: `{measures.get('ncloc', 'unknown')}`")
    lines.append(f"- Duplication: `{duplication}%`")
    lines.append("")

    issues = report["issues"]
    lines.append("## Unresolved Issues")
    lines.append(f"- Total: `{issues['total']}`")
    lines.append(f"- By type: `{counter_to_dict(issues['by_type'])}`")
    lines.append(f"- By severity: `{counter_to_dict(issues['by_severity'])}`")
    lines.append("")

    lines.append("## Highest-Risk Issues")
    if issues["risk"]:
        for issue in issues["risk"]:
            path = issue_path(issue)
            line = issue.get("line")
            location = f"{path}:{line}" if line else path
            impact = first_impact(issue)
            impact_quality = impact.get("softwareQuality", "n/a")
            impact_severity = impact.get("severity", "n/a")
            issue_severity = issue.get("severity")
            issue_type = issue.get("type")
            issue_rule = issue.get("rule")
            lines.append(
                f"- `{issue_severity}` `{issue_type}` `{issue_rule}` "
                f"`{location}` - {issue.get('message')} "
                f"(impact: {impact_quality}/{impact_severity}, "
                f"key: `{issue.get('key')}`)",
            )
    else:
        lines.append("- None in selected issue set.")
    lines.append("")

    new_code = report["new_code"]
    lines.append("## New Code")
    lines.append(f"- Total: `{new_code['total']}`")
    lines.append(f"- By type: `{counter_to_dict(new_code['by_type'])}`")
    lines.append(f"- By severity: `{counter_to_dict(new_code['by_severity'])}`")
    if new_code["issues"]:
        lines.append("- Sample:")
        for issue in new_code["issues"]:
            path = issue_path(issue)
            line = issue.get("line")
            location = f"{path}:{line}" if line else path
            lines.append(
                f"  - `{issue.get('severity')}` `{issue.get('rule')}` "
                f"`{location}` - {issue.get('message')}",
            )
    lines.append("")

    hotspots = report["hotspots"]
    lines.append("## Security Hotspots")
    lines.append(f"- Total: `{hotspots['total']}`")
    lines.append(f"- By status: `{counter_to_dict(hotspots['by_status'])}`")
    for hotspot in hotspots["items"]:
        component = hotspot.get("component") or ""
        path = component.split(":", 1)[1] if ":" in component else component
        line = hotspot.get("line")
        location = f"{path}:{line}" if line else path
        lines.append(
            f"- `{hotspot.get('status')}` `{hotspot.get('vulnerabilityProbability')}` "
            f"`{location}` - {hotspot.get('message')} "
            f"(key: `{hotspot.get('key')}`)",
        )
    lines.append("")

    lines.append("## Top Clusters")
    lines.append("Top rules:")
    for rule, count in issues["top_rules"]:
        lines.append(f"- `{rule}`: {count}")
    lines.append("")
    lines.append("Top files:")
    for path, count in issues["top_files"]:
        lines.append(f"- `{path}`: {count}")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize SonarQube Cloud findings.",
    )
    parser.add_argument("--env", default=".env", help="Path to local env file.")
    parser.add_argument(
        "--project",
        help="Sonar project key. Defaults to SONAR_PROJECT_KEY.",
    )
    parser.add_argument(
        "--branch",
        help="Branch to query. Defaults to SONAR_BRANCH or trunk.",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=12,
        help="Number of detailed rows per section.",
    )
    parser.add_argument(
        "--new-code",
        action="store_true",
        help="Filter the main issue set to new-code issues.",
    )
    parser.add_argument(
        "--bugs",
        action="store_true",
        help="Filter the main issue set to bugs.",
    )
    parser.add_argument(
        "--security",
        action="store_true",
        help="Filter the main issue set to vulnerabilities.",
    )
    args = parser.parse_args()

    report = summarize(args)
    if args.format == "json":
        print(json.dumps(json_safe(report), indent=2))  # noqa: T201
    else:
        print(render_markdown(report))  # noqa: T201


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(0)
