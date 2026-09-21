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
