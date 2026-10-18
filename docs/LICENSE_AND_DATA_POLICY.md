# Software licensing and private-data policy

## Software scope

The existing MIT LICENSE applies to the original GridGuard implementation, tests, original documentation and aggregate charts authored for this portfolio, to the extent the project has rights in those works. Its notice is preserved. No upstream MATPOWER code/case tables, instructor-protected material, vendor package source, course documents or private screenshots are bundled. External dependencies retain their own licenses. The project does not relicense them.

## Data scope

The canonical modeling datasets are treated as private, non-public project data and are not distributed in this portfolio repository. The public repository contains the modeling pipeline, schemas, documentation, validation logic, aggregate statistics, result summaries and reproduction instructions for authorized data holders. Data and model artifacts are excluded from the software-license grant and release bundle. Rights to redistribute the benchmark-derived canonical CSVs remain unestablished. This release resolves that uncertainty by **not redistributing** them, not by inventing ownership or permission.

No claim is made that the current datasets are company property. In a company deployment, equivalent controls would treat canonical datasets as proprietary internal data accessible only to authorized users. The current public GridRail guide receives no private-data connection and uses sanitized documentation only.

Published data fingerprints and aggregate metrics are provenance/discussion material, not a record-level dataset or a download service. A private directory and empty environment-variable convention govern authorized local access. Trained models and record-level sample/prediction rows are also excluded unless separately reviewed and approved. Third-party artifacts require their own rights review before any future addition.

## Disclosed limitations

The historical executable physics/data generator is missing. Full canonical CSV regeneration is not claimed. Historical Dataproc execution and current local 1M reproduction are distinct. Neither missing generator nor a second cloud run is required for publishing a truthful source/docs-only portfolio. Publication approval remains a separate user decision.

See [Results](RESULTS.md) for the three execution layers and current measurements.
