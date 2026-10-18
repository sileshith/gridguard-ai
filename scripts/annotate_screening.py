"""Derive ceiling context without modifying archived screening measurements."""
import argparse
import json
from pathlib import Path
from gridguard.screening import ceiling_context
from gridguard.review_runtime import prepare_output, write_json


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', required=True)
    a = p.parse_args()
    out = prepare_output(a.output)
    root = Path(__file__).resolve().parents[1]
    records = []
    for group,folder,n,positives in [('50k','small',7651,872),('local_1m','big',153105,17739),
                                    ('fresh_dataproc','dataproc_1m_manual',153105,17739)]:
        rows = json.loads((root / f'results/{folder}/screening.json').read_text())
        for row in rows:
            records.append(dict(evidence=group, **row, **ceiling_context(n, positives,
                row['number_screened'], row['violations_captured'], row['budget'])))
    write_json(out / 'screening_ceiling_annotations.json', dict(records=records,
        note='Derived context only. Archived measurements unchanged. Nominal and realized-budget ceilings are distinct.'))


if __name__ == '__main__':
    main()
