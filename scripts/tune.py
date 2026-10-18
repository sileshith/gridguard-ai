import argparse,json
from pathlib import Path
from pyspark.sql import SparkSession
from gridguard.config import load
from gridguard.splitting import split
from gridguard.tuning import tune
from gridguard.artifacts import save,manifest
from gridguard.models import pipeline
from gridguard.evaluation import evaluate,with_score,threshold_metrics
from gridguard.screening import budgets
p=argparse.ArgumentParser();p.add_argument('--config',required=True);a=p.parse_args();c=load(a.config)
if (Path(c['output'])/'freeze.json').exists(): raise SystemExit('Experiment frozen; no further tuning permitted')
if not (Path(c['output'])/'manifest.json').exists(): raise SystemExit('Historical reproduction must complete before tuning')
s=SparkSession.builder.master(c.get('master','local[2]')).appName('GridGuard-tuning').getOrCreate()
try:
    df=s.read.csv(c['data'],header=True,inferSchema=True);train,val,_=split(df,c['seed']);result=tune(train,c['seed']);out=Path(c['output']);save(out/'tuning.json',result)
    model=pipeline('gbt',c['seed'],result['winner']['parameters']).fit(train);pred=model.transform(val).cache();metrics=evaluate(pred)
    model.write().overwrite().save(str(out/'gbt_tuned/model'));save(out/'gbt_tuned/metrics.json',metrics);save(out/'gbt_tuned/parameters.json',{p.name:v for p,v in model.stages[-1].extractParamMap().items()})
    baseline=json.loads((out/'selection.json').read_text());old=json.loads((out/baseline['model']/'metrics.json').read_text())
    if metrics['PR_AUC']>=old['PR_AUC']:
        scored=with_score(pred);table=[threshold_metrics(scored,t) for t in [.05,.1,.2,.3,.4,.5,.6,.7,.8,.9]];threshold=max(table,key=lambda r:(r['F1'],-r['threshold']))['threshold']
        save(out/'selection.json',dict(model='gbt_tuned',threshold=threshold,rule='train-only grouped PR-AUC search; validation PR-AUC compared to baseline; validation max F1 threshold',test_evaluated=False));save(out/'thresholds_selected.json',table);save(out/'screening_selected.json',budgets(scored)+budgets(scored,'Pre_Outage_Line_Loading'))
    record=manifest(a.config,c,metrics);record['evidence_state']='ENHANCED';record['model']='gbt_tuned';record['hyperparameters']=result['winner']['parameters'];record['tuning']=result;save(Path('results/manifests')/(record['run_id']+'.json'),record)
finally:s.stop()
