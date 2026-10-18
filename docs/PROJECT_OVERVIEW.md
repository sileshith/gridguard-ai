# GridGuard AI: Project Overview

> **Contingency Screening & Energy-Risk Prioritization**

GridGuard AI is a PySpark contingency-screening workflow that studies a practical decision problem in power-system analytics:

> **When engineering review capacity is limited, which modeled transmission-grid contingencies should be reviewed first?**

The current project evaluates screening and prioritization on a controlled **synthetic IEEE 118-bus DC benchmark**. It is a research prototype, not operational grid-control software, and it does not claim measured utility savings or real-grid safety.

## Current Verified Project State

- **1,000,000** scenario-outage observations
- **5,650** operating scenarios
- **117,193** modeled positive violations
- **11.7193%** positive prevalence
- **9** predictive features
- **3** evaluated Spark ML model families
- Scenario-grouped splitting to reduce within-scenario leakage
- PySpark / Spark ML / Google Cloud Dataproc workflow
- Review-budget evaluation and paired scenario-cluster bootstrap
- Public dashboard, GitHub repository, portfolio case study, and GridRail AI project guide

## Main Decision-Level Result

At a **20% pooled review budget** on the local 1M validation audit:

| Ranking | Modeled violations captured |
|---|---:|
| Gradient-Boosted Trees | **95.1%** |
| Strongest tested simple baseline: Pre-Outage Line Loading | **78.8%** |
| Gain | **+16.3 percentage points** |

The paired scenario-bootstrap interval for the gain is approximately **+15.75 to +16.72 percentage points** across 1,000 resamples.

Important qualification:

> **Intervals do not correct selection optimism or calibration overlap.**

GBT still missed **875 modeled violations** at the 20% pooled review budget. GridGuard is therefore a screening and prioritization workflow, not a safety authority or replacement for engineering contingency analysis.

## Model Validation

Fresh Google Cloud Dataproc validation:

| Model | PR-AUC |
|---|---:|
| Logistic Regression | **0.8555** |
| Random Forest | **0.8683** |
| Gradient-Boosted Trees | **0.9250** |

The separate local 1M validation audit reports GBT PR-AUC of approximately **0.9247**.

These are **validation results**. They are not held-out final-test results.

## Leakage Prevention

Rows are not split independently at random. Operating scenarios are assigned to train, validation, or test first, and all outage rows associated with one scenario remain together.

This prevents outages from the same operating scenario from leaking across partitions.

Scenario IDs, outage IDs, and other metadata fields are excluded from the predictive feature vector.

## Current Business-Relevant Context

Existing validation summaries show:

| Context feature | Non-violation mean | Violation mean |
|---|---:|---:|
| Total demand | 3,759.78 MW | 3,970.41 MW |
| Renewable-generation share | 18.44% | 19.80% |
| Pre-outage loading | 28.24% | 63.54% |

These are descriptive class-conditional comparisons only. They do **not** establish causality, operational stress, economic consequence, or utility savings.

Broader reliability-cost evidence from Berkeley Lab and the U.S. Department of Energy motivates why prioritization can matter economically, but those historical cost estimates are not assigned to GridGuard modeled violations.

## Energy-Business Extension

The next research layer asks:

> **Can a fixed review budget prioritize not only the largest number of modeled violations, but also the cases with the greatest estimated operational or economic consequence?**

Planned work includes:

- demand-decile screening analysis
- renewable-generation segmentation
- missed violations by hour of day
- high-demand / high-loading stress analysis
- CAISO and EIA market context
- wholesale electricity-price analysis
- transmission-congestion context
- estimated consequence proxies
- **Economic Exposure Capture@k**
- Cost-Weighted Recall@k
- external / real-system validation
- AC/security-analysis comparison

These are **upcoming research directions, not current measured results**.

## GridRail AI

GridRail AI is the conversational project guide for GridGuard AI. It has completed core manual validation in a private ASU-managed ChatGPT workspace. Direct GPT sharing is currently limited to users recognized by that workspace. Other visitors may [submit an access request](https://docs.google.com/forms/d/e/1FAIpQLSddC199Z7tKwWrrFcPfUeZEiMqhM-7-hKzAlmLFpLpcesjSRA/viewform) to express interest, but submission does not guarantee access. The private canonical dataset is not exposed. It explains methodology, validation evidence, leakage prevention, review-budget analysis, reproducibility, limitations and future work using sanitized project documentation. Public GPT sharing is disabled by the ASU-managed workspace. External accounts are not currently directly shareable under this policy.

## Reproducibility Boundary

The original executable physics/data generator was not recovered. Therefore:

- full canonical 1M dataset regeneration is not claimed;
- exact sensitivity construction is not independently recoverable from the public artifact set;
- public software checks use synthetic fixtures and sanitized aggregate evidence;
- training/validation reproduction requires separately authorized canonical inputs.

## Public Project Ecosystem

| Resource | Purpose | Link |
|---|---|---|
| **Live Dashboard** | Interactive validation evidence and GridRail entry point | [Open dashboard](https://gridguard-ai.pages.dev) |
| **GitHub** | Code, methodology, reproducibility, results, and limitations | [Open repository](https://github.com/sileshith/gridguard-ai) |
| **Portfolio** | Recruiter-oriented flagship case study | [Open portfolio](https://hirpadata.com) |
| **LinkedIn Walkthrough** | 12-page visual project walkthrough | [View walkthrough](https://lnkd.in/p/gkxwd35u) |
| **Facebook Project Post** | Broader business-oriented project introduction | [View Facebook post](https://www.facebook.com/sileshith/posts/pfbid0xiBU4DaSKEwdF3noXDxwWpjgbG7yMmMPg9rAadoEy7ezXNg6pq6AXcY99JZtXVy5l) |
| **GridRail AI Access** | Workspace-eligible access request or expression of interest | [Request invitation](https://docs.google.com/forms/d/e/1FAIpQLSddC199Z7tKwWrrFcPfUeZEiMqhM-7-hKzAlmLFpLpcesjSRA/viewform) |

## Current Governance

**POLICY FROZEN / FINAL TEST UNEVALUATED**

The held-out 1M final-test population has not been scored. No held-out final-test PR-AUC is currently reported.

### Current Public State

- **GridGuard V4-R2:** live and verified
- **GitHub public release:** verified
- **GridGuard on hirpadata.com:** live as the first featured project
- **LinkedIn walkthrough:** published
- **Facebook project post:** published
- **GridRail AI:** direct access limited to workspace-eligible users, public interest form active
- **Final test:** unevaluated
