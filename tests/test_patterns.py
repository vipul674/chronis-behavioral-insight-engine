import pytest
import pandas as pd
from src.patterns import discover_patterns


class TestPatterns:
    def _make_df(self, values):
        return pd.DataFrame({
            "user_id": ["U1"] * len(values),
            "date": pd.date_range("2026-01-01", periods=len(values)),
            "steps": values,
            "sleep_hours": [7.0] * len(values),
            "screen_time_hours": [5.0] * len(values),
            "deep_work_hours": [3.0] * len(values),
            "exercise_minutes": [30.0] * len(values),
        })

    def test_increasing_trend_detected(self):
        values = [100] * 7 + [200] * 7 + [150] * 16
        df = self._make_df(values)
        patterns = discover_patterns(df)
        steps_pattern = next((p for p in patterns if p.metric == "steps"), None)
        assert steps_pattern is not None
        assert steps_pattern.direction == "increasing"
        assert steps_pattern.percent_change > 10

    def test_declining_trend_detected(self):
        values = [200] * 7 + [100] * 7 + [150] * 16
        df = self._make_df(values)
        patterns = discover_patterns(df)
        steps_pattern = next((p for p in patterns if p.metric == "steps"), None)
        assert steps_pattern is not None
        assert steps_pattern.direction == "declining"
        assert steps_pattern.percent_change < -10

    def test_weak_trend_stable(self):
        values = [100] * 7 + [105] * 7 + [100] * 16
        df = self._make_df(values)
        patterns = discover_patterns(df)
        steps_pattern = next((p for p in patterns if p.metric == "steps"), None)
        assert steps_pattern is not None
        assert steps_pattern.direction == "stable_or_weak_change"

    def test_percent_change_calculated_correctly(self):
        values = [100.0] * 7 + [150.0] * 7 + [150.0] * 16
        df = self._make_df(values)
        patterns = discover_patterns(df)
        steps_pattern = next((p for p in patterns if p.metric == "steps"), None)
        assert steps_pattern is not None
        assert steps_pattern.baseline_average == 100.0
        assert steps_pattern.recent_average == 150.0
        assert steps_pattern.percent_change == 50.0

    def test_evidence_string_generated(self):
        values = [100] * 7 + [200] * 7 + [150] * 16
        df = self._make_df(values)
        patterns = discover_patterns(df)
        steps_pattern = next((p for p in patterns if p.metric == "steps"), None)
        assert steps_pattern is not None
        assert "changed from" in steps_pattern.evidence
        assert "% change" in steps_pattern.evidence
