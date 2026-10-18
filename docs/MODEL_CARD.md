# Model card

Purpose: screen and prioritize synthetic benchmark contingencies for human review. LR, RF and GBT use the nine approved predictors only. Historical models use near-default Spark settings. Current parameters are captured from fitted model stages. Sorted scenario IDs are split before joining rows, preserving group exclusivity. Membership may differ from the historical partition layout.

Training, execution, metrics and selected model provenance are captured in generated manifests. Measured results follow below. Earlier 50K experiment threshold policy: maximum validation F1 across 0.05, 0.1, 0.2 through 0.9. Lower threshold breaks ties. This is an experimental policy without a real operator's recall/workload requirement. False negatives are missed modeled violations. The documented original final evaluation followed a configuration freeze. Historical usage caveats remain. See LIMITATIONS.md for physics and external-validity constraints.

## Frozen local 50K model

Three-fold scenario-grouped training search evaluated two GBT configurations. Depth5/maxIter20 won mean PR-AUC 0.91512764 and equals baseline defaults, so no tuning gain is claimed. Validation-only earlier-experiment max-F1 grid selected threshold 0.4. One final evaluation after content/config/data freeze produced test PR-AUC 0.93181144 and ROC-AUC 0.98475007. At the frozen 0.4 threshold: precision 0.87622549, recall 0.84515366, F1 0.86040915. TP715, FP101, FN131, TN6575. Test prevalence was historically inspected. No pristine historical-test claim. No selection was performed afterward. Source guards reject post-freeze tuning/retraining and repeated final evaluation.

The original private target-free20-row batch inference passed. Those data-derived rows are excluded from this snapshot. Ranking is now distributed sort/indexing with bounded partition metadata. Output includes model-content version, timestamp, input hash, threshold and risk rank. This sample demonstrates inference mechanics, not independent generalization.

`selection.json` is retained as the frozen pre-evaluation snapshot. `final_test.json` is the authoritative completed-assessment record. The snapshot test_evaluated=false is not current execution status. The frozen model digest remained unchanged at final audit.

See [Results](RESULTS.md) for the three execution layers and current measurements.

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

## Current frozen policy

The governing 1M policy is pooled top-20% review, not an earlier max-F1 threshold. No threshold or confusion-count report is retained for the future test. See [policy freeze](VALIDATION_POLICY_FREEZE.md).
