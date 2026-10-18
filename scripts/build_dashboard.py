"""Build canonical dashboard payloads and synchronized static assets from sanitized aggregate artifacts."""
import json,os,shutil
from pathlib import Path
from urllib.parse import urlsplit

def safe_gpt_url(value):
    import re
    if not value:return ''
    try:
        u=urlsplit(value)
        valid=u.scheme=='https' and u.netloc=='chatgpt.com' and not u.query and not u.fragment and re.fullmatch(r'/g/g-[A-Za-z0-9-]+(?:/[A-Za-z0-9-]+)?/?',u.path)
    except ValueError:valid=False
    if not valid:raise ValueError('GRIDRAIL_GPT_URL must be an approved public HTTPS ChatGPT GPT URL without query, fragment or credentials')
    return value

def build(root=Path('.')):
    root=Path(root);dest=root/'dashboard/dist';dest.mkdir(parents=True,exist_ok=True)
    url=safe_gpt_url(os.environ.get('GRIDRAIL_GPT_URL','').strip())
    for name in ['index.html','styles.css','app.js']:shutil.copyfile(root/'dashboard'/name,dest/name)
    shutil.copyfile(root/'dashboard/starters.json',dest/'starters.json')
    (dest/'assets').mkdir(exist_ok=True)
    shutil.copyfile(root/'dashboard/assets/gridrail-ai-banner.svg',dest/'assets/gridrail-ai-banner.svg')
    payload={}
    for size in ['small','big']:
        base=root/'results'/size
        payload[size]={'metrics':{n:json.loads((base/n/'metrics.json').read_text()) for n in ['lr','rf','gbt']},'screening':json.loads((base/'screening.json').read_text()),'note':'50K local reproduction · historical metrics match to four decimals.' if size=='small' else '1M local Spark run · validation population/runtime differ from historical Dataproc results.'}
    base=root/'results/dataproc_1m_manual'
    payload['cloud']={'metrics':{n:json.loads((base/n/'metrics.json').read_text()) for n in ['lr','rf','gbt']},'screening':json.loads((base/'screening.json').read_text()),'note':'Fresh Dataproc run, October 2026. Only the 20% review budget is available. Final test unevaluated. RF PR-AUC falls within local seed and partition variation. Causation is not isolated.'}
    audit=json.loads((root/'results/review_validation_1m/comparison.json').read_text())
    ranks={r['score']:r for r in audit['rankings']}
    payload['review']={'metrics':{'loading':{'PR_AUC':ranks['Pre_Outage_Line_Loading']['PR_AUC']},'gbt':{'PR_AUC':ranks['risk_score']['PR_AUC']}},'screening':ranks['Pre_Outage_Line_Loading']['screening']+ranks['risk_score']['screening'],'comparisons':audit['comparisons'],'note':'Local 1M validation audit: 153,105 cases across 865 scenarios. Synthetic IEEE 118-bus DC benchmark. Policy frozen. Final test unevaluated.'}
    payload['review']['uncertainty']=json.loads((root/'results/review_validation_1m/scenario_bootstrap.json').read_text())
    (root/'dashboard/data.json').write_text(json.dumps(payload,indent=2)+'\n');(root/'dashboard/config.json').write_text(json.dumps({'GRIDRAIL_GPT_URL':url},indent=2)+'\n')
    docs=root/'dashboard/docs';docs.mkdir(exist_ok=True);(docs/'LIMITATIONS.md').write_text((root/'docs/LIMITATIONS.md').read_text().replace('See [Results](RESULTS.md) for the three execution layers and current measurements.','The dashboard keeps development, earlier local, fresh Dataproc and local validation audit results separate.').replace('Stronger heuristic and per-scenario estimates remain pending local execution.','The local validation audit now reports heuristic and within-scenario comparisons. Baseline selection used these validation rows, so comparisons are descriptive and subject to selection optimism.'))
    for name in ['data.json','config.json','docs/LIMITATIONS.md']:
        (dest/name).parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(root/'dashboard'/name,dest/name)
    print('Built dashboard from aggregate results; GPT destination '+('configured' if url else 'unconfigured (honest fallback)'))
if __name__=='__main__':build()
