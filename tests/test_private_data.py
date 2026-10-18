from pathlib import Path
import pytest
from gridguard.config import load,PROJECT_ROOT

def config(tmp_path):
    p=tmp_path/'config.yaml';p.write_text('data_env: GRIDGUARD_SMALL_DATA\ndata_filename: small.csv\noutput: results/local/test\n');return p

def clear(monkeypatch):
    for k in ['GRIDGUARD_DATA_DIR','GRIDGUARD_SMALL_DATA']:monkeypatch.delenv(k,raising=False)

def test_missing_data_is_clear(tmp_path,monkeypatch):
    clear(monkeypatch)
    with pytest.raises(ValueError,match='Private canonical data unavailable'):load(config(tmp_path))

def test_private_directory_resolution(tmp_path,monkeypatch):
    clear(monkeypatch);data=tmp_path/'small.csv';data.write_text('fixture')
    monkeypatch.setenv('GRIDGUARD_DATA_DIR',str(tmp_path));c=load(config(tmp_path));assert c['data']==str(data);assert c['data_reference']=='private:small.csv'

def test_individual_override_wins(tmp_path,monkeypatch):
    clear(monkeypatch);data=tmp_path/'override.csv';data.write_text('fixture');monkeypatch.setenv('GRIDGUARD_SMALL_DATA',str(data));monkeypatch.setenv('GRIDGUARD_DATA_DIR','unavailable');assert load(config(tmp_path))['data']==str(data)

def test_repository_canonical_path_rejected(tmp_path,monkeypatch):
    clear(monkeypatch);monkeypatch.setenv('GRIDGUARD_SMALL_DATA',str(PROJECT_ROOT/'data/private/small.csv'))
    with pytest.raises(ValueError,match='outside'):load(config(tmp_path))

def test_symlink_into_repository_rejected(tmp_path,monkeypatch):
    clear(monkeypatch);alias=tmp_path/'alias.csv';alias.symlink_to(PROJECT_ROOT/'README.md');monkeypatch.setenv('GRIDGUARD_SMALL_DATA',str(alias))
    with pytest.raises(ValueError,match='outside'):load(config(tmp_path))

def test_scoring_does_not_require_training_data(tmp_path,monkeypatch):
    clear(monkeypatch);assert load(config(tmp_path),require_data=False)['data'] is None


def test_manifest_hides_resolved_data_path(tmp_path):
    import json
    from gridguard.artifacts import manifest
    data=tmp_path/'private-records.csv';data.write_text('test fixture')
    cp=tmp_path/'private-config.yaml';cp.write_text('fixture: true')
    result=manifest(cp,{'data':str(data),'data_reference':'private:small.csv','seed':4152026},{})
    assert str(tmp_path) not in json.dumps(result)
    assert result['data_path']=='private:small.csv'
    assert result['config_path']=='private-config.yaml'
