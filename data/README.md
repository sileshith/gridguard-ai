# Data availability

The canonical modeling datasets used for GridGuard AI are private, non-public project data and are not distributed in this portfolio repository. Public material includes schema, validation rules, published checksums, aggregate statistics, models' effective parameters, result summaries and reproduction instructions for authorized holders. No company ownership claim is made.

| File | Rows | Positives | SHA-256 |
|---|---:|---:|---|
| cis415_grid_small_50000.csv | 50,000 | 5,732 | `0647a744810f26691d2f46ee176a2d167c1beb1ce88a076be69a69b445226ec9` |
| cis415_grid_big_1000000.csv | 1,000,000 | 117,193 | `66d3e763848cb7fa07867dd83587b1125b53366df6dd1af0dd54b7739e0c8aa6` |

CSV dataset_version is ieee118_dc_lodf_v1. Configure GRIDGUARD_DATA_DIR or GRIDGUARD_SMALL_DATA / GRIDGUARD_BIG_DATA to authorized files outside this repository. Read [private data access](../docs/PRIVATE_DATA_ACCESS.md). Missing or invalid paths fail clearly. The files were found and checksum-verified locally; no manual upload was needed.

Dataset redistribution rights remain unestablished and redistribution is prohibited by this repository's release policy. This uncertainty does not require shipping data and is not a blocker for the independently licensed source/docs-only release. No raw or derived record-level samples are included. Artificial test fixtures exercise software behavior and do not represent physics-derived benchmark records.

The original executable physics-based generator was not recovered. Full CSV regeneration from the IEEE118 source case is not claimed; ML pipeline reproduction from authorized canonical inputs is supported. See [attribution](../docs/ATTRIBUTION.md) for benchmark lineage and the distinction between MATPOWER software and case-file data licensing.
