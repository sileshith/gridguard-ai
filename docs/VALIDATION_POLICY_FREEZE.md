# Validation policy freeze

State: POLICY FROZEN / FINAL TEST UNEVALUATED

Date: October 17, 2026. This written freeze is authorized by the current project instruction. It does not authorize a test run.

Primary policy: pooled top-20% review. Secondary report: within-scenario top-20% review. Retain pooled and within-scenario 10% as tighter-budget analyses. No max-F1 threshold is retained, so final confusion counts are excluded.

Model: fixed local 1M GBT. Baseline: Pre_Outage_Line_Loading, strongest tested among nine descending features and loading times sensitivity. No sign search. All feature values and model parameters remain fixed.

Code commit: `68bdae2261f78777829c38a804b06f9e28b4416e`. Model content SHA-256: `90930b358852484762cf6b63ee41f3028bb19c03fb7b3a5ed80cf58908e7429a`. Split seed: 4152026. Validation population: 153,105 rows, 17,739 positives, 865 scenarios.

Features: Total_Demand, Renewable_Generation_Pct, Hour_of_Day, Pre_Outage_Line_Loading, Line_Thermal_Rating, Edge_Betweenness, Degree_From_Bus, Degree_To_Bus, Line_Outage_Sensitivity.

Rank descending. Pooled ties use ascending scenario_id then outage_line_id. Within-scenario ties use ascending outage_line_id. Review ceil(N × budget) cases for each policy. Positive-scenario recall excludes zero-positive scenarios. Report both all-scenario and positive-scenario miss-share denominators.

One future test report will contain PR-AUC, secondary ROC-AUC, pooled GBT and loading capture at 10% and 20%, paired capture gains, mean within-scenario recall at 10% and 20%, and scenario shares with at least one missed positive. Both GBT and loading scenario metrics are reported. Spark ranking metrics use rawPrediction and numBins=1000. No threshold search, fitting, model selection or final-test optimization is allowed.

After this freeze, no feature, model, baseline, ranking policy, threshold policy or evaluation metric may be changed based on final-test results.

The [machine-readable record](../configs/validation_policy_freeze_1m.json) binds source, config, canonical-data and model hashes. The final-test entry point requires a separate approval JSON with action APPROVE_ONE_FINAL_TEST_EVALUATION, this policy file's SHA-256, approved_by and approved_at. No approval file is created here. It checks all hashes before Spark starts and reserves an exclusive attempt lock in the single fixed private results directory. A failed attempt requires investigation and does not automatically clear that lock.

Intervals do not correct selection optimism or calibration overlap. The original generator is missing. No utility performance claim follows from this freeze.
