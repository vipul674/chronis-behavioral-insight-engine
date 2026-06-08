# Chronis Behavioral Insight Engine

Analyzes daily behavioral data (steps, sleep, screen time, deep work, exercise) across multiple users. It spots trends, flags unusual days, and produces confidence-scored insights. When the data is too weak to support a claim, it abstains instead of guessing.

This project is built for Chronis Task A: Behavioral Insight Engine, which requires pattern discovery, anomaly detection, evidence-backed insight generation, evidence sufficiency checks, worked examples, tests, and methodology documentation.

## Demo

```bash
python -m src.main --input data/Chronis_TaskA_Synthetic_Behavioral_Data_v2-2.csv --output results
```

This generates evidence-backed behavioral insights, anomaly reports, abstention cases, and a markdown summary in the `results/` folder.

## Why It Uses Simple Statistics

No machine learning models. Just trend comparison and z-scores. Every insight shows its math. Same input always gives the same output. No hidden weights, no opaque decisions.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python -m src.main --input data/Chronis_TaskA_Synthetic_Behavioral_Data_v2-2.csv --output results
```

Or with defaults:

```bash
python -m src.main
```

## Test

```bash
pytest
```

## Output Files

The `results/` directory after running:

| File | What it contains |
|------|------------------|
| insights.json | All insights (claims and abstentions) |
| anomalies.json | All detected anomalies |
| assessment_summary.json | Counts and domain breakdown |
| summary.md | Human-readable summary with examples |

## How It Works

### Evidence Sufficiency

Before making a claim, the system checks the data:
- At least 14 observations per user-metric pair
- At least 70% non-missing values
- Non-zero variance
- Enough values in both early and recent comparison windows

If any check fails, it abstains with a reason.

### Pattern Discovery

Compares the first 7 observations against the last 7 for each metric:
- +10% or more change is "increasing"
- -10% or more change is "declining"
- Anything else is "stable_or_weak_change" and triggers abstention

### Anomaly Detection

Per-user, per-metric z-scores:
- |z| >= 1.5 is flagged as anomaly
- |z| >= 3.0 is high severity
- 2.5 <= |z| < 3.0 is medium severity
- 1.5 <= |z| < 2.5 is low severity

### Confidence Scoring

- Trend claims: `0.45 + 0.45 * trend_strength * completeness`, capped at 0.95
- Abstentions: always 0.0
- Anomalies: `0.50 + |z| / 10`, capped at 0.95

## Example Output

Claim insight:
> Physical activity declined over the observed period.
> Evidence: Average daily steps changed from 8298.7 to 7426.0, a -10.5% change.
> Confidence: 0.57

Abstention insight:
> Sleep duration data was insufficient to support a directional claim.
> Reason: insufficient_history

Anomaly insight:
> Steps showed a low-severity spike on 2026-01-06.
> Evidence: Steps on 2026-01-06 was 11922, which is 1.5 standard deviations above this user's baseline of 7872.0.

## Safety

This system describes what the data shows. It does not diagnose, judge, or characterize individuals. It avoids language that reads as medical, psychological, or moral assessment.

## Project Structure

```
chronis-behavioral-insight-engine/
├── README.md
├── requirements.txt
├── decisions.md
├── assessment.md
├── data/
│   └── Chronis_TaskA_Synthetic_Behavioral_Data_v2-2.csv
├── results/
│   ├── insights.json
│   ├── anomalies.json
│   ├── summary.md
│   └── assessment_summary.json
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── loader.py
│   ├── models.py
│   ├── sufficiency.py
│   ├── patterns.py
│   ├── anomalies.py
│   ├── insights.py
│   └── reporting.py
└── tests/
    ├── __init__.py
    ├── test_loader.py
    ├── test_sufficiency.py
    ├── test_patterns.py
    ├── test_anomalies.py
    └── test_insights.py
```
