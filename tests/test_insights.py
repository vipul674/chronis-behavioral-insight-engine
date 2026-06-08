import pytest
import pandas as pd
import numpy as np
from src.models import PatternResult, AnomalyResult
from src.insights import generate_insights, UNSAFE_TERMS


class TestInsights:
    def _make_df(self, user_id, metric, values):
        data = {
            "user_id": [user_id] * len(values),
            "date": pd.date_range("2026-01-01", periods=len(values)),
            metric: values,
        }
        for m in ["steps", "sleep_hours", "screen_time_hours", "deep_work_hours", "exercise_minutes"]:
            if m not in data:
                data[m] = [0.0] * len(values)
        return pd.DataFrame(data)

    def test_claim_generated_for_strong_trend(self):
        values = [100] * 7 + [200] * 7 + [150] * 16
        df = self._make_df("U1", "steps", values)
        pattern = PatternResult(
            user_id="U1", metric="steps", domain="physical_activity",
            direction="increasing", baseline_average=100.0, recent_average=200.0,
            absolute_change=100.0, percent_change=100.0,
            evidence="Test evidence",
        )
        insights = generate_insights(df, [pattern], [])
        claims = [i for i in insights if i.status == "claim"]
        assert len(claims) >= 1
        assert claims[0].confidence > 0

    def test_abstention_generated_for_weak_evidence(self):
        values = [100] * 7 + [102] * 7 + [100] * 16
        df = self._make_df("U1", "steps", values)
        pattern = PatternResult(
            user_id="U1", metric="steps", domain="physical_activity",
            direction="stable_or_weak_change", baseline_average=100.0, recent_average=102.0,
            absolute_change=2.0, percent_change=2.0,
            evidence="Test evidence",
        )
        insights = generate_insights(df, [pattern], [])
        abstentions = [i for i in insights if i.status == "abstain"]
        assert len(abstentions) >= 1

    def test_insight_contains_evidence_and_confidence(self):
        values = [100] * 7 + [200] * 7 + [150] * 16
        df = self._make_df("U1", "steps", values)
        pattern = PatternResult(
            user_id="U1", metric="steps", domain="physical_activity",
            direction="increasing", baseline_average=100.0, recent_average=200.0,
            absolute_change=100.0, percent_change=100.0,
            evidence="Average daily steps changed from 100.0 to 200.0, a 100.0% change.",
        )
        insights = generate_insights(df, [pattern], [])
        for ins in insights:
            assert hasattr(ins, "evidence")
            assert hasattr(ins, "confidence")
            assert isinstance(ins.confidence, float)

    def test_unsafe_terms_not_present(self):
        values = [100] * 7 + [200] * 7 + [150] * 16
        df = self._make_df("U1", "steps", values)
        pattern = PatternResult(
            user_id="U1", metric="steps", domain="physical_activity",
            direction="increasing", baseline_average=100.0, recent_average=200.0,
            absolute_change=100.0, percent_change=100.0,
            evidence="Test evidence",
        )
        insights = generate_insights(df, [pattern], [])
        for ins in insights:
            lower = ins.insight.lower()
            for term in UNSAFE_TERMS:
                assert term not in lower, f"Unsafe term '{term}' found in: {ins.insight}"

    def test_anomaly_insight_generated(self):
        values = [1000] * 28 + [10000]
        df = self._make_df("U1", "steps", values)
        anomaly = AnomalyResult(
            user_id="U1", date="2026-01-29", metric="steps",
            domain="physical_activity", observed_value=10000.0,
            baseline_mean=1000.0, baseline_std=0.0, z_score=10.0,
            severity="high", explanation="Test anomaly",
        )
        insights = generate_insights(df, [], [anomaly])
        anomaly_insights = [i for i in insights if i.insight_type == "anomaly"]
        assert len(anomaly_insights) == 1
        assert anomaly_insights[0].confidence > 0
