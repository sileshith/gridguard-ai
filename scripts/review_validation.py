"""Compute validation baselines and scenario metrics. Never evaluates test."""
import argparse
from gridguard.review_runtime import prepare_output, open_validation, write_json
from gridguard.review_analysis import summarize_validation


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default='configs/large.yaml')
    parser.add_argument('--model-dir', help='Existing GBT pipeline directory. No model is fitted here.')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    out = prepare_output(args.output)
    spark, _, val, meta = open_validation(args.config, args.model_dir)
    try:
        result = summarize_validation(val, include_gbt=bool(args.model_dir))
        write_json(out / 'validation_review.json', dict(provenance=meta, **result))
        print('Wrote validation_review.json. No test scoring.')
    finally:
        spark.stop()


if __name__ == '__main__':
    main()
