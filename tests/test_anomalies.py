import pytest
import pandas as pd
import numpy as np
from src.anomalies import detect_anomalies


class TestAnomalies:
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

    def test_zscore_anomaly_detected(self):
        values = [1000] * 28 + [10000]
        df = self._make_df(values)
        anomalies = detect_anomalies(df)
        steps_anomalies = [a for a in anomalies if a.metric == "steps" and a.user_id == "U1"]
        assert len(steps_anomalies) >= 1
        assert steps_anomalies[-1].observed_value == 10000
        assert steps_anomalies[-1].z_score > 2.0

    def test_normal_point_not_flagged(self):
        values = [100] * 30
        df = self._make_df(values)
        anomalies = detect_anomalies(df)
        steps_anomalies = [a for a in anomalies if a.metric == "steps"]
        assert len(steps_anomalies) == 0

    def test_zero_variance_abstains(self):
        values = [100.0] * 30
        df = self._make_df(values)
        anomalies = detect_anomalies(df)
        steps_anomalies = [a for a in anomalies if a.metric == "steps"]
        assert len(steps_anomalies) == 0

    def test_anomaly_has_severity(self):
        values = [1000] * 28 + [15000]
        df = self._make_df(values)
        anomalies = detect_anomalies(df)
        steps_anomalies = [a for a in anomalies if a.metric == "steps" and a.user_id == "U1"]
        if steps_anomalies:
            assert steps_anomalies[-1].severity in ("low", "medium", "high")

    def test_anomaly_explanation_contains_baseline(self):
        values = [1000] * 28 + [10000]
        df = self._make_df(values)
        anomalies = detect_anomalies(df)
        steps_anomalies = [a for a in anomalies if a.metric == "steps" and a.user_id == "U1"]
        if steps_anomalies:
            assert "baseline" in steps_anomalies[-1].explanation.lower()
