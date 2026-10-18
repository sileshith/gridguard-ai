# Current Work and Energy-Business Roadmap

Local planning draft. No deployment, commit or push is part of this task.

| Current verified work | Upcoming energy-business extension |
|---|---|
| Synthetic IEEE 118-bus benchmark with 1M scenario-outage observations | Recover or independently validate a generator before market-anchored scenario creation |
| Scenario-grouped validation and LR/RF/GBT comparison | Demand, renewable, hour and loading segmentation using validation only |
| PR-AUC, strongest tested simple baseline and review-budget analysis | Prespecified high-demand/high-loading coverage analysis |
| Paired scenario-bootstrap uncertainty | Descriptive scenario-cluster intervals for segment gaps, with sparse-cell reporting |
| GridGuard dashboard and public GitHub | CAISO/EIA price and congestion-context feasibility study |
| GridRail private-workspace core validation and public invitation CTA | No change to workspace access or public GPT availability in this extension |
| Reproducibility audit with unrecovered-generator limitation | Economic consequence proxy and Economic Exposure Capture@k |
| Frozen model and pooled 20% policy | External market realism, AC/security comparison and real-system validation |
| Final test reserved and unevaluated | Single frozen held-out evaluation only after separate explicit written approval |

## Prioritized Milestones

1. **Validation evidence access:** Locate or produce an authenticated validation-only score snapshot from the existing model without fitting. Validate its membership and hashes. Keep private rows outside the repository. Current blocker: no stored row-level validation scores found in inspected locations.
2. **Descriptive segmentation:** Follow the [fixed protocol](ENERGY_BUSINESS_EXTENSION.md), including both unchanged pooled-policy diagnostics and separately labeled within-segment reallocation. Reconcile totals. Export aggregates only. Do not change the frozen policy based on these findings.
3. **Uncertainty and visuals:** Add scenario-cluster intervals where support permits. Prepare demand prevalence, segment capture and missed-hour plots only after their actual joint aggregates exist. Show sparse or undefined cells explicitly.
4. **Market-data pilot:** Choose one bounded CAISO period and market product. Verify report schemas, access, units, time zones, daylight-saving handling, missing intervals, revisions and reuse terms. Keep day-ahead forecasts distinct from real-time observations. Compare with EIA context at matching geographic and temporal resolution.
5. **Separate cohort design:** Select market-anchored semi-synthetic generation or a native real-system contextual study. Do not attach real prices to existing synthetic rows by hour. Establish temporal holdouts and an independent protocol before experiments.
6. **Consequence design:** Define the proxy, assumptions, units, nonnegative weights, negative-price policy and uncertainty. Evaluate Economic Exposure Capture@k against transparent baselines. Make no utility-loss or savings claim without a defensible consequence study.
7. **External validation:** Test AC/security-analysis relevance and real-system applicability with appropriate data and independent review. DC/LODF ranking success alone does not establish transfer.
8. **Publication review:** Review the proposed README and portfolio wording before any public change. Dashboard, website and social publishing require separate authorization. Final-test evaluation also requires separate written approval under the unchanged frozen policy.

See the [business question matrix](ENERGY_BUSINESS_QUESTION_MATRIX.md) and [energy-sector decision relevance](ENERGY_BUSINESS_EXTENSION.md). Existing results remain in [Results](RESULTS.md).

**POLICY FROZEN / FINAL TEST UNEVALUATED**
