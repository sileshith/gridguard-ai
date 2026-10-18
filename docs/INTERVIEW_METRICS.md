# Interview metrics

## Local 1M validation gains

On the local 1M validation split, GBT increased modeled-violation capture at a 20% review budget from 78.8% for the strongest tested simple baseline to 95.1%, a gain of 16.3 percentage points. At 10% review, capture increased from 54.3% to 78.9%, a gain of 24.6 points. Mean per-scenario recall at a 20% budget increased from 79.4% to 93.8%.

These are validation results on a synthetic IEEE 118-bus DC benchmark, not real-grid operational benefits. Loading was the strongest of the tested descending single-feature rankings and loading times sensitivity, selected on these validation rows. Comparisons are descriptive and subject to selection optimism. Uncertainty for capture and scenario recall is reported below.

Here, pp means percentage points. PR-AUC gains use the original 0 to 1 scale.

| Decision metric | Loading baseline | GBT | Improvement |
|---|---:|---:|---:|
| PR-AUC | 0.6390 | 0.9247 | +0.2857 |
| Capture at 10% review | 54.33% | 78.92% | +24.59 pp |
| Capture at 20% review | 78.78% | 95.07% | +16.29 pp |
| Mean per-scenario recall at 10% | 54.16% | 80.27% | +26.10 pp |
| Mean per-scenario recall at 20% | 79.39% | 93.80% | +14.41 pp |
| Scenarios with at least one miss at 20% | 92.72% | 44.05% | -48.67 pp |

Pooled capture ranks all 153,105 validation cases together. Per-scenario recall ranks outages within each of the 865 positive validation scenarios and then averages their recalls. These are different review policies. At 20%, 44.05% of scenarios still have at least one miss, versus 92.72% for loading, a reduction of 48.67 percentage points. Pooled GBT still misses 875 modeled violations. At 10%, scenario misses fall from 99.42% to 70.40%, a reduction of 29.02 points. At that budget, GBT reaches 91.44% of the nominal pooled ceiling versus 62.95%, a gain of 28.49 points.

## Talking points

### What improved?

PR-AUC increased from 0.6390 to 0.9247, an absolute gain of 0.2857. This is 28.57 points on a 0 to 100 scale, or 44.7% relative.

### What matters at a fixed review budget?

On the local 1M validation split, GBT increased modeled-violation capture at a 20% review budget from 78.8% for the strongest tested simple baseline to 95.1%, a gain of 16.3 percentage points. At 10% review, capture increased from 54.3% to 78.9%, a gain of 24.6 points. Mean per-scenario recall at a 20% budget increased from 79.4% to 93.8%.

### How close to the ceiling?

At 10% review, GBT reached 91.44% of the nominal pooled capture ceiling.

### Did misses disappear?

No. About 44% of positive scenarios still had a miss at 20% review. Ranking supports triage and does not replace full contingency analysis.

## Relative gains

- PR-AUC: +44.7% relative.
- Capture at 10% review: +45.3% relative.
- Capture at 20% review: +20.7% relative.
- Mean per-scenario recall at 10%: +48.2% relative.
- Mean per-scenario recall at 20%: +18.2% relative.

Absolute gain is GBT minus baseline. Relative gain divides that difference by the baseline. Percentage-point gains multiply differences in proportions by 100.

## Resume bullet

Built a scenario-grouped PySpark contingency-ranking pipeline on 1M synthetic IEEE 118-bus cases, with local validation GBT capture increasing from 78.8% to 95.1% versus the strongest tested simple baseline at a 20% review budget.

## Portfolio sentence

Across 865 validation operating scenarios on a synthetic IEEE 118-bus DC benchmark, the local GBT ranking captured 95.1% of modeled violations within the top 20% of cases, compared with 78.8% for the strongest tested simple baseline.

These are validation results on a synthetic IEEE 118-bus DC benchmark, not real-grid operational benefits. Loading was the strongest of the tested descending single-feature rankings and loading times sensitivity, selected on these validation rows. Comparisons are descriptive and subject to selection optimism. Uncertainty for capture and scenario recall is reported below.

## Evidence

[Full-precision derived comparisons](../results/review_validation_1m/comparison.json) record the aggregate-source checksum and model identity. PR-AUC uses Spark areaUnderPR with 1,000 bins, not average precision. The small repeated-evaluation difference in single-feature PR-AUC does not affect displayed rounding. The fresh Dataproc results remain separate in [Results](RESULTS.md). The final test remains frozen and unevaluated.

## Local validation uncertainty

On 865 validation operating scenarios from the synthetic IEEE 118-bus DC benchmark, GBT increased modeled-violation capture at 20% review from 78.8% to 95.1% versus the strongest tested simple baseline. The gain was 16.3 percentage points. Across 1,000 paired scenario-cluster bootstrap resamples, its 95% percentile interval was 15.75 to 16.72 percentage points.

Here, pp means percentage points. The baseline is pre-outage line loading.

| Decision metric | Loading baseline | GBT | Gain | 95% bootstrap interval for gain |
|---|---:|---:|---:|---:|
| Capture at 10% review | 54.33% | 78.92% | +24.59 pp | +23.23 to +25.96 pp |
| Capture at 20% review | 78.78% | 95.07% | +16.29 pp | +15.75 to +16.72 pp |
| Mean per-scenario recall at 20% | 79.39% | 93.80% | +14.41 pp | +13.85 to +14.97 pp |

At 10% review, the gain was 24.59 percentage points, with a 95% interval of 23.23 to 25.96 points. At 20%, GBT capture had a 95% interval of 94.29% to 95.64%, compared with 78.03% to 79.53% for loading. The bootstrap interval for each reported gain remained entirely above zero within the resampled validation scenarios.

PR-AUC remains 0.9247 for GBT versus 0.6390 for loading, a gain of 0.2857. PR-AUC uncertainty was not reported because the bounded Python bootstrap implementation was not shown to reproduce Spark's areaUnderPR definition exactly.

**Limitation. Intervals do not correct selection optimism or calibration overlap.** The model and validation-selected baseline were fixed. These intervals describe validation ranking on this synthetic benchmark, not real-grid benefits. The held-out 1M test remains unevaluated.


## RF reproducibility

The fresh Dataproc RF PR-AUC falls within the range observed across 15 local seed-and-partition experiments. This is consistent with Random Forest stochastic variability, but the experiment does not isolate partition count as the unique cause. Fixed-threshold precision was not reproduced by the sensitivity study. The original local precision (0.941) and fresh Dataproc precision (0.878) both fall outside the 15-run local range of approximately 0.890 to 0.937. The RF sensitivity study repartitioned and sorted the training input differently from the original local pipeline, so it samples a neighboring layout family rather than reproducing the original reference run exactly. Local PR-AUC ranged from 0.8612 to 0.8777. Historical 1M results with a different split remain context rather than the direct reproduction target.
