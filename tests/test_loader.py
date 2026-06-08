import pytest
import pandas as pd
from pathlib import Path
from src.loader import load_data, REQUIRED_COLUMNS

DATA_PATH = "data/Chronis_TaskA_Synthetic_Behavioral_Data_v2-2.csv"


class TestLoadData:
    def test_valid_csv_loads(self):
        df = load_data(DATA_PATH)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert "user_id" in df.columns
        assert "date" in df.columns
        assert pd.api.types.is_datetime64_any_dtype(df["date"])

    def test_sorted_by_user_and_date(self):
        df = load_data(DATA_PATH)
        for user_id in df["user_id"].unique():
            user_df = df[df["user_id"] == user_id]
            dates = user_df["date"].tolist()
            assert dates == sorted(dates), f"Dates not sorted for user {user_id}"

    def test_missing_required_column_raises(self, tmp_path):
        bad_csv = tmp_path / "bad.csv"
        bad_csv.write_text("user_id,steps\nU1,1000\n")
        with pytest.raises(ValueError, match="Missing required columns"):
            load_data(str(bad_csv))

    def test_nonexistent_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_data("nonexistent_file.csv")

    def test_required_columns_present(self):
        df = load_data(DATA_PATH)
        for col in REQUIRED_COLUMNS:
            assert col in df.columns, f"Missing column: {col}"
