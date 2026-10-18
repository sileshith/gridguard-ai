# Limitations

IEEE 118-bus is a benchmark, not a real utility network. Operating scenarios are synthetic. DC power flow simplifies AC physics. Modeled thermal limits are calibrated synthetic limits, not actual utility ratings. Course report states islanding outages were excluded. Independent CSV validation confirms every retained islanding flag is zero, without proving the generation algorithm. Validation performance does not establish operational utility performance. Predictions are not authoritative grid-security decisions. Human engineering validation is required for real-world use.

Dataset-generation executable source is absent from the supplied package. Label physics cannot currently be reproduced. Historical split membership is not saved and Spark randomSplit depends on partition layout. Deterministic sorted local IDs preserve grouping but may differ from original membership. Historical dependency versions are under review. The previously assessed 50K test has historical prevalence exposure and is not pristine. The fresh 1M test remains unevaluated. Exact batch ranks use distributed sorting and Spark RDD prefix indexing. Partition count metadata is bounded. Sorting and Python worker serialization still incur overhead. Scoring currently expects a local input file for its SHA-256 provenance. Remote storage hashing integration remains proposed.

The public portfolio reproduces the ML validation/splitting/modeling/tuning/evaluation/screening/scoring workflows when authorized canonical data are supplied outside the repository. The original executable generator was not recovered. Full CSV regeneration from IEEE118 is not claimed. Canonical data remains private non-public project data with no company ownership assertion. These are disclosed scope limitations, not automatic source/docs publication blockers.

The dashboard keeps development, earlier local, fresh Dataproc and local validation audit results separate.

## Evaluation limits

The 50K and 1M datasets share the same 5,650 operating scenarios. The 1M dataset adds denser outage coverage rather than independent operating states. Ratings were reportedly calibrated on 5,000 scenarios. Their overlap with modeled scenarios is unknown, so calibration may carry information from validation or test flows. Existing published review rankings pool cases across scenarios and do not enforce equal review capacity within each state. The completed validation audit reports stronger heuristics and within-scenario metrics.

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
