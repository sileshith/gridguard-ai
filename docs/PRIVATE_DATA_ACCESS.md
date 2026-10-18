# Private canonical data access

The canonical modeling datasets are private, non-public project data and are not redistributed. They are not described as company-owned. In a hypothetical company deployment, equivalent controls would treat source datasets as proprietary internal data accessible through authorized systems.

Keep files in an authorized directory **outside the publication repository**. Set GRIDGUARD_DATA_DIR in your local shell. The project reads cis415_grid_small_50000.csv and cis415_grid_big_1000000.csv from it. GRIDGUARD_SMALL_DATA and GRIDGUARD_BIG_DATA optionally override individual full-file locations. Do not commit environment values or move files into this repository. .env.example contains empty configuration keys only. No dotenv file is loaded automatically.

```sh
export GRIDGUARD_DATA_DIR="$HOME/private-gridguard-data"
.venv/bin/python scripts/validate_data.py --config configs/development.yaml
.venv/bin/python scripts/run_pipeline.py --config configs/development.yaml
```

The path above is an example for an authorized user's own directory, not a claim that files exist there. This preparation found the canonical datasets locally and verified both checksums. Their actual private location is recorded outside this public tree, without requiring upload. Missing data produces a clear error before Spark starts. Canonical environment paths resolving inside this repository are rejected, including symlinks. Per-dataset overrides take precedence over the directory. Private runtime models and detailed outputs remain ignored under results/local. Aggregate run manifests may also be saved under results/manifests for review. They contain published hashes/metrics and logical input references, not resolved paths or records. Manifests record a logical private filename and data hash, never its resolved filesystem path.

Expected schema/checksums are in data/README.md. Software tests require no private data. Training, tuning, evaluation and batch scoring require authorized inputs and fitted models. No public download service, private-data connector, authentication bypass or dataset-generation replacement is implemented.

See [Results](RESULTS.md) for the three execution layers and current measurements.
