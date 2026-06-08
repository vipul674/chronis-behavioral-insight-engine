from typing import List
import pandas as pd

from src.models import PatternResult, AnomalyResult, InsightResult
from src.sufficiency import check_all_sufficiency

DOMAIN_LABELS = {
    "physical_activity": "Physical activity",
    "fitness": "Fitness",
    "sleep": "Sleep duration",
    "digital_behavior": "Screen time",
    "productivity": "Deep work",
}

DIRECTION_MESSAGES = {
    "increasing": "increased over the observed period",
    "declining": "declined over the observed period",
    "stable_or_weak_change": "remained too stable or weakly changed to support a directional claim",
}

UNSAFE_TERMS = [
    "lazy", "unhealthy", "addicted", "undisciplined",
    "depressed", "anxious", "diagnostic", "personality",
    "disorder", "mental", "disease", "illness",
]


def _compute_trend_confidence(percent_change: float, non_missing_ratio: float) -> float:
    trend_strength = min(abs(percent_change) / 40.0, 1.0)
    confidence = 0.45 + 0.45 * trend_strength * non_missing_ratio
    return round(min(confidence, 0.95), 2)


def _compute_anomaly_confidence(z_score: float) -> float:
    confidence = min(0.95, 0.50 + abs(z_score) / 10.0)
    return round(confidence, 2)


def _validate_text(text: str) -> str:
    lower = text.lower()
    for term in UNSAFE_TERMS:
        if term in lower:
            raise ValueError(f"Generated text contains unsafe term: {term}")
    return text


def generate_insights(
    df: pd.DataFrame,
    patterns: List[PatternResult],
    anomalies: List[AnomalyResult],
) -> List[InsightResult]:
    sufficiency_results = check_all_sufficiency(df)
    sufficiency_map = {
        (s.user_id, s.metric): s for s in sufficiency_results
    }

    insights: List[InsightResult] = []

    for p in patterns:
        key = (p.user_id, p.metric)
        suff = sufficiency_map.get(key)

        if suff is None or not suff.is_sufficient:
            reason = "; ".join(suff.abstain_reasons) if suff else "unknown"
            label = DOMAIN_LABELS.get(p.domain, p.domain)
            abstain_text = f"{label} data was insufficient to support a directional claim."
            _validate_text(abstain_text)
            insights.append(InsightResult(
                user_id=p.user_id,
                domain=p.domain,
                metric=p.metric,
                insight_type="trend",
                insight=abstain_text,
                confidence=0.0,
                evidence=p.evidence,
                status="abstain",
                reason=reason,
                supporting_stats={
                    "baseline_average": p.baseline_average,
                    "recent_average": p.recent_average,
                    "percent_change": p.percent_change,
                },
            ))
            continue

        if p.direction == "stable_or_weak_change":
            label = DOMAIN_LABELS.get(p.domain, p.domain)
            abstain_text = f"{label} showed no strong directional change over the observed period."
            _validate_text(abstain_text)
            insights.append(InsightResult(
                user_id=p.user_id,
                domain=p.domain,
                metric=p.metric,
                insight_type="trend",
                insight=abstain_text,
                confidence=0.0,
                evidence=p.evidence,
                status="abstain",
                reason="weak_change_signal",
                supporting_stats={
                    "baseline_average": p.baseline_average,
                    "recent_average": p.recent_average,
                    "percent_change": p.percent_change,
                },
            ))
            continue

        label = DOMAIN_LABELS.get(p.domain, p.domain)
        claim_text = f"{label} {DIRECTION_MESSAGES[p.direction]}."
        _validate_text(claim_text)
        confidence = _compute_trend_confidence(p.percent_change, suff.non_missing_ratio)

        insights.append(InsightResult(
            user_id=p.user_id,
            domain=p.domain,
            metric=p.metric,
            insight_type="trend",
            insight=claim_text,
            confidence=confidence,
            evidence=p.evidence,
            status="claim",
            reason="strong_directional_change",
            supporting_stats={
                "baseline_average": p.baseline_average,
                "recent_average": p.recent_average,
                "percent_change": p.percent_change,
            },
        ))

    for a in anomalies:
        label = DOMAIN_LABELS.get(a.domain, a.domain)
        claim_text = f"{label} showed an unusual {a.severity}-severity spike on {a.date}."
        _validate_text(claim_text)
        confidence = _compute_anomaly_confidence(a.z_score)
        insights.append(InsightResult(
            user_id=a.user_id,
            domain=a.domain,
            metric=a.metric,
            insight_type="anomaly",
            insight=claim_text,
            confidence=confidence,
            evidence=a.explanation,
            status="claim",
            reason="statistical_outlier",
            supporting_stats={
                "observed_value": a.observed_value,
                "baseline_mean": a.baseline_mean,
                "z_score": a.z_score,
            },
        ))

    return insights
