import pandas as pd
from pathlib import Path

REQUIRED_COLUMNS = ["user_id", "date", "steps", "sleep_hours", "screen_time_hours", "deep_work_hours", "exercise_minutes"]


def load_data(filepath: str) -> pd.DataFrame:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    if not path.suffix.lower() == ".csv":
        raise ValueError(f"Expected a CSV file, got: {path.suffix}")

    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        raise ValueError(f"Unable to read CSV file: {e}")

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["user_id", "date"]).reset_index(drop=True)

    return df
