# Reproducibility scope

ML pipeline reproducibility is supported with authorized canonical data: schema/integrity validation, deterministic grouped splitting, LR/RF/GBT fitting, positive-class evaluation, grouped GBT tuning, validation-only threshold selection, screening budgets and target-free scoring. Inputs are resolved using GRIDGUARD_DATA_DIR or the per-file variables in PRIVATE_DATA_ACCESS.md, outside this repository. No canonical data/model is distributed. Software tests run on artificial fixtures without those inputs. Test fixtures have no claim of physical validity.

Full benchmark regeneration is not supported: the original executable physics-based dataset generator was not recovered. No reconstructed program is represented as the original, and no from-scratch IEEE118-to-CSV regeneration is claimed. This limitation and private-data access do not automatically block a truthful source/docs-only publication.

The original local environment was macOS 26.7.1 x86_64, Python 3.11.5, Java 21.0.1 and Spark 4.0.1. requirements.txt records installed packages. pyproject.toml declares project dependencies. Cross-platform dependency installation is not asserted tested. Historical outputs show different Spark versions. Exact historical 1M membership/environment receipts are incomplete. Full results/discrepancies remain in results and audit.

Follow README commands with authorized external inputs. Missing data produces a clear error before Spark. Defaults write to ignored results/local, preserving archived measurements. Existing frozen experiments must not be overwritten. A local model and authorized scoring input are required for batch inference. Its fixture test needs neither canonical CSV. Scoring inputs are currently local files for streaming SHA-256, while the separate proposed cloud entry supports bounded Spark-side file hashing.

Archived manifest git_commit fields were intentionally redacted. Original private history remains preserved. Earlier runs sometimes had uncommitted governance/reporting edits, so their Git HEAD was never a clean-source guarantee. Historical baseline configs and full local execution logs are retained privately. Current configs implement private environment access and ignored local outputs. New manifests serialize logical data references rather than resolved private paths.

Historical course evidence and earlier local 1M reproduction are preserved separately. Local integration performed no cloud operations.

Current public verification is documented in audit/PUBLICATION_AUDIT.md. No new final-test assessment is performed just to change data-path conventions or add the public guide. GridRail core manual validation has been reported, while saved responses establishing completion of the entire behavioral probe suite are not published. Local tests check only the interface and specification boundaries.

See [Results](RESULTS.md) for the three execution layers and current measurements.

## Scenario-bootstrap implementation

V1 used repeated Spark jobs and exhausted JVM heap. Its 680 partial draws remain debugging evidence only. V2 scored and materialized validation once in Spark, then stopped Spark and moved repeated resampling to NumPy. All rows from each sampled operating scenario inherited the same multiplicity. The completed run contains 1,000 paired scenario-cluster resamples with fixed seed 4152026. No retraining, model selection, threshold tuning or final-test scoring occurred. Full-sample capture and scenario-recall estimates agree with the validation audit within 1e-10. PR-AUC intervals were intentionally omitted because metric equivalence was not established. Intervals do not correct selection optimism or calibration overlap.
