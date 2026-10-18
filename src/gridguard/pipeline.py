import argparse,datetime
from pathlib import Path
from pyspark.sql import SparkSession
from .config import load
from .validation import validate_csv,validate_spark
from .splitting import split
from .models import pipeline
from .evaluation import evaluate,with_score,threshold_metrics
from .screening import budgets
from .artifacts import save,manifest,directory_checksum
from .scoring import score

def main():
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--action',choices=['validate','train','evaluate','score','run'],default='run');p.add_argument('--input');p.add_argument('--output');a=p.parse_args()
    try: c=load(a.config,require_data=a.action!='score')
    except ValueError as exc: p.error(str(exc))
    out=Path(c['output'])
    if a.action=='validate':
        save(out/'validation.json',validate_csv(c['data'],c.get('expected_rows')));return
    if a.action in ['run','train','evaluate'] and (out/'freeze.json').exists(): raise SystemExit('Experiment is frozen; use a new output directory for any new experiment')
    spark=SparkSession.builder.master(c.get('master','local[2]')).appName('GridGuard').config('spark.sql.shuffle.partitions','4').config('spark.driver.memory','2g').getOrCreate();spark.sparkContext.setLogLevel('WARN')
    try:
        if a.action=='score':
            selected=__import__('json').loads((out/'selection.json').read_text())
            score(spark,a.input,a.output,str(out/selected['model']/'model'),selected['threshold'],selected['model']+'@'+directory_checksum(out/selected['model']/'model')[:12]);return
        df=spark.read.csv(c['data'],header=True,inferSchema=True).cache()
        validation=validate_spark(df,c.get('expected_rows'));save(out/'spark_validation.json',validation)
        train,val,test=split(df,c['seed']);metrics={};predictions={}
        save(out/'split_summary.json',{n:validate_spark(part) for n,part in [('train',train),('validation',val),('test',test)]})
        for name in ['lr','rf','gbt']:
            model=__import__('pyspark.ml',fromlist=['PipelineModel']).PipelineModel.load(str(out/name/'model')) if a.action=='evaluate' else pipeline(name,c['seed'],c.get('parameters',{}).get(name)).fit(train)
            pred=model.transform(val).cache();metrics[name]=evaluate(pred);predictions[name]=pred
            if a.action!='evaluate': model.write().overwrite().save(str(out/name/'model'))
            save(out/name/'metrics.json',metrics[name]);save(out/name/'parameters.json',{p.name:v for p,v in model.stages[-1].extractParamMap().items()})
        best=max(metrics,key=lambda x:metrics[x]['PR_AUC']);selected=with_score(predictions[best]);table=[threshold_metrics(selected,t) for t in [.05,.1,.2,.3,.4,.5,.6,.7,.8,.9]];threshold=max(table,key=lambda x:(x['F1'],-x['threshold']))['threshold']
        save(out/'thresholds.json',table);save(out/'selection.json',dict(model=best,threshold=threshold,rule='maximum validation F1; ties prefer lower threshold',test_evaluated=False))
        save(out/'screening.json',budgets(selected)+budgets(selected,'Pre_Outage_Line_Loading'))
        m=manifest(a.config,c,metrics);m['model']='lr/rf/gbt';m['hyperparameters']={name:__import__('json').loads((out/name/'parameters.json').read_text()) for name in metrics};save(out/'manifest.json',m)
        historical={'lr':[.8477,.9696,.8253,.6881,.7505],'rf':[.8588,.9630,.906,.6193,.7357],'gbt':[.9142,.981,.8921,.7775,.8309]} if c.get('expected_rows')==50000 else {'lr':[.8542,.9699,.8264,.6918,.7531],'rf':[.8736,.9663,.9234,.6585,.7687],'gbt':[.9262,.9832,.9256,.7829,.8483]}
        if c.get('expected_rows') in [50000,1000000]: save(out/'historical_comparison.json',{n:{k:dict(historical=v,reproduced=metrics[n][k],absolute_difference=abs(metrics[n][k]-v)) for k,v in zip(['PR_AUC','ROC_AUC','precision','recall','F1'],vs)} for n,vs in historical.items()})
        print(metrics)
    finally:spark.stop()
if __name__=='__main__':main()
