"""Resolve authorized data outside the publication tree without serializing its location."""
import os
from pathlib import Path
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def load(path, require_data=True):
    c=yaml.safe_load(Path(path).read_text())
    if not isinstance(c,dict) or 'output' not in c: raise ValueError('Configuration requires an output directory')
    if 'data_env' in c:
        explicit=os.environ.get(c['data_env'],'').strip()
        directory=os.environ.get('GRIDGUARD_DATA_DIR','').strip()
        candidate=explicit or (str(Path(directory)/c['data_filename']) if directory else '')
        if not candidate:
            if require_data: raise ValueError('Private canonical data unavailable. Set GRIDGUARD_DATA_DIR or the configured per-dataset environment variable; keep data outside this repository.')
            c['data']=None
        else:
            data=Path(candidate).expanduser().resolve()
            if data.is_relative_to(PROJECT_ROOT): raise ValueError('Canonical datasets must be outside the publication repository')
            if require_data and not data.is_file(): raise ValueError('Configured private dataset is unavailable; verify authorized local access')
            c['data']=str(data)
        c['data_reference']='private:'+c['data_filename']
    elif 'data' not in c:
        raise ValueError('Configuration requires data_env or an explicit data input')
    else:
        # Explicit data is retained for noncanonical test fixtures, not bundled datasets.
        c['data_reference']='input:'+Path(c['data']).name
    return c
