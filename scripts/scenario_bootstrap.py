"""Compute paired validation-scenario uncertainty. No fitting or test scoring."""
import argparse
import json
from pathlib import Path
from gridguard.review_runtime import prepare_output, open_validation, write_json
from gridguard.bootstrap_review import bounded_arrays, bootstrap_arrays, verify_points


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', default='configs/large.yaml')
    p.add_argument('--model-dir', required=True)
    p.add_argument('--review-json', required=True)
    p.add_argument('--resamples', type=int, default=1000)
    p.add_argument('--seed', type=int, default=4152026)
    p.add_argument('--output', required=True)
    a = p.parse_args()
    if a.resamples != 1000:
        p.error('The frozen 1M protocol requires exactly 1000 resamples')
    chosen = json.loads(Path(a.review_json).read_text())
    if chosen['strongest_heuristic'] != 'Pre_Outage_Line_Loading':
        raise ValueError('Invalid selected heuristic')
    out = prepare_output(a.output)
    spark, _, val, meta = open_validation(a.config, a.model_dir)
    try:
        if chosen['provenance']['data_sha256'] != meta['data_sha256'] or chosen['provenance']['split_seed'] != meta['split_seed']:
            raise ValueError('Validation input differs from baseline selection')
        if chosen['provenance']['model_content_sha256'] != meta['model_content_sha256']:
            raise ValueError('GBT model differs from baseline evaluation')
        if chosen['strongest_heuristic'] != 'Pre_Outage_Line_Loading':
            raise ValueError('This protocol freezes the loading baseline')
        data, inverse = bounded_arrays(val)
        if len(data) != 153105 or len(set(inverse)) != 865:
            raise ValueError('Expected the verified 1M validation population')
        meta['driver_memory_config'] = spark.sparkContext.getConf().get('spark.driver.memory', 'not explicitly configured')
        meta['jvm_max_heap_bytes'] = int(spark.sparkContext._jvm.java.lang.Runtime.getRuntime().maxMemory())
        # Release the JVM before the 1,000 Python-only draws.
        spark.stop()
        with (out/'resamples.jsonl').open('x') as progress:
            def checkpoint(record):
                progress.write(json.dumps(record, allow_nan=False)+'\n')
                progress.flush()
            result = bootstrap_arrays(data, inverse, a.resamples, a.seed, checkpoint)
        result['point_estimate_check'] = verify_points(result, chosen)
        meta.update(bootstrap_seed=a.seed, resamples=a.resamples, bootstrap_unit='operating scenario')
        write_json(out/'scenario_bootstrap.json', dict(provenance=meta, **result))
        print('Wrote scenario_bootstrap.json. No test scoring.')
    finally:
        spark.stop()


if __name__ == '__main__':
    main()
