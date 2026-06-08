import json
from pathlib import Path
from typing import List

from src.models import InsightResult, AnomalyResult


def _dataclass_to_dict(obj) -> dict:
    return {k: v for k, v in obj.__dict__.items()}


def _save_json(data: list, filepath: Path) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)


def save_insights(insights: List[InsightResult], output_dir: str) -> Path:
    path = Path(output_dir) / "insights.json"
    _save_json([_dataclass_to_dict(i) for i in insights], path)
    return path


def save_anomalies(anomalies: List[AnomalyResult], output_dir: str) -> Path:
    path = Path(output_dir) / "anomalies.json"
    _save_json([_dataclass_to_dict(a) for a in anomalies], path)
    return path


def save_assessment_summary(
    insights: List[InsightResult],
    anomalies: List[AnomalyResult],
    output_dir: str,
) -> Path:
    claims = [i for i in insights if i.status == "claim"]
    abstentions = [i for i in insights if i.status == "abstain"]

    summary = {
        "total_insights": len(insights),
        "total_claims": len(claims),
        "total_abstentions": len(abstentions),
        "total_anomalies": len(anomalies),
        "insights_by_domain": {},
        "abstention_reasons": {},
    }

    for i in insights:
        domain = i.domain
        if domain not in summary["insights_by_domain"]:
            summary["insights_by_domain"][domain] = {"claims": 0, "abstentions": 0}
        if i.status == "claim":
            summary["insights_by_domain"][domain]["claims"] += 1
        else:
            summary["insights_by_domain"][domain]["abstentions"] += 1

    for i in abstentions:
        for reason in i.reason.split("; "):
            summary["abstention_reasons"][reason] = summary["abstention_reasons"].get(reason, 0) + 1

    path = Path(output_dir) / "assessment_summary.json"
    _save_json(summary, path)
    return path


def save_summary_md(
    insights: List[InsightResult],
    anomalies: List[AnomalyResult],
    df,
    output_dir: str,
) -> Path:
    claims = [i for i in insights if i.status == "claim"]
    abstentions = [i for i in insights if i.status == "abstain"]

    n_users = df["user_id"].nunique()
    n_rows = len(df)
    metrics_analyzed = ["steps", "sleep_hours", "screen_time_hours", "deep_work_hours", "exercise_minutes"]

    lines = [
        "# Chronis Behavioral Insight Engine — Summary",
        "",
        "## Dataset Overview",
        f"- **Rows**: {n_rows}",
        f"- **Users**: {n_users}",
        f"- **Metrics analyzed**: {', '.join(metrics_analyzed)}",
        "",
        "## Results",
        f"- **Total insights generated**: {len(insights)}",
        f"- **Claims**: {len(claims)}",
        f"- **Abstentions**: {len(abstentions)}",
        f"- **Anomalies detected**: {len(anomalies)}",
        "",
    ]

    example_insights = claims[:5] + abstentions[:5]
    if example_insights:
        lines.append("## Example Insights")
        lines.append("")
        for i, ins in enumerate(example_insights, 1):
            lines.append(f"{i}. **[{ins.status.upper()}]** (confidence: {ins.confidence}) {ins.insight}")
            lines.append(f"   - User: {ins.user_id}, Domain: {ins.domain}")
            lines.append(f"   - Evidence: {ins.evidence}")
            if ins.status == "abstain":
                lines.append(f"   - Reason: {ins.reason}")
            lines.append("")

    example_anomalies = anomalies[:5]
    if example_anomalies:
        lines.append("## Example Anomalies")
        lines.append("")
        for i, a in enumerate(example_anomalies, 1):
            lines.append(f"{i}. **{a.severity.upper()}** — {a.explanation}")
            lines.append(f"   - User: {a.user_id}, z-score: {a.z_score}")
            lines.append("")

    lines.extend([
        "## Abstention Logic",
        "The system abstains from making claims when:",
        "- Fewer than 14 observations exist for a user-metric pair.",
        "- More than 30% of values are missing.",
        "- The metric has zero variance (constant values).",
        "- There are not enough values in both the early and recent comparison windows.",
        "- The observed change is weaker than the 10% threshold.",
        "",
        "Abstentions ensure the system does not over-interpret noisy or sparse data.",
        "",
        "## Safety Note",
        "This system describes observable behavioral patterns in the data only.",
        "It does not diagnose, judge, or characterize individuals.",
    ])

    path = Path(output_dir) / "summary.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(lines))
    return path
