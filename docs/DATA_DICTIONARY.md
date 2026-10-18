# Data dictionary

| Field | Interpretation |
|---|---|
| `Total_Demand` | Total scenario demand (MW) |
| `Renewable_Generation_Pct` | Scenario renewable generation percentage |
| `Hour_of_Day` | Operating hour (0–23) |
| `Pre_Outage_Line_Loading` | Candidate line loading before outage. Benchmark percentage feature |
| `Line_Thermal_Rating` | Synthetic calibrated line rating (MW), not utility equipment rating |
| `Edge_Betweenness` | Network edge betweenness feature. Exact normalization awaits generator source |
| `Degree_From_Bus` | From-bus graph degree |
| `Degree_To_Bus` | To-bus graph degree |
| `Line_Outage_Sensitivity` | LODF-derived sensitivity summary. Exact construction awaits generator source |
| `Post_Outage_Violation` | Binary modeled thermal violation after outage |
| `scenario_id` | Operating scenario identifier. Grouping only |
| `outage_line_id` | Candidate outage identifier. Traceability only |
| `random_seed` | Generation metadata. Excluded from predictors |
| `dataset_version` | CSV version string. Excluded from predictors |
| `islanding_flag` | Retained-population metadata. All canonical values zero |

See [Results](RESULTS.md) for the three execution layers and current measurements.
