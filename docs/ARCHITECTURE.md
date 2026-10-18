# Architecture

```mermaid
flowchart TD
 A[Operating scenarios] --> B[Candidate outages]
 B --> C[Validation]
 C --> D[Nine approved predictors]
 D --> E[Scenario grouped Spark pipelines]
 E --> F[Versioned model and manifest]
 F --> G[Batch scoring]
 G --> H[Risk ranked contingencies]
 H --> I[Threshold or screening budget]
 I --> J[Human engineering review]
```

Implemented source includes input validation, grouped split, fitting, evaluation, provenance and scoring. Execution status is distinct and tracked in audit. PROPOSED production controls: drift monitoring, delayed-label performance monitoring, immutable registry, authenticated job submission, alerting and fallback to engineering review when data checks fail. No production service is deployed.

See [Results](RESULTS.md) for the three execution layers and current measurements.
