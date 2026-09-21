from pathlib import Path

import pytest

from dqcheck.io import UnsupportedFileType, load_dataframe


def test_load_csv(tmp_path: Path):
    path = tmp_path / "sample.csv"
    path.write_text("id,name\n1,A\n2,B\n", encoding="utf-8")
    df = load_dataframe(path)
    assert list(df.columns) == ["id", "name"]
    assert len(df) == 2


def test_unsupported_file_type(tmp_path: Path):
    path = tmp_path / "sample.txt"
    path.write_text("hello", encoding="utf-8")
    with pytest.raises(UnsupportedFileType):
        load_dataframe(path)
