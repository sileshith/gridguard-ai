# Energy-Business Question Matrix

Local research draft. See the [decision-relevance document](ENERGY_BUSINESS_EXTENSION.md) for sources, current descriptive evidence and the segmentation protocol.

**POLICY FROZEN / FINAL TEST UNEVALUATED**

| Business question | Why it matters | Can current GridGuard answer it? | Evidence/data required | Current or future work |
|---|---|---|---|---|
| 1. Where are modeled violations concentrated across demand conditions? | Locate review pressure | Partly. Positive-class mean demand is higher, but decile prevalence is not established | Validation labels, demand and scenario membership | Current validation analysis pending |
| 2. Does GBT retain its screening advantage during high-demand scenarios? | Assess conditional coverage | Not from stored aggregate summaries | Existing validation scores and frozen selections, demand bins | Current validation analysis pending |
| 3. Does renewable-generation share alter modeled risk concentration? | Describe renewable context | Positive-class mean share is higher. Neither segment concentration nor a causal alteration is established | Validation renewable share, labels and scores | Current validation analysis pending |
| 4. At which hours are missed modeled violations concentrated? | Locate missed-case patterns | Not from available summaries | Hour, labels and frozen selection indicators | Current validation analysis pending |
| 5. Are high-loading scenarios disproportionately represented among violations? | Check loading-based review priorities | Positive rows have higher mean candidate-line loading. A high-loading share is not established | Explicit row-level bands or a prespecified scenario loading summary | Current validation analysis pending |
| 6. Can a fixed 20% review budget retain performance in high-stress conditions? | Assess policy robustness | Pooled performance is known. Stress-subset coverage is unknown | Existing global selections plus the single prespecified stress subset | Current validation analysis pending |
| 7. Are modeled high-risk periods also high-price periods? | Link engineering and market context | No real timestamp mapping or prices in this cohort | New defensible time-context mapping and market prices | Future work |
| 8. Does congestion increase economic consequence? | Distinguish physical constraints and financial exposure | No causal or monetary evidence | Constraint, location, price, consequence and confounding information | Future work |
| 9. Can contingencies be ranked by estimated economic exposure? | Test consequence-aware review | Not currently | Validated consequence weights and their mapping to cases | Future work |
| 10. Can GridGuard optimize violation and economic-risk capture together? | Compare review objectives | Not currently | New cohort, weights, objective trade-offs and independent evaluation | Future work |

No question above licenses final-test evaluation or a revision to the frozen policy. Segment analysis remains descriptive. Existing validation reuse and baseline selection optimism must be disclosed.
