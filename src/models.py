from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SufficiencyResult:
    metric: str
    user_id: str
    is_sufficient: bool
    total_observations: int
    non_missing_count: int
    non_missing_ratio: float
    has_variance: bool
    early_window_count: int
    recent_window_count: int
    abstain_reasons: List[str] = field(default_factory=list)


@dataclass
class PatternResult:
    user_id: str
    metric: str
    domain: str
    direction: str
    baseline_average: float
    recent_average: float
    absolute_change: float
    percent_change: float
    evidence: str


@dataclass
class AnomalyResult:
    user_id: str
    date: str
    metric: str
    domain: str
    observed_value: float
    baseline_mean: float
    baseline_std: float
    z_score: float
    severity: str
    explanation: str


@dataclass
class InsightResult:
    user_id: str
    domain: str
    metric: str
    insight_type: str
    insight: str
    confidence: float
    evidence: str
    status: str
    reason: str
    supporting_stats: dict = field(default_factory=dict)
