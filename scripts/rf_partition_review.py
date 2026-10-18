"""Fit RF on training only. Evaluate a fixed validation split across seeds/partitions."""
import argparse
import json
import time
from pathlib import Path
from gridguard.review_runtime import prepare_output, open_validation, write_json
from gridguard.models import pipeline
from gridguard.evaluation import evaluate


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', default='configs/large.yaml')
    p.add_argument('--output', required=True)
    a = p.parse_args()
    out = prepare_output(a.output)
    spark, train, val, meta = open_validation(a.config)
    root = Path(__file__).resolve().parents[1]
    try:
        runs = []
        for partitions in (2, 4, 8):
            fitted_input = train.repartition(partitions, 'scenario_id', 'outage_line_id').sortWithinPartitions(
                'scenario_id', 'outage_line_id').cache()
            fitted_input.count()
            for seed in range(4152026, 4152031):
                start = time.perf_counter()
                model = pipeline('rf', seed, dict(numTrees=20, maxDepth=5, maxBins=32,
                    featureSubsetStrategy='auto', subsamplingRate=1.0, bootstrap=True)).fit(fitted_input)
                prediction = model.transform(val).cache()
                metrics = evaluate(prediction)
                prediction.unpersist()
                record = dict(partitions=partitions, model_seed=seed, split_seed=meta['split_seed'],
                    elapsed_seconds=time.perf_counter()-start, metrics=metrics,
                    parameters={k.name:v for k,v in model.stages[-1].extractParamMap().items()})
                runs.append(record)
                write_json(out / f'rf_{partitions}_{seed}.json', record)
            fitted_input.unpersist()
        reference = {n:json.loads((root / f'results/{folder}/rf/metrics.json').read_text())
            for n,folder in [('local_1m','big'),('fresh_dataproc','dataproc_1m_manual')]}
        write_json(out / 'rf_partition_review.json', dict(provenance=meta, runs=runs,
            comparison=reference, comparison_scope='Local 1M versus fresh Dataproc. Counts agree but per-scenario identity is not independently established by counts alone.',
            interpretation='Partition and seed sensitivity study. Covering the observed gap does not identify a unique cause.', test_evaluated=False))
        print('Wrote rf_partition_review.json with 15 training/validation runs. No test scoring.')
    finally:
        spark.stop()


if __name__ == '__main__':
    main()
