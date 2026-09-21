import pandas as pd

from dqcheck.rules import evaluate_rules


def test_rules_detect_failures():
    df = pd.DataFrame({"id": [1, 1, 2], "status": ["active", "unexpected", "inactive"]})
    config = {
        "dataset": {"min_rows": 2},
        "columns": {
            "id": {"unique": True},
            "status": {"allowed_values": ["active", "inactive"]},
        },
    }

    results = evaluate_rules(df, config)
    assert any(result.rule == "unique" and not result.passed for result in results)
    assert any(result.rule == "allowed_values" and not result.passed for result in results)


def test_regex_passes_matching_values():
    df = pd.DataFrame({"email": ["a@b.com", "c@d.org"]})
    results = evaluate_rules(df, {"columns": {"email": {"regex": r"^[^@]+@[^@]+\.[^@]+$"}}})
    assert any(result.rule == "regex" and result.passed for result in results)


def test_regex_fails_non_matching_values():
    df = pd.DataFrame({"email": ["a@b.com", "not-an-email"]})
    results = evaluate_rules(df, {"columns": {"email": {"regex": r"^[^@]+@[^@]+\.[^@]+$"}}})
    failed = next(result for result in results if result.rule == "regex")
    assert not failed.passed
    assert "Invalid values: 1" in failed.message


def test_regex_ignores_nulls():
    df = pd.DataFrame({"email": ["a@b.com", None]})
    results = evaluate_rules(df, {"columns": {"email": {"regex": r"^[^@]+@[^@]+\.[^@]+$"}}})
    passed = next(result for result in results if result.rule == "regex")
    assert passed.passed
    assert "Invalid values: 0" in passed.message


def test_regex_invalid_pattern_returns_clear_error():
    df = pd.DataFrame({"code": ["CUS-000001"]})
    results = evaluate_rules(df, {"columns": {"code": {"regex": "("}})
    failed = next(result for result in results if result.rule == "regex")
    assert not failed.passed
    assert failed.message.startswith("Invalid regular expression:")
