import pandas as pd

from dqcheck.profile import profile_dataframe


def test_profile_counts_nulls_and_duplicates():
    df = pd.DataFrame({"id": [1, 2, 2, 2], "name": ["a", "b", "b", None]})
    profile = profile_dataframe(df)

    assert profile.rows == 4
    assert profile.columns == 2
    assert profile.duplicate_rows == 1
    name = next(item for item in profile.column_profiles if item.name == "name")
    assert name.null_count == 1
    assert name.null_percent == 25.0
