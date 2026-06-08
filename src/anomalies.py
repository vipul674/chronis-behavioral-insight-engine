from typing import List
import pandas as pd
import numpy as np

from src.models import AnomalyResult

METRIC_DOMAIN_MAP = {
    "steps": "physical_activity",
    "exercise_minutes": "fitness",
    "sleep_hours": "sleep",
    "screen_time_hours": "digital_behavior",
    "deep_work_hours": "productivity",
}

Z_SCORE_THRESHOLD = 1.5


def _severity_label(z: float) -> str:
    abs_z = abs(z)
    if abs_z >= 3.0:
        return "high"
    elif abs_z >= 2.5:
        return "medium"
    else:
        return "low"


def detect_anomalies(df: pd.DataFrame) -> List[AnomalyResult]:
    results = []
    for user_id in df["user_id"].unique():
        user_df = df[df["user_id"] == user_id].sort_values("date")
        for metric, domain in METRIC_DOMAIN_MAP.items():
            series = user_df[metric].dropna()
            if len(series) < 3:
                continue
            mean = series.mean()
            std = series.std()
            if std == 0:
                continue
            for _, row in user_df.iterrows():
                val = row[metric]
                if pd.isna(val):
                    continue
                z = (val - mean) / std
                if abs(z) >= Z_SCORE_THRESHOLD:
                    severity = _severity_label(z)
                    date_str = row["date"].strftime("%Y-%m-%d") if hasattr(row["date"], "strftime") else str(row["date"])
                    explanation = (
                        f"{metric.replace('_', ' ').title()} on {date_str} was {val}, "
                        f"which is {abs(z):.1f} standard deviations "
                        f"{'above' if z > 0 else 'below'} this user's baseline of {mean:.1f}."
                    )
                    results.append(AnomalyResult(
                        user_id=user_id,
                        date=date_str,
                        metric=metric,
                        domain=domain,
                        observed_value=float(val),
                        baseline_mean=round(float(mean), 2),
                        baseline_std=round(float(std), 2),
                        z_score=round(float(z), 2),
                        severity=severity,
                        explanation=explanation,
                    ))
    return results
