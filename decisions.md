# Decisions — Chronis Behavioral Insight Engine

## Why Descriptive Statistics Instead of ML

I used descriptive statistics rather than machine learning models. Three reasons drove this:

Explainability. Every insight traces back to a computation on the data. There are no hidden weights or learned parameters. Anyone can verify the output by hand.

Determinism. The same dataset always produces the same output. No randomness, no training variance, no "I ran it twice and got different results."

Simplicity. The assessment says reasoning and clarity matter more than model complexity. A straightforward approach that works is better than a complex one that might work.

## Pattern Discovery

I compare the first 7 observations against the last 7 for each user and metric. The threshold is +/- 10%: above that, I call it increasing or declining. Below that, I call it stable and abstain from a directional claim.

Why 10%? Lower thresholds would flag noise as trends. Higher thresholds would miss real shifts. Ten percent sits in the middle for a 30-day window.

What it misses: monotonic trends that reverse near the end, non-linear patterns, seasonality, and time-of-week effects. It only catches end-to-end change.

## Anomaly Detection

I use per-user, per-metric z-scores with a threshold of 1.5 standard deviations. Each observation is compared against that user's own mean and standard deviation for that metric.

Why z-scores? They are interpretable, require no training, and per-user baselines account for individual differences. A threshold of 1.5 catches observations outside roughly the 7th and 93rd percentiles, which felt right for a 30-day window.

What it misses: gradual drift, contextual anomalies, and cases where a single outlier inflates the standard deviation and masks other outliers. It also assumes roughly normal distributions.

## Confidence Scoring

For trend claims:
```
trend_strength = min(abs(percent_change) / 40, 1.0)
confidence = 0.45 + 0.45 * trend_strength * non_missing_ratio
confidence = min(confidence, 0.95)
```

Abstentions always get 0.0.

For anomalies:
```
confidence = 0.50 + abs(z_score) / 10
confidence = min(confidence, 0.95)
```

Confidence goes up with stronger observed changes and more complete data. The formula is deterministic and auditable.

## Evidence Sufficiency Rules

A metric passes sufficiency only when all of these hold:

1. At least 14 observations for the user-metric pair
2. At least 70% non-missing values relative to the user's total rows
3. Non-zero variance (the metric is not constant)
4. At least 7 values in both the early and recent comparison windows

If any check fails, the system abstains with one of these reasons:
- `insufficient_history`: fewer than 14 observations
- `too_many_missing_values`: non-missing ratio below 70%
- `flat_or_non_variable_metric`: zero standard deviation
- `insufficient_comparison_windows`: one or both windows have fewer than 7 values
- `weak_change_signal`: change magnitude below the 10% threshold

## Assumptions

- The dataset has one row per user per day
- Each metric is a continuous numeric value
- Missing values are NaN or empty cells
- A 30-day window is enough to spot meaningful behavioral trends
- Per-user baselines matter (users have different activity levels)

## Failure Modes

1. Short datasets. If a user has fewer than 14 days, all metrics abstain. This is by design.

2. Volatile data. High variance can make z-score detection less sensitive. The system still catches extreme outliers.

3. Gradual drift. The windowed comparison only sees end-to-end change. A metric that went up then down would look stable.

4. Correlated metrics. The system analyzes each metric independently. It does not detect that increased screen time correlates with decreased sleep, for example.

## Safety and Refusal Logic

This system does not:
- Diagnose medical or psychological conditions
- Make moral judgments about behavior
- Use characterological labels (lazy, unhealthy, addicted, etc.)
- Offer recommendations or advice
- Compare users to external norms or populations

It only describes what the data shows: whether a metric went up, down, or stayed flat, and whether individual observations are statistically unusual for that specific user.

All generated text is validated against a blocklist of unsafe terms. If any unsafe term appears, the system raises an error.

## Domain Mapping

| Metric | Domain |
|--------|--------|
| steps | physical_activity |
| exercise_minutes | fitness |
| sleep_hours | sleep |
| screen_time_hours | digital_behavior |
| deep_work_hours | productivity |
