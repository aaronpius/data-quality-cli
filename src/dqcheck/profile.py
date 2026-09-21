from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd


@dataclass
class ColumnProfile:
    name: str
    dtype: str
    rows: int
    non_null: int
    null_count: int
    null_percent: float
    unique_count: int
    unique_percent: float
    min: Any = None
    max: Any = None
    mean: float | None = None
    outlier_count: int | None = None


@dataclass
class DatasetProfile:
    rows: int
    columns: int
    duplicate_rows: int
    duplicate_percent: float
    column_profiles: list[ColumnProfile]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["column_profiles"] = [asdict(item) for item in self.column_profiles]
        return data


def _safe_scalar(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, AttributeError):
            pass
    return value


def _iqr_outliers(series: pd.Series) -> int:
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if len(numeric) < 4:
        return 0
    q1 = numeric.quantile(0.25)
    q3 = numeric.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return 0
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return int(((numeric < lower) | (numeric > upper)).sum())


def profile_dataframe(df: pd.DataFrame) -> DatasetProfile:
    rows = len(df)
    duplicate_rows = int(df.duplicated().sum())
    profiles: list[ColumnProfile] = []

    for name in df.columns:
        series = df[name]
        null_count = int(series.isna().sum())
        non_null = rows - null_count
        unique_count = int(series.nunique(dropna=True))
        is_numeric = pd.api.types.is_numeric_dtype(series)

        profiles.append(
            ColumnProfile(
                name=str(name),
                dtype=str(series.dtype),
                rows=rows,
                non_null=non_null,
                null_count=null_count,
                null_percent=round((null_count / rows * 100) if rows else 0.0, 2),
                unique_count=unique_count,
                unique_percent=round((unique_count / non_null * 100) if non_null else 0.0, 2),
                min=_safe_scalar(series.min()) if non_null and (is_numeric or pd.api.types.is_datetime64_any_dtype(series)) else None,
                max=_safe_scalar(series.max()) if non_null and (is_numeric or pd.api.types.is_datetime64_any_dtype(series)) else None,
                mean=round(float(series.mean()), 4) if non_null and is_numeric else None,
                outlier_count=_iqr_outliers(series) if is_numeric else None,
            )
        )

    return DatasetProfile(
        rows=rows,
        columns=len(df.columns),
        duplicate_rows=duplicate_rows,
        duplicate_percent=round((duplicate_rows / rows * 100) if rows else 0.0, 2),
        column_profiles=profiles,
    )
