"""Run both existing entry points on synthetic software fixtures, never canonical data."""
import csv
import subprocess
import sys
import tempfile
from pathlib import Path
import yaml
from gridguard.features import FEATURES, METADATA, TARGET
from gridguard.review_runtime import prepare_output


def main():
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', required=True)
    a = p.parse_args()
    out = prepare_output(a.output)
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix='gridguard-fixture-') as directory:
        base = Path(directory)
        data = base/'synthetic_fixture.csv'
        with data.open('w', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=FEATURES+METADATA+[TARGET])
            writer.writeheader()
            for scenario in range(80):
                for outage in range(4):
                    row = {name:float((scenario*(index+2)+outage)%19) for index,name in enumerate(FEATURES)}
                    row.update(scenario_id=scenario, outage_line_id=outage, islanding_flag=0,
                        random_seed=4152026, dataset_version='ieee118_dc_lodf_v1')
                    row[TARGET] = int(row['Pre_Outage_Line_Loading']>11)
                    writer.writerow(row)
        config = base/'fixture.yaml'
        config.write_text(yaml.safe_dump(dict(data=str(data), output=str(out),
            seed=4152026, expected_rows=320, master='local[2]')))
        for script in ['validate_data.py','run_pipeline.py']:
            result = subprocess.run([sys.executable,str(root/'scripts'/script),'--config',str(config)],
                                     cwd=root, capture_output=True, text=True)
            if result.returncode:
                raise RuntimeError('Synthetic '+script+' failed. '+result.stderr[-2000:])
            print('Synthetic '+script+' completed')
    print('Fixture smoke complete. No canonical inputs or held-out scoring.')


if __name__ == '__main__':
    main()
