# Chronis Behavioral Insight Engine — Summary

## Dataset Overview
- **Rows**: 150
- **Users**: 5
- **Metrics analyzed**: steps, sleep_hours, screen_time_hours, deep_work_hours, exercise_minutes

## Results
- **Total insights generated**: 96
- **Claims**: 84
- **Abstentions**: 12
- **Anomalies detected**: 71

## Example Insights

1. **[CLAIM]** (confidence: 0.57) Physical activity declined over the observed period.
   - User: U1, Domain: physical_activity
   - Evidence: Average daily steps changed from 8298.7 in the first 7 observations to 7426.0 in the most recent 7 observations, a -10.5% change.

2. **[CLAIM]** (confidence: 0.72) Fitness declined over the observed period.
   - User: U1, Domain: fitness
   - Evidence: Average daily exercise_minutes changed from 46.0 in the first 7 observations to 34.9 in the most recent 7 observations, a -24.1% change.

3. **[CLAIM]** (confidence: 0.66) Screen time declined over the observed period.
   - User: U1, Domain: digital_behavior
   - Evidence: Average daily screen_time_hours changed from 7.0 in the first 7 observations to 5.7 in the most recent 7 observations, a -18.6% change.

4. **[CLAIM]** (confidence: 0.9) Fitness increased over the observed period.
   - User: U2, Domain: fitness
   - Evidence: Average daily exercise_minutes changed from 36.6 in the first 7 observations to 55.6 in the most recent 7 observations, a 51.9% change.

5. **[CLAIM]** (confidence: 0.64) Screen time increased over the observed period.
   - User: U2, Domain: digital_behavior
   - Evidence: Average daily screen_time_hours changed from 5.4 in the first 7 observations to 6.3 in the most recent 7 observations, a 16.7% change.

6. **[ABSTAIN]** (confidence: 0.0) Sleep duration showed no strong directional change over the observed period.
   - User: U1, Domain: sleep
   - Evidence: Average daily sleep_hours changed from 6.7 in the first 7 observations to 6.7 in the most recent 7 observations, a 0.0% change.
   - Reason: weak_change_signal

7. **[ABSTAIN]** (confidence: 0.0) Deep work showed no strong directional change over the observed period.
   - User: U1, Domain: productivity
   - Evidence: Average daily deep_work_hours changed from 3.7 in the first 7 observations to 3.5 in the most recent 7 observations, a -5.4% change.
   - Reason: weak_change_signal

8. **[ABSTAIN]** (confidence: 0.0) Physical activity showed no strong directional change over the observed period.
   - User: U2, Domain: physical_activity
   - Evidence: Average daily steps changed from 8933.3 in the first 7 observations to 9402.6 in the most recent 7 observations, a 5.3% change.
   - Reason: weak_change_signal

9. **[ABSTAIN]** (confidence: 0.0) Sleep duration showed no strong directional change over the observed period.
   - User: U2, Domain: sleep
   - Evidence: Average daily sleep_hours changed from 7.5 in the first 7 observations to 7.2 in the most recent 7 observations, a -4.0% change.
   - Reason: weak_change_signal

10. **[ABSTAIN]** (confidence: 0.0) Physical activity showed no strong directional change over the observed period.
   - User: U3, Domain: physical_activity
   - Evidence: Average daily steps changed from 7760.3 in the first 7 observations to 7060.6 in the most recent 7 observations, a -9.0% change.
   - Reason: weak_change_signal

## Example Anomalies

1. **LOW** — Steps on 2026-01-06 was 11922, which is 1.5 standard deviations above this user's baseline of 7872.0.
   - User: U1, z-score: 1.54

2. **LOW** — Exercise Minutes on 2026-01-03 was 83, which is 1.7 standard deviations above this user's baseline of 38.7.
   - User: U1, z-score: 1.66

3. **LOW** — Exercise Minutes on 2026-01-06 was 87, which is 1.8 standard deviations above this user's baseline of 38.7.
   - User: U1, z-score: 1.81

4. **LOW** — Sleep Hours on 2026-01-06 was 5.7, which is 1.5 standard deviations below this user's baseline of 7.1.
   - User: U1, z-score: -1.55

5. **LOW** — Sleep Hours on 2026-01-30 was 5.5, which is 1.8 standard deviations below this user's baseline of 7.1.
   - User: U1, z-score: -1.77

## Abstention Logic
The system abstains from making claims when:
- Fewer than 14 observations exist for a user-metric pair.
- More than 30% of values are missing.
- The metric has zero variance (constant values).
- There are not enough values in both the early and recent comparison windows.
- The observed change is weaker than the 10% threshold.

Abstentions ensure the system does not over-interpret noisy or sparse data.

## Safety Note
This system describes observable behavioral patterns in the data only.
It does not diagnose, judge, or characterize individuals.