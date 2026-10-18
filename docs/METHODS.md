# Methods

## Introduction

Contingency analysis checks how a power network responds to a candidate outage. Screening ranks candidates for detailed study. The intended reader is an engineer planning a study batch, before any dispatch or operating decision. A missed positive is a modeled violating outage that does not reach detailed review.

## Motivation

DC power flow and LODF calculations can be inexpensive. This study does not show that learning is faster or more accurate than computing its DC labels directly. The synthetic DC/LODF labels form a known-truth testbed for checking a ranking and evaluation workflow before using more expensive targets such as AC, N-k or dynamic studies. Exact physical dataset generation remains unverified because the original generator is missing.

## Problem statement

The unit is one operating scenario paired with one candidate line outage. Nine declared pre-outage features rank outages according to modeled post-outage thermal violations on any remaining line. The current published ranking pools validation cases across scenarios. New evaluation code also measures recall within each scenario at 10% and 20% review. The completed local validation audit reports these results. A loading-times-sensitivity heuristic and the best raw single-feature ranking strengthen the loading-only comparison. They are not substitutes for classical full-network performance indices.

## Data, features and splitting

Both datasets contain the same 5,650 operating scenarios. The 50K dataset samples about 9 outages per scenario and the 1M dataset about 177. More rows therefore mean denser outage coverage, not more independent operating conditions. Scenario IDs are sorted into one partition, then split 70/30 and 50/50 with seed 4152026 before joining rows. Pairwise overlap assertions enforce separation. Equal scenario counts alone do not establish historical per-ID membership.

The nine features include scenario demand, renewable share, hour, line loading, rating, centrality, endpoint degrees and sensitivity. Metadata and labels never enter the feature vector. Hour is a raw numeric input rather than a cyclic encoding. Exact sensitivity construction and pre-contingency availability remain unverified. Ratings were reportedly calibrated on 5,000 scenarios. Overlap with modeled scenarios is unknown and may affect absolute out-of-sample estimates. A common construction does not prove equal effects on every method.

## Models and tuning check

Compare three near-default Spark baselines on the same training and validation partitions. RF uses 20 trees and maximum depth 5. GBT uses 20 iterations and maximum depth 5. This is not a matched tuning-budget comparison. The earlier training-only grouped GBT check compared depths 3 and 5 across three scenario folds and selected the baseline configuration. No tuning gain is claimed.

## Metrics, rankings and operating policy

PR-AUC is Spark areaUnderPR with 1,000 bins unless stated otherwise. It is not average precision. Report positive-class confusion counts separately at a stated threshold. Pooled screening sorts descending by score with scenario and outage IDs as deterministic tie-breaks, reviewing ceil(N * budget) cases. Per-scenario screening uses ceil(n_s * budget) within each scenario. Recall mean and median exclude scenarios with no positives. Miss shares report both all-scenario and positive-scenario denominators.

The requested ceiling is min(1, budget / prevalence). Its share is capture divided by that ceiling. Ceiling annotations also report the realized rounded-budget ceiling because ceil can exceed a small nominal budget. Best single feature means the highest validation PR-AUC among nine raw descending feature scores. It is validation selection and its apparent performance can be optimistic. Bootstrap intervals use paired scenario resampling with the chosen heuristic held fixed and do not correct that selection effect.

Earlier max-F1 thresholds describe earlier experiments only. The written 1M policy freezes pooled top-20% review as primary, within-scenario top-20% as secondary, and 10% as a tighter-budget report. A future test evaluation requires separate written authorization. The fresh test remains untouched. See [results](RESULTS.md) for measured evidence and [reproduction](REPRODUCIBILITY.md) for commands.

At 177 outages per validation scenario, top-20% reviews ceil(177 × 0.2) = 36 outages, or 20.34%. Top-10% reviews 18 outages, or 10.17%. Both methods receive identical rounded capacities.

[Written policy freeze](VALIDATION_POLICY_FREEZE.md).
