from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dqcheck.profile import DatasetProfile
from dqcheck.rules import RuleResult


def build_report(profile: DatasetProfile, rules: list[RuleResult] | None = None) -> dict[str, Any]:
    return {
        "summary": {
            "rows": profile.rows,
            "columns": profile.columns,
            "duplicate_rows": profile.duplicate_rows,
            "duplicate_percent": profile.duplicate_percent,
        },
        "columns": [item.__dict__ for item in profile.column_profiles],
        "rules": [result.to_dict() for result in (rules or [])],
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# dqcheck report",
        "",
        "## Dataset summary",
        "",
        f"- Rows: **{summary['rows']}**",
        f"- Columns: **{summary['columns']}**",
        f"- Duplicate rows: **{summary['duplicate_rows']} ({summary['duplicate_percent']:.2f}%)**",
        "",
        "## Columns",
        "",
        "| Column | Type | Null % | Unique | Outliers |",
        "|---|---:|---:|---:|---:|",
    ]
    for item in report["columns"]:
        outliers = "" if item["outlier_count"] is None else str(item["outlier_count"])
        lines.append(
            f"| {item['name']} | {item['dtype']} | {item['null_percent']:.2f}% | "
            f"{item['unique_count']} | {outliers} |"
        )

    rules = report.get("rules", [])
    if rules:
        lines.extend(["", "## Rule checks", ""])
        for rule in rules:
            icon = "PASS" if rule["passed"] else "FAIL"
            target = f" [{rule['column']}]" if rule.get("column") else ""
            lines.append(f"- **{icon}** `{rule['rule']}`{target}: {rule['message']}")

    return "\n".join(lines) + "\n"


def write_report(report: dict[str, Any], destination: str | Path, fmt: str) -> None:
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "json":
        target.write_text(json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8")
    elif fmt == "markdown":
        target.write_text(render_markdown(report), encoding="utf-8")
    else:
        raise ValueError("Report format must be 'json' or 'markdown'.")
