# Focused literature review

APA 7 author-date style. Bibliographic source of truth: [references.bib](../references.bib). Claim mapping: [literature matrix](LITERATURE_MATRIX.csv).

## 1. Scope and review method

Focused narrative review of 16 primary studies and authoritative technical sources. Publisher pages, author repositories, versioned documentation and DOI registration metadata were checked on October 16, 2026 (local date). This is not a systematic review or evidence of exhaustive coverage. No full papers are redistributed. Exact metadata, claim mapping, retrieval links and exceptions are in the literature matrix and audit receipts.

## 2. Power-system contingency analysis

N-1 analysis examines system response after a single element outage. Planning assessments include performance requirements beyond thermal overload. GridGuard ranks modeled line-outage cases for review. It does not certify compliance or operational security ([North American Electric Reliability Corporation [NERC], n.d.](https://www.nerc.com/globalassets/standards/reliability-standards/tpl/tpl-001-5.1.pdf)).

## 3. DC power flow and LODF

The DC formulation simplifies steady-state active-power flows and does not resolve full AC voltage/reactive behavior ([Zimmerman et al., 2011](https://doi.org/10.1109/TPWRS.2010.2051168)). Line-outage distribution factors (LODFs) approximate branch-flow changes in a DC network. MATPOWER documents bridge masking for outages that island a network ([MATPOWER Developers, n.d.-b](https://matpower.org/documentation/ref-manual/legacy/functions/makeLODF.html)). Project reports describe DC/LODF labels, but the missing generator prevents independent verification of their exact construction.

## 4. Benchmark-network context

MATPOWER case118 documents conversion from an IEEE Common Data Format case in the University of Washington archive ([MATPOWER Developers, n.d.-a](https://matpower.org/docs/ref/matpower6.0/case118.html)). This supports benchmark attribution, not a claim that the canonical CSV uses an unmodified case or represents a current utility. Synthetic calibrated thermal ratings require separate validation.

## 5. ML-based security assessment and screening

Learned security classifiers have prior art on other networks and security targets ([Hidalgo-Arteaga et al., 2019](https://doi.org/10.1109/PTC.2019.8810906)). Deliberate sampling of operating regions and security boundaries is central to dataset generation ([Thams et al., 2020](https://doi.org/10.1109/TPWRS.2018.2890769)). GridGuard instead evaluates tabular LR, RF and GBT on a fixed thermal-label benchmark. The studies are context, not directly comparable performance baselines or a novelty claim.

## 6. Imbalanced classification and PR-AUC

Precision-recall analysis emphasizes positive-class retrieval under imbalance ([Saito & Rehmsmeier, 2015](https://doi.org/10.1371/journal.pone.0118432)). GridGuard reports PR-AUC alongside recall, precision, F1 and explicit false negatives. Area under the Spark PR curve is not automatically identical to average precision in other libraries. Validation prevalence is the relevant random-ranking reference, and deployment costs cannot be inferred from F1 alone.

## 7. Leakage-aware grouped validation

Learn-predict separation excludes information unavailable at decision time ([Kaufman et al., 2012](https://doi.org/10.1145/2382577.2382579)). Group-based validation addresses dependence among observations sharing an underlying unit ([Roberts et al., 2017](https://doi.org/10.1111/ecog.02881)). All outages from one operating scenario stay in one partition. Grouping does not remove synthetic sampling bias, shared topology dependence or historical test-set exposure.

## 8. Distributed Spark implementation

RDD lineage and partitioned processing support iterative distributed computation ([Zaharia et al., 2012](https://www.usenix.org/conference/nsdi12/technical-sessions/presentation/zaharia)). Spark pipelines sequence estimators and transformers ([The Apache Software Foundation, n.d.-a](https://spark.apache.org/docs/3.5.8/ml-pipeline.html)). toPandas collects results into driver memory ([The Apache Software Foundation, n.d.-b](https://spark.apache.org/docs/3.5.8/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.toPandas.html)). The current code aggregates in Spark. Documentation version 3.5.8 explains concepts. Reproduced runtime is 4.0.1. Historical refactoring evidence does not establish a controlled speedup.

## 9. Reproducibility and responsible reporting

Dataset documentation should expose composition and intended use ([Gebru et al., 2021](https://doi.org/10.1145/3458723)), while model cards document performance and limitations ([Mitchell et al., 2019](https://doi.org/10.1145/3287560.3287596)). GridGuard distinguishes historical, reproduced, enhanced and proposed evidence, with private input configuration and aggregate-only public artifacts.

## 10. Positioning of GridGuard AI

Random forests aggregate randomized trees ([Breiman, 2001](https://doi.org/10.1023/A:1010933404324)). Gradient boosting iteratively optimizes an additive predictor ([Friedman, 2001](https://doi.org/10.1214/aos/1013203451)). LR is a conventional linear-logit reference, with implementation parameters disclosed. GBT performs best among the fixed evaluated baselines here. This observational result does not explain causally why it wins or establish superiority on unseen grids.

## 11. References

Breiman, L. (2001). Random forests. *Machine Learning, 45*(1), 5–32. [https://doi.org/10.1023/A:1010933404324](https://doi.org/10.1023/A:1010933404324)

Friedman, J. H. (2001). Greedy function approximation: A gradient boosting machine. *The Annals of Statistics, 29*(5), 1189–1232. [https://doi.org/10.1214/aos/1013203451](https://doi.org/10.1214/aos/1013203451)

Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daumé, H., III, & Crawford, K. (2021). Datasheets for datasets. *Communications of the ACM, 64*(12), 86–92. [https://doi.org/10.1145/3458723](https://doi.org/10.1145/3458723)

Hidalgo-Arteaga, J.-M., Hancharou, F., Thams, F., & Chatzivasileiadis, S. (2019). Deep learning for power system security assessment. In *2019 IEEE Milan PowerTech* (pp. 1–6). IEEE. [https://doi.org/10.1109/PTC.2019.8810906](https://doi.org/10.1109/PTC.2019.8810906)

Kaufman, S., Rosset, S., Perlich, C., & Stitelman, O. (2012). Leakage in data mining: Formulation, detection, and avoidance. *ACM Transactions on Knowledge Discovery from Data, 6*(4), Article 15. [https://doi.org/10.1145/2382577.2382579](https://doi.org/10.1145/2382577.2382579)

MATPOWER Developers (n.d.-a). case118: Power flow data for IEEE 118 bus test case. *MATPOWER 6.0 function reference*. [https://matpower.org/docs/ref/matpower6.0/case118.html](https://matpower.org/docs/ref/matpower6.0/case118.html)

MATPOWER Developers (n.d.-b). makeLODF. *MATPOWER 8.1 documentation*. [https://matpower.org/documentation/ref-manual/legacy/functions/makeLODF.html](https://matpower.org/documentation/ref-manual/legacy/functions/makeLODF.html)

Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., Spitzer, E., Raji, I. D., & Gebru, T. (2019). Model cards for model reporting. In *Proceedings of the Conference on Fairness, Accountability, and Transparency* (pp. 220–229). Association for Computing Machinery. [https://doi.org/10.1145/3287560.3287596](https://doi.org/10.1145/3287560.3287596)

North American Electric Reliability Corporation (n.d.). TPL-001-5.1: Transmission system planning performance requirements. *Reliability standard*. [https://www.nerc.com/globalassets/standards/reliability-standards/tpl/tpl-001-5.1.pdf](https://www.nerc.com/globalassets/standards/reliability-standards/tpl/tpl-001-5.1.pdf)

Roberts, D. R., Bahn, V., Ciuti, S., Boyce, M. S., Elith, J., Guillera-Arroita, G., Hauenstein, S., Lahoz-Monfort, J. J., Schröder, B., Thuiller, W., Warton, D. I., Wintle, B. A., Hartig, F., & Dormann, C. F. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography, 40*(8), 913–929. [https://doi.org/10.1111/ecog.02881](https://doi.org/10.1111/ecog.02881)

Saito, T., & Rehmsmeier, M. (2015). The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. *PLOS ONE, 10*(3), Article e0118432. [https://doi.org/10.1371/journal.pone.0118432](https://doi.org/10.1371/journal.pone.0118432)

Thams, F., Venzke, A., Eriksson, R., & Chatzivasileiadis, S. (2020). Efficient database generation for data-driven security assessment of power systems. *IEEE Transactions on Power Systems, 35*(1), 30–41. [https://doi.org/10.1109/TPWRS.2018.2890769](https://doi.org/10.1109/TPWRS.2018.2890769)

The Apache Software Foundation (n.d.-a). ML pipelines. *Apache Spark 3.5.8 documentation*. [https://spark.apache.org/docs/3.5.8/ml-pipeline.html](https://spark.apache.org/docs/3.5.8/ml-pipeline.html)

The Apache Software Foundation (n.d.-b). pyspark.sql.DataFrame.toPandas. *PySpark 3.5.8 documentation*. [https://spark.apache.org/docs/3.5.8/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.toPandas.html](https://spark.apache.org/docs/3.5.8/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.toPandas.html)

Zaharia, M., Chowdhury, M., Das, T., Dave, A., Ma, J., McCauley, M., Franklin, M. J., Shenker, S., & Stoica, I. (2012). Resilient distributed datasets: A fault-tolerant abstraction for in-memory cluster computing. In *9th USENIX Symposium on Networked Systems Design and Implementation (NSDI 12)* (pp. 15–28). USENIX Association. [https://www.usenix.org/conference/nsdi12/technical-sessions/presentation/zaharia](https://www.usenix.org/conference/nsdi12/technical-sessions/presentation/zaharia)

Zimmerman, R. D., Murillo-Sánchez, C. E., & Thomas, R. J. (2011). MATPOWER: Steady-state operations, planning, and analysis tools for power systems research and education. *IEEE Transactions on Power Systems, 26*(1), 12–19. [https://doi.org/10.1109/TPWRS.2010.2051168](https://doi.org/10.1109/TPWRS.2010.2051168)

## Implications for GridGuard AI

Keep scenario-level partitions. Fit preprocessing only within training. Report positive-class retrieval and missed violations at fixed budgets. Bound driver-side outputs. Preserve immutable experiment receipts. Document unknown generator physics. Treat screening as a prioritization aid requiring engineering confirmation. Do not transfer another study’s accuracy, speedup or safety claims.
