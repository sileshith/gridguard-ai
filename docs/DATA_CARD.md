# Data card

Synthetic operating scenarios × candidate line outages on the public MATPOWER IEEE 118-bus benchmark. Each label indicates whether a remaining line exceeds its modeled limit after an outage. Historical README describes DC/LODF labeling and fixed limits calibrated on 5,000 scenarios: R_i=max(55,1.03×Q_0.995(|F_i|)+5) MW. This is documented historical methodology, not regenerated physics evidence.

Canonical data: 15 columns, nine numeric predictors, five metadata fields and binary target. See `src/gridguard/features.py` for exact names. Independent CSV validation reproduced 50K/1M row counts, 11.4640%/11.7193% prevalence, finite predictors, binary target, no duplicate scenario-outage pairs, constant dataset version, and retained zero islanding flags. No utility safety inference or financial valuation is supported.

The public portfolio reproduces the ML validation/splitting/modeling/tuning/evaluation/screening/scoring workflows when authorized canonical data are supplied outside the repository. The original executable generator was not recovered. Full CSV regeneration from IEEE118 is not claimed. Canonical data remains private non-public project data with no company ownership assertion. These are disclosed scope limitations, not automatic source/docs publication blockers.

See [Results](RESULTS.md) for the three execution layers and current measurements.

## Evaluation limits

The two files reuse 5,650 operating states, with more outages sampled per state in the larger file. They are not independent scenario cohorts. The documented 5,000-state rating-calibration population has not been matched to those states, so information overlap cannot be excluded. Published candidate rankings allocate a pooled budget across states. Read [Methods](METHODS.md) for the new within-state evaluation and [Limitations](LIMITATIONS.md) for the interpretation boundaries.
