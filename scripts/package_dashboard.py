"""Allowlist-only static deployment ZIP. Never authenticates or deploys."""
import hashlib,json,zipfile
from pathlib import Path
FILES=['index.html','styles.css','app.js','data.json','config.json','starters.json','docs/LIMITATIONS.md','assets/gridrail-ai-banner.svg']
def package(root=Path('.')):
    root=Path(root);base=root/'dashboard/dist';out=root/'dashboard/gridguard-dashboard-deployment.zip';records=[]
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name in FILES:
            p=base/name
            if p.is_symlink() or not p.is_file():raise ValueError('Missing/unsafe deployment input: '+name)
            data=p.read_bytes();info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,data)
            records.append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    result={'files':records,'count':len(records),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'deployed':False,'scope':'Static sanitized UI only; no functions, records, raw cloud evidence, report export, Git history or credentials'}
    (root/'audit/DASHBOARD_BUNDLE_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n');print('Prepared '+str(len(FILES))+'-file static deployment ZIP; no deployment')
if __name__=='__main__':package(Path(__file__).resolve().parents[1])
