# GridGuard AI: Energy-Sector Decision Relevance

Local research draft, October 17, 2026. Not published. Existing scientific results and the live dashboard are unchanged.

**POLICY FROZEN / FINAL TEST UNEVALUATED**

## Why Contingency Prioritization Matters

Reliability disruptions can carry substantial economic consequences. LaCommare, Eto, Dunn and Sohn (2018) estimated sustained U.S. power-interruption costs at approximately $44 billion annually in 2015 dollars. This is a historical national estimate, not a current annual forecast or a value per modeled violation. [Berkeley Lab publication](https://eta.lbl.gov/publications/improving-estimated-cost-sustained), DOI: 10.1016/j.energy.2018.04.082.

The U.S.-Canada Power System Outage Task Force's September 2006 implementation report, background section, records estimated U.S. costs of $4 billion to $10 billion for the August 2003 blackout. This describes a particular major event, not the consequences of GridGuard cases. [DOE report](https://www.energy.gov/oe/articles/blackout-2003-blackout-final-implementation-report).

Demand, generation costs and transmission constraints affect wholesale prices. Constraints can produce locational price differences. [EIA price factors](https://www.eia.gov/energyexplained/electricity/prices-and-factors-affecting-prices.php), [EIA transmission and locational prices](https://www.eia.gov/TodayinEnergy/detail.php?id=3150). These sources motivate studying review priorities. They do not establish a GridGuard economic benefit.

Engineering attention and detailed-review capacity are finite. GridGuard examines which modeled cases should enter a limited review queue. **The existing GridGuard experiment measures modeled violation capture, NOT financial savings.** A modeled thermal-limit violation does not establish a blackout, customer interruption, utility loss, congestion payment or interruption cost.

## Evidence Boundaries

| State | Available evidence | Permitted conclusion |
|---|---|---|
| Demonstrated | Synthetic IEEE 118-bus benchmark, grouped validation, existing capture and uncertainty estimates | Descriptive ranking performance on the recorded validation population |
| Current analysis | Reuse of validation class summaries below | Association between class membership and average operating features |
| Pending validation analysis | Demand, renewable, hour, loading and stress segmentation | No segment capture or stress robustness conclusion yet |
| Future market work | New external context and consequence model | No measured economic-risk capture or dollar savings yet |

## Current Validation Context

Source: [recorded validation review](../results/review_validation_1m/validation_review.json). The population contains 153,105 rows, 865 scenarios and 17,739 positives, or approximately 11.5862%. Values below are re-expressed existing aggregates, not a new model run. The source hash and full-precision differences are in [derived context](../results/business_extension/current_evidence.json).

| Feature | Mean for non-violations | Mean for violations | Difference |
|---|---:|---:|---:|
| Total demand, MW | 3,759.78 | 3,970.41 | +210.63 MW |
| Renewable generation share, % | 18.44 | 19.80 | +1.36 percentage points |
| Pre-outage line loading, benchmark % | 28.24 | 63.54 | +35.30 percentage points |

**Observed validation evidence:** Positive rows have higher mean demand, renewable share and pre-outage loading than negative rows. These are class-conditional means, not prevalence by segment. Arithmetic mean hour is not interpreted because hour is circular.

**Business interpretation:** Demand, renewable share and loading are useful candidates for describing where a review policy may need closer examination. Loading is also the strongest tested simple ranking baseline. Feature usefulness for defining a descriptive segment is not a new feature-importance claim.

**What is not yet established:** These differences do not show segment-level GBT advantage, causal renewable effects, real operating stress, or economic consequence. A larger mean loading among positives does not establish the fraction of positives above a chosen loading threshold. Misses by hour cannot be recovered from these summaries.

No stored validation candidate scores were located in the inspected local result folders and private verification area. Existing review scripts write aggregate summaries rather than reusable row-level scores. Full decile and missed-case segmentation was therefore not executed. No private dataset was copied, no model was fitted or transformed, and no test was scored. No segment-performance figure is provided because its required joint information is absent.

## Validation Segmentation Protocol

This is a prespecified descriptive extension. It cannot change the frozen model, baseline, budget or final-test policy. See the [question matrix](ENERGY_BUSINESS_QUESTION_MATRIX.md).

1. Reuse only an authenticated validation-score snapshot matching the recorded data hash, model hash, split seed, 153,105 rows, 865 scenarios and 17,739 positives. Require scenario ID, outage ID, label, the four context fields, GBT score and loading score. Keep rows and identifiers outside the repository. If no snapshot exists, a separately logged validation-only inference run with the existing model is the next prerequisite, not retraining.
2. Verify no duplicate scenario-outage keys and verify all IDs belong to the recorded validation membership. Never use a test partition to choose boundaries. Compute demand and renewable cutpoints over distinct validation scenarios after checking those fields are constant within each scenario. Repeated outage rows must not split one scenario across context bins.
3. Demand: use nine empirical decile cutpoints. Renewables: use three empirical quartile cutpoints. Keep tied values together, record the numeric boundaries, and allow fewer bins if cutpoints coincide. Hour: use 00:00–05:59, 06:00–11:59, 12:00–17:59 and 18:00–23:59 as descriptive six-hour groups. Do not call them observed peak periods. No date or time-zone mapping to a real system exists.
4. Loading: use benchmark bands [0,25), [25,50), [50,75), [75,100] percent. Report out-of-range and missing values separately rather than silently dropping them. Do not equate benchmark loading with verified field equipment stress.
5. Primary segment result: retain each ranking's existing global top ceil(0.20 × 153,105) selection, including frozen tie rules. Within each segment report rows, scenarios, positives, prevalence, selected rows, captured positives, capture, missed positives and GBT-minus-loading capture. This asks where the unchanged pooled policy succeeds or misses. Segment review fractions can differ from 20%.
6. Secondary result, clearly separate: rerank within each segment and allocate ceil(0.20 × segment rows). Report the same fields. This is an alternative descriptive allocation policy, not verification of the frozen pooled policy. Do not mix its results with primary pooled capture.
7. Examine exactly one combined stress subset: demand at or above its validation 90th-percentile scenario cutpoint and candidate loading at least 75%. No additional combination search. Flag segments with fewer than 30 contributing scenarios or 30 positives as sparse and withhold comparative robustness claims. These are reporting rules, not guarantees of statistical power. Report zero-positive recall as undefined.
8. Use Spark group aggregation for private rows. Export aggregate cells only. Validate that segment counts, captured positives and misses reconcile to global totals for every exhaustive segmentation. Never sum overlapping stress subsets. Do not use full-data collect or toPandas. Scenario-cluster uncertainty, if computed, must resample scenarios jointly for both rankings. Label all comparisons descriptive and avoid multiple-testing or causal claims.

## Protected Scientific Reference

Fresh Dataproc validation GBT PR-AUC remains 0.9250. Local validation-audit GBT PR-AUC remains approximately 0.9247. At the pooled 20% review budget, GBT capture remains 95.1%, loading-baseline capture 78.8%, and gain +16.3 percentage points. The paired scenario-bootstrap gain interval remains approximately +15.75 to +16.72 percentage points. **Intervals do not correct selection optimism or calibration overlap.** GBT still missed 875 modeled violations.

The 50K and 1M datasets share 5,650 scenarios. Rating calibration may overlap modeled scenarios. The physics generator was not recovered. Full canonical-data regeneration is not claimed. These limitations also apply to any validation segmentation. See [Results](RESULTS.md), [Methods](METHODS.md) and [Limitations](LIMITATIONS.md).

## Future Electricity-Market Extension

**Path A: market-anchored semi-synthetic scenarios.** Select a documented market, period and demand/renewable context. Generate a new IEEE 118-bus cohort using explicit scaling and dispatch assumptions. Real context supplies scenario inputs, not a real CAISO topology. Recover or independently implement and validate a generator first. Hold out time blocks before choosing models or economic weights. Keep this new cohort separate from the existing frozen study.

**Path B: real-system contextual study.** Analyze public demand, renewable output, prices and constraints within their native regional and temporal scope. This can test contextual associations without a fabricated join to existing synthetic scenarios or a claim of contingency accuracy on real equipment.

**Path C: estimated consequence proxy.** Specify nonnegative case weights with documented units and uncertainty. Load shed × interruption duration × a suitable customer-specific interruption-cost model could be studied only when those inputs exist and are defensibly linked. Price × energy is an exposure proxy, not outage damage. Wholesale prices can be negative, and congestion components can be signed. Do not silently treat signed prices as positive loss weights or double-count customer damage and market payments.

Never attach real prices to the current synthetic rows by hour alone. They have no defensible CAISO date, node or topology mapping. Normalize UTC and local time, daylight-saving transitions, market interval, forecast versus actual status, revision vintage, geography and units. Day-ahead and real-time prices remain distinct. Avoid forward-looking inputs when defining an executable policy.

### Candidate Data and Variables

| Source | Candidate observations | Scope and validation needed |
|---|---|---|
| [CAISO OASIS](https://www.caiso.com/systems-applications/portals-applications/open-access-same-time-information-system-oasis) | Day-ahead and real-time LMP, demand forecasts, transmission outage and capacity status | Verify report availability, access requirements, node identifiers, intervals and revisions before extraction |
| [CAISO prices](https://www.caiso.com/todays-outlook/prices), [demand](https://www.caiso.com/todays-outlook), [supply](https://www.caiso.com/todays-outlook/supply) | Price, demand/net-demand context and renewable production | Inspect downloadable series definitions. Public display does not establish a harmonized historical dataset |
| [EIA Grid Monitor](https://www.eia.gov/electricity/gridmonitor/), [wholesale markets](https://www.eia.gov/electricity/monthly/update/wholesale-markets.php) | Regional grid context and wholesale market summaries | Match reporting geography and frequency. Monthly summaries cannot substitute for nodal interval prices |
| [EIA summer outlook](https://www.eia.gov/outlooks/steo/report/summerElectricity.php) | Forecast and seasonal market context | Version forecasts explicitly. They are not realized hourly outcomes |
| [Berkeley Lab interruption methodology](https://emp.lbl.gov/cost-power-interruptions) | Reliability-cost methods | Applicability depends on customer type, duration and event scope. No direct cost assignment to thermal labels |

Observed external candidates: Wholesale_Price, LMP_Energy_Component, LMP_Congestion_Component, LMP_Loss_Component, System_Demand, Renewable_Output and reported Outage_Derate. Availability and definitions remain to be verified for each selected report. Weather_Stress starts from separately sourced observed weather, then a declared stress rule.

Derived proxies: Net_Demand under a declared renewable subtraction rule, Reserve_Margin_Proxy with a defined capacity denominator, Transmission_Congestion_Flag with a declared component/constraint rule, Peak_Period with a specified tariff or empirical definition, and Customer_Class_Exposure from defensible customer/load information. Net demand may also be a directly reported series, whose definition takes precedence. Estimated_Interruption_Cost is a modeled consequence with assumptions, not an observed loss. Synthetic variables include new dispatch, topology-to-context mappings and simulated contingency outcomes. Do not relabel these as observed CAISO measurements.

### Proposed Economic-Risk Metrics

For risky-case indicator y, review selection s and independently justified nonnegative estimated consequence c, define Economic Exposure Capture@k = sum(y × c × s) / sum(y × c). A zero denominator is undefined. Declare the review-budget denominator, tie rules, market horizon and whether overlapping contingencies are alternatives rather than additive realized losses.

| Metric | Proposed definition or interpretation |
|---|---|
| Cost-Weighted Recall@k | Same ratio when c denotes the selected cost proxy. Avoid presenting it as an independent improvement over the identical exposure metric |
| Risk-Weighted Miss Rate | 1 minus exposure capture, using the same cases and weights |
| Economic Exposure Missed@k | sum(y × c × (1-s)), in declared proxy units, not realized losses |
| Congestion-Weighted Capture@k | Capture with a justified nonnegative congestion-exposure weight. Declare any sign transformation |
| High-Price-Hour Capture@k | Capture among risky cases in a prespecified high-price subset. Report its denominator and prevalence |

All are future metrics, not existing GridGuard measurements. A contingency classifier score is not automatically a calibrated failure probability. Do not multiply it by dollars and call the product expected loss without probability and consequence validation.

## Proposed README Section

Draft only. README is unchanged.

### Why This Matters to the Energy Sector

Reliability disruptions can have substantial economic consequences, while demand and transmission constraints influence electricity-market conditions. [Berkeley Lab](https://eta.lbl.gov/publications/improving-estimated-cost-sustained) and [EIA](https://www.eia.gov/TodayinEnergy/detail.php?id=3150) provide this broader context. GridGuard studies how modeled contingencies can be prioritized under limited review capacity. It measures modeled violation capture and does not estimate event-specific financial savings.

Use a level-two heading when approved for README insertion.

## Proposed Portfolio Copy

### Energy-Sector Relevance

**Business problem:** Detailed grid review competes for limited engineering attention.

**Why prioritization matters:** Reliability disruptions can have economic consequences, and demand and congestion shape market conditions. These motivate careful review priorities, without establishing dollar benefits for GridGuard.

**What GridGuard currently measures:** Violation capture under constrained review budgets on a synthetic IEEE 118-bus validation population.

**What comes next:** Demand and renewable segmentation, followed by a separately designed market-context and estimated-consequence study. Real-world savings and operational validity remain unestablished.

[Technical methodology and reproducibility](https://github.com/sileshith/gridguard-ai) · [Interactive dashboard](https://gridguard-ai.pages.dev)

## Source Verification

The linked LBNL, DOE, EIA and CAISO pages were opened for this task on October 17, 2026. The DOE source is the 2006 implementation report about the 2003 event, not a report published in 2003. Historic monetary estimates retain their original scope and dollar basis where stated. No large external dataset was downloaded. This document is a design and evidence-reuse artifact, not a market-data validation report.
