import pytest
import pandas as pd
import numpy as np
from src.sufficiency import check_sufficiency


class TestSufficiency:
    def _make_df(self, user_id, metric_values):
        return pd.DataFrame({
            "user_id": [user_id] * len(metric_values),
            "date": pd.date_range("2026-01-01", periods=len(metric_values)),
            "steps": metric_values,
            "sleep_hours": [7.0] * len(metric_values),
            "screen_time_hours": [5.0] * len(metric_values),
            "deep_work_hours": [3.0] * len(metric_values),
            "exercise_minutes": [30.0] * len(metric_values),
        })

    def test_fewer_than_14_observations_abstains(self):
        df = self._make_df("U1", [100] * 10)
        result = check_sufficiency(df, "U1", "steps")
        assert not result.is_sufficient
        assert "insufficient_history" in result.abstain_reasons

    def test_too_many_missing_values_abstains(self):
        values = [float("nan")] * 30
        for i in range(5):
            values[i] = 100.0
        df = self._make_df("U1", values)
        result = check_sufficiency(df, "U1", "steps")
        assert not result.is_sufficient
        assert "too_many_missing_values" in result.abstain_reasons

    def test_zero_variance_abstains(self):
        df = self._make_df("U1", [5.0] * 20)
        result = check_sufficiency(df, "U1", "steps")
        assert not result.is_sufficient
        assert "flat_or_non_variable_metric" in result.abstain_reasons

    def test_valid_data_passes_sufficiency(self):
        np.random.seed(42)
        values = np.random.normal(5000, 1000, 30).tolist()
        df = self._make_df("U1", values)
        result = check_sufficiency(df, "U1", "steps")
        assert result.is_sufficient
        assert len(result.abstain_reasons) == 0
        assert result.total_observations == 30

    def test_non_missing_ratio_calculation(self):
        values = [float("nan")] * 30
        for i in range(25):
            values[i] = 100.0 + i
        df = self._make_df("U1", values)
        result = check_sufficiency(df, "U1", "steps")
        assert result.non_missing_count == 25
