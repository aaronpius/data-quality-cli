from __future__ import annotations

from pathlib import Path

import pandas as pd


class UnsupportedFileType(ValueError):
    pass


def load_dataframe(path: str | Path) -> pd.DataFrame:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"File not found: {source}")

    suffix = source.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(source)
    if suffix in {".xlsx", ".xlsm"}:
        return pd.read_excel(source)
    if suffix == ".json":
        return pd.read_json(source)
    if suffix == ".parquet":
        try:
            return pd.read_parquet(source)
        except ImportError as exc:
            raise RuntimeError(
                "Parquet support requires the optional dependency: pip install 'dqcheck[parquet]'"
            ) from exc

    raise UnsupportedFileType(
        f"Unsupported file type '{suffix}'. Supported: .csv, .xlsx, .xlsm, .json, .parquet"
    )
