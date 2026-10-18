import csv
import pytest
from gridguard.features import FEATURES,METADATA,TARGET
from gridguard.evaluation import counts
from gridguard.screening import budget_counts
from gridguard.validation import validate_csv

def test_features():
    assert len(FEATURES)==9
    assert not set(FEATURES)&set(METADATA+[TARGET])
def test_metrics():
    m=counts(2,1,1,4)
    assert m['precision']==pytest.approx(2/3)
    assert m['recall']==pytest.approx(2/3)
    assert m['F1']==pytest.approx(2/3)
def test_screening():
    m=budget_counts(10,4,2,2)
    assert m['capture_rate']==.5 and m['workload_reduction']==.8
@pytest.mark.parametrize('bad',['target','duplicate','null','schema','version'])
def test_invalid_data(tmp_path,bad):
    row={k:'1' for k in FEATURES+METADATA+[TARGET]};row['islanding_flag']='0';row['dataset_version']='ieee118_dc_lodf_v1'
    if bad=='target':row[TARGET]='2'
    if bad=='null':row[FEATURES[0]]=''
    if bad=='schema':del row[FEATURES[0]]
    if bad=='version':row['dataset_version']='unknown'
    f=tmp_path/'input.csv'
    with f.open('w') as h:
        w=csv.DictWriter(h,fieldnames=list(row));w.writeheader();w.writerow(row)
        if bad=='duplicate':w.writerow(row)
    with pytest.raises(ValueError):validate_csv(f)


def test_model_content_digest(tmp_path):
    from gridguard.artifacts import directory_checksum
    p=tmp_path/'model';p.mkdir();(p/'weights').write_text('v1')
    first=directory_checksum(p);assert first==directory_checksum(p)
    (p/'weights').write_text('v2');assert first!=directory_checksum(p)
