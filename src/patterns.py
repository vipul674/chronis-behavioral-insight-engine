from typing import List
import pandas as pd

from src.models import PatternResult

METRIC_DOMAIN_MAP = {
    "steps": "physical_activity",
    "exercise_minutes": "fitness",
    "sleep_hours": "sleep",
    "screen_time_hours": "digital_behavior",
    "deep_work_hours": "productivity",
}

WINDOW_SIZE = 7
PERCENT_CHANGE_THRESHOLD = 10.0


def _compute_trend(values: pd.Series, window_size: int = WINDOW_SIZE) -> dict:
    clean = values.dropna()
    if len(clean) < 2 * window_size:
        return None

    baseline = clean.head(window_size)
    recent = clean.tail(window_size)

    baseline_avg = round(float(baseline.mean()), 1)
    recent_avg = round(float(recent.mean()), 1)
    abs_change = round(recent_avg - baseline_avg, 1)

    if baseline_avg != 0:
        pct_change = round((abs_change / abs(baseline_avg)) * 100, 1)
    else:
        pct_change = 0.0

    if pct_change >= PERCENT_CHANGE_THRESHOLD:
        direction = "increasing"
    elif pct_change <= -PERCENT_CHANGE_THRESHOLD:
        direction = "declining"
    else:
        direction = "stable_or_weak_change"

    return {
        "baseline_average": baseline_avg,
        "recent_average": recent_avg,
        "absolute_change": abs_change,
        "percent_change": pct_change,
        "direction": direction,
    }


def _format_evidence(metric: str, trend: dict) -> str:
    return (
        f"Average daily {metric} changed from {trend['baseline_average']} "
        f"in the first {WINDOW_SIZE} observations to {trend['recent_average']} "
        f"in the most recent {WINDOW_SIZE} observations, "
        f"a {trend['percent_change']}% change."
    )


def discover_patterns(df: pd.DataFrame) -> List[PatternResult]:
    results = []
    for user_id in df["user_id"].unique():
        user_df = df[df["user_id"] == user_id].sort_values("date")
        for metric, domain in METRIC_DOMAIN_MAP.items():
            trend = _compute_trend(user_df[metric])
            if trend is None:
                continue
            evidence = _format_evidence(metric, trend)
            results.append(PatternResult(
                user_id=user_id,
                metric=metric,
                domain=domain,
                direction=trend["direction"],
                baseline_average=trend["baseline_average"],
                recent_average=trend["recent_average"],
                absolute_change=trend["absolute_change"],
                percent_change=trend["percent_change"],
                evidence=evidence,
            ))
    return results
