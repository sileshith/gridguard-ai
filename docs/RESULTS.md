# Results

## Evidence hierarchy

The five-layer register below separates the evidence populations and audit extensions.

## Fresh Dataproc run, October 2026

| Model | PR-AUC | Precision at 0.5 | Recall at 0.5 | F1 at 0.5 |
|---|---:|---:|---:|---:|
| LR | 0.85550 | 0.83131 | 0.68758 | 0.75265 |
| RF | 0.86833 | 0.87844 | 0.65669 | 0.75155 |
| GBT | 0.92500 | 0.92598 | 0.78206 | 0.84796 |

GBT ranked highest of these three near-default baselines. At 20% pooled validation review, GBT captured 16,812 of 17,739 positives, or 94.77%, versus 13,974, or 78.78%, for loading alone. It missed 927 positives. Reviewing 20% defines the candidate budget and is not measured labor savings. At this budget the best possible capture is 100%, so GBT reaches 94.77% of that ceiling. The separate local validation audit now provides heuristic and per-scenario comparisons below. Only the fresh 20% budget and thresholds 0.4 and 0.5 are currently exported here. No missing curve points are inferred.

The input has 1,000,000 rows, 117,193 positives and 5,650 scenarios. Train, validation and test contain 696,268, 153,105 and 150,627 rows across 3,934, 865 and 851 scenarios. Pairwise scenario overlap is zero in the recorded split. The fresh test has not been scored.

## Supporting local evidence

At the same nominal 20% pooled review budget, 50K development capture was 95.18% versus 79.47% for loading alone, with 42 positives missed. The exposed earlier 50K test is a separate experiment and is not a pristine confirmatory cohort. Local 1M GBT PR-AUC was 0.92465785. Local 1M RF PR-AUC was 0.87617 versus 0.86833 in the fresh run. The completed RF study is summarized below. Historical 1M used a different validation population and is context, not an exact reproduction target. Equal local and cloud row counts do not alone prove matching per-ID membership.

## Separate execution environments

| Environment | Spark | Python | Java |
|---|---|---|---|
| Local reproduction, recorded | 4.0.1 | 3.11.5 | 21.0.1 |
| Fresh Dataproc run, October 2026 | 4.1.2 | 3.12.13 | 21.0.12.1 |

The fresh run used two two-core executors and a 4g driver. Approximately 152 seconds through manifest writing describes one pipeline configuration, not cluster lifetime or controlled scaling speedup. Version and layout differences do not establish the cause of RF variation.

Machine-readable measurements remain unchanged under results/small, results/big and results/dataproc_1m_manual. New experiments use separate ignored results/local folders. See [Methods](METHODS.md) and [limitations](LIMITATIONS.md).

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

[Full comparisons](INTERVIEW_METRICS.md).

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

## Five-layer evidence register

| Evidence layer | Scope | Boundary |
|---|---|---|
| 50K development | Earlier development and exposed test experiment | Not current confirmatory evidence |
| Historical 1M course evidence | Original reported results with a different validation population | Context rather than direct reproduction target |
| Local 1M validation/reproduction | Recorded local Spark LR, RF and GBT run | Validation only |
| Fresh 1M Dataproc validation/reproduction | Fresh cloud run, October 2026 | Separate runtime evidence, only measured fresh budgets |
| Local 1M validation audit, October 2026 | Same local 1M split and GBT model. Stronger baseline, per-scenario metrics, ceilings, RF study and paired bootstrap | Validation only. Selection optimism remains. Test unused |
