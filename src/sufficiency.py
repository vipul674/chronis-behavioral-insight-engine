from typing import List
import pandas as pd
import numpy as np

from src.models import SufficiencyResult

METRICS = ["steps", "sleep_hours", "screen_time_hours", "deep_work_hours", "exercise_minutes"]
MIN_OBSERVATIONS = 14
MIN_NON_MISSING_RATIO = 0.70
WINDOW_SIZE = 7


def check_sufficiency(df: pd.DataFrame, user_id: str, metric: str) -> SufficiencyResult:
    user_metric = df.loc[df["user_id"] == user_id, metric].dropna()
    total_observations = len(user_metric)
    non_missing_count = total_observations
    non_missing_ratio = non_missing_count / len(df.loc[df["user_id"] == user_id]) if len(df.loc[df["user_id"] == user_id]) > 0 else 0.0
    has_variance = user_metric.std() > 0 if len(user_metric) > 1 else False

    all_values = df.loc[df["user_id"] == user_id, metric]
    early_window = all_values.head(WINDOW_SIZE).dropna()
    recent_window = all_values.tail(WINDOW_SIZE).dropna()
    early_window_count = len(early_window)
    recent_window_count = len(recent_window)

    abstain_reasons: List[str] = []

    if total_observations < MIN_OBSERVATIONS:
        abstain_reasons.append("insufficient_history")
    if non_missing_ratio < MIN_NON_MISSING_RATIO:
        abstain_reasons.append("too_many_missing_values")
    if not has_variance:
        abstain_reasons.append("flat_or_non_variable_metric")
    if early_window_count < WINDOW_SIZE or recent_window_count < WINDOW_SIZE:
        abstain_reasons.append("insufficient_comparison_windows")

    is_sufficient = len(abstain_reasons) == 0

    return SufficiencyResult(
        metric=metric,
        user_id=user_id,
        is_sufficient=is_sufficient,
        total_observations=total_observations,
        non_missing_count=non_missing_count,
        non_missing_ratio=round(non_missing_ratio, 4),
        has_variance=has_variance,
        early_window_count=early_window_count,
        recent_window_count=recent_window_count,
        abstain_reasons=abstain_reasons,
    )


def check_all_sufficiency(df: pd.DataFrame) -> List[SufficiencyResult]:
    results = []
    for user_id in df["user_id"].unique():
        for metric in METRICS:
            results.append(check_sufficiency(df, user_id, metric))
    return results
