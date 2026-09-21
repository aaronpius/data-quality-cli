from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


@dataclass
class RuleResult:
    rule: str
    column: str | None
    passed: bool
    message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_rules(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    if not isinstance(data, dict):
        raise ValueError("Rules file must contain a YAML mapping at the top level.")

    return data


def evaluate_rules(df: pd.DataFrame, config: dict[str, Any]) -> list[RuleResult]:
    results: list[RuleResult] = []

    dataset_rules = config.get("dataset", {}) or {}
    max_duplicate_percent = dataset_rules.get("max_duplicate_percent")
    if max_duplicate_percent is not None:
        actual = (df.duplicated().sum() / len(df) * 100) if len(df) else 0.0
        limit = float(max_duplicate_percent)
        results.append(
            RuleResult(
                rule="max_duplicate_percent",
                column=None,
                passed=actual <= limit,
                message=f"Duplicate rows: {actual:.2f}% (limit {limit:.2f}%)",
            )
        )

    min_rows = dataset_rules.get("min_rows")
    if min_rows is not None:
        minimum_rows = int(min_rows)
        results.append(
            RuleResult(
                rule="min_rows",
                column=None,
                passed=len(df) >= minimum_rows,
                message=f"Rows: {len(df)} (minimum {minimum_rows})",
            )
        )

    columns = config.get("columns", {}) or {}
    for column, rules in columns.items():
        if column not in df.columns:
            results.append(
                RuleResult(
                    rule="column_exists",
                    column=column,
                    passed=False,
                    message=f"Required column '{column}' does not exist.",
                )
            )
            continue

        series = df[column]
        rules = rules or {}

        max_null_percent = rules.get("max_null_percent")
        if max_null_percent is not None:
            actual = (series.isna().sum() / len(df) * 100) if len(df) else 0.0
            limit = float(max_null_percent)
            results.append(
                RuleResult(
                    rule="max_null_percent",
                    column=column,
                    passed=actual <= limit,
                    message=f"Nulls: {actual:.2f}% (limit {limit:.2f}%)",
                )
            )

        if rules.get("unique") is True:
            duplicates = int(series.dropna().duplicated().sum())
            results.append(
                RuleResult(
                    rule="unique",
                    column=column,
                    passed=duplicates == 0,
                    message=f"Duplicate non-null values: {duplicates}",
                )
            )

        allowed_values = rules.get("allowed_values")
        if allowed_values is not None:
            non_null = series.dropna()
            invalid = non_null[~non_null.isin(allowed_values)]
            results.append(
                RuleResult(
                    rule="allowed_values",
                    column=column,
                    passed=invalid.empty,
                    message=f"Invalid values: {int(len(invalid))}",
                )
            )

        minimum = rules.get("min")
        if minimum is not None:
            numeric = pd.to_numeric(series, errors="coerce").dropna()
            actual = numeric.min() if not numeric.empty else None
            passed = actual is not None and actual >= float(minimum)
            results.append(
                RuleResult(
                    rule="min",
                    column=column,
                    passed=passed,
                    message=f"Minimum: {actual} (required >= {minimum})",
                )
            )

        maximum = rules.get("max")
        if maximum is not None:
            numeric = pd.to_numeric(series, errors="coerce").dropna()
            actual = numeric.max() if not numeric.empty else None
            passed = actual is not None and actual <= float(maximum)
            results.append(
                RuleResult(
                    rule="max",
                    column=column,
                    passed=passed,
                    message=f"Maximum: {actual} (required <= {maximum})",
                )
            )

        pattern = rules.get("regex")
        if pattern is not None:
            results.append(_evaluate_regex(column, series, pattern))

    return results


def _evaluate_regex(column: str, series: pd.Series, pattern: Any) -> RuleResult:
    if not isinstance(pattern, str) or pattern == "":
        return RuleResult(
            rule="regex",
            column=column,
            passed=False,
            message="Invalid regular expression: pattern must be a non-empty string.",
        )

    try:
        compiled = re.compile(pattern)
    except re.error as exc:
        return RuleResult(
            rule="regex",
            column=column,
            passed=False,
            message=f"Invalid regular expression: {exc}",
        )

    non_null = series.dropna()
    if len(non_null) == 0:
        return RuleResult(
            rule="regex",
            column=column,
            passed=True,
            message="Invalid values: 0 (nulls ignored)",
        )

    as_text = non_null.astype(str)
    invalid = as_text[~as_text.str.fullmatch(compiled.pattern, na=False)]
    count = int(len(invalid))
    return RuleResult(
        rule="regex",
        column=column,
        passed=count == 0,
        message=f"Invalid values: {count}",
    )
