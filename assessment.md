# Chronis Internship Program — Round 1 Assessment Submission

## Selected Task

Task A — Behavioral Insight Engine

## What I Built

A system that takes daily behavioral data (steps, sleep, screen time, deep work, exercise) across multiple users and produces two things: trend insights and anomaly alerts. It compares early vs. recent observations to spot direction changes, flags statistical outliers per user, and gives each output a confidence score. When the data is too thin or the change too small, it says so instead of guessing.

## Requirements Checklist

- [x] GitHub repository
- [x] requirements.txt
- [x] Single-command execution
- [x] Worked examples from the supplied dataset
- [x] Test suite for insight generation and anomaly detection
- [x] decisions.md with methodology, assumptions, failure modes
- [x] Evidence-backed insights with confidence scores
- [x] Anomaly detection with severity and explanations
- [x] Evidence sufficiency checks and abstention behavior
- [x] Explainable computation throughout

## How to Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.main --input data/Chronis_TaskA_Synthetic_Behavioral_Data_v2-2.csv --output results
```

Or with default paths:

```bash
python -m src.main
```

## How to Test

```bash
pytest
```

## Dataset

The supplied synthetic behavioral dataset (`Chronis_TaskA_Synthetic_Behavioral_Data_v2-2.csv`). 150 rows, 5 users, 30 days each. Columns: steps, sleep_hours, screen_time_hours, deep_work_hours, exercise_minutes.

## System Design

The pipeline runs in order:

```
CSV Loading → Validation → Sufficiency Checks → Pattern Discovery → Anomaly Detection → Insight Generation → Reporting
```

1. `loader.py` reads the CSV, checks that required columns exist, parses dates, sorts by user and date.

2. `sufficiency.py` checks each user-metric pair. It asks: are there at least 14 observations? Are at least 70% non-missing? Does the metric vary? Are both comparison windows full? If any check fails, it returns an abstention reason.

3. `patterns.py` takes the first 7 and last 7 valid observations for each metric, computes their means, and calculates percent change. Changes of 10% or more get classified as increasing or declining. Below that, it calls it stable and abstains.

4. `anomalies.py` computes a per-user, per-metric z-score for every day. Anything with |z| >= 1.5 gets flagged. Severity: >= 3.0 is high, >= 2.5 is medium, >= 1.5 is low.

5. `insights.py` combines pattern and anomaly results with the sufficiency checks. It emits either a claim (with confidence) or an abstention (confidence 0.0).

6. `reporting.py` writes insights.json, anomalies.json, assessment_summary.json, and summary.md to the output directory.

## Methodology

### Trend Detection

For each user and metric, extract the first 7 and last 7 valid observations. Compute their means. Calculate percent change. Changes of +/- 10% or more count as directional trends. Anything weaker triggers abstention.

### Anomaly Detection

Per-user, per-metric z-scores. Each observation is compared against that user's own mean and standard deviation for that metric. Observations with |z| >= 1.5 are flagged as anomalies.

### Confidence Scoring

Trend claims use this formula:
```
trend_strength = min(abs(percent_change) / 40, 1.0)
confidence = 0.45 + 0.45 * trend_strength * non_missing_ratio
confidence = min(confidence, 0.95)
```

Abstentions always get confidence 0.0.

Anomalies use:
```
confidence = 0.50 + abs(z_score) / 10
confidence = min(confidence, 0.95)
```

### Abstention Policy

The system abstains (status="abstain", confidence=0.0) when:
- Fewer than 14 observations exist
- More than 30% of values are missing
- The metric has zero variance
- Comparison windows are incomplete
- Change magnitude is below the 10% threshold

## Example Output

### Claim Insight

```json
{
  "user_id": "U1",
  "domain": "physical_activity",
  "metric": "steps",
  "insight_type": "trend",
  "insight": "Physical activity declined over the observed period.",
  "confidence": 0.68,
  "evidence": "Average daily steps changed from 8173.8 to 7222.7, a -11.6% change.",
  "status": "claim",
  "reason": "strong_directional_change"
}
```

### Abstention Insight

```json
{
  "user_id": "U1",
  "domain": "sleep",
  "metric": "sleep_hours",
  "insight_type": "trend",
  "insight": "Sleep duration showed no strong directional change over the observed period.",
  "confidence": 0.0,
  "evidence": "Average daily sleep_hours changed from 6.8 to 7.1, a 4.4% change.",
  "status": "abstain",
  "reason": "weak_change_signal"
}
```

### Anomaly Insight

```json
{
  "user_id": "U2",
  "domain": "digital_behavior",
  "metric": "screen_time_hours",
  "insight_type": "anomaly",
  "insight": "Screen time showed a medium-severity spike on 2026-01-29.",
  "confidence": 0.78,
  "evidence": "Screen time on 2026-01-29 was 8.9 hours, which is 2.7 standard deviations above this user's baseline of 5.8 hours.",
  "status": "claim",
  "reason": "statistical_outlier"
}
```

## Why It's Simple on Purpose

The assessment says a simple, well-explained solution is preferred. I took that seriously.

Every insight includes an evidence string showing the exact math. No black-box models, no hidden weights. Same input always gives same output. The system abstains rather than guessing, which is more honest than confident wrong answers. Confidence scores follow a deterministic formula anyone can verify.

## Safety and Refusal Logic

This system does not make medical, psychological, moral, or personality judgments. It:

- Describes measured behavioral patterns only
- Uses neutral language ("the data suggests", "the observed period", "this metric")
- Avoids characterological labels (lazy, unhealthy, addicted, undisciplined, depressed, anxious)
- Validates all generated text against a blocklist of unsafe terms
- Does not compare users to external norms or populations
- Does not offer recommendations or advice

The system describes what the data shows. It does not interpret what that means for the person.

## Files to Review

| File | Purpose |
|------|---------|
| README.md | Project overview, setup, usage |
| decisions.md | Methodology, assumptions, failure modes |
| assessment.md | This file |
| results/summary.md | Human-readable results summary |
| results/insights.json | All generated insights |
| results/anomalies.json | All detected anomalies |
| results/assessment_summary.json | Aggregate statistics |
| tests/ | Test suite for all core logic |
| src/ | Source code for the insight engine |

## Final Note

This repository contains a complete Task A Behavioral Insight Engine with single-command execution, worked results, tests, decisions documentation, evidence sufficiency checks, abstention behavior, and explainable insight generation.
