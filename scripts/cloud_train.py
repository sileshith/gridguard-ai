"""Distributed cloud entry point; also locally smoke-tested. Never provisions resources."""
import argparse,datetime,hashlib,json,platform,tempfile
from pathlib import Path
from pyspark.sql import SparkSession,functions as F
from gridguard.features import FEATURES
from gridguard.validation import validate_spark
from gridguard.splitting import split
from gridguard.models import pipeline
from gridguard.evaluation import evaluate,with_score,threshold_metrics
from gridguard.screening import budgets

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True);p.add_argument('--sha256',required=True);p.add_argument('--expected-rows',type=int,default=1000000);p.add_argument('--source-commit',required=True);p.add_argument('--master');a=p.parse_args()
    builder=SparkSession.builder.appName('GridGuard-cloud')
    if a.master:builder=builder.master(a.master)
    s=builder.getOrCreate();s.sparkContext.setLogLevel('WARN')
    try:
        # Canonical 1M CSV is ~99 MB. Bound the binary hashing operation to 128 MB.
        metadata=s.read.format('binaryFile').load(a.input).select('length')
        if metadata.count()!=1 or metadata.first()[0]>128*1024*1024:raise ValueError('Require one canonical CSV no larger than 128 MiB')
        actual_hash=s.read.format('binaryFile').load(a.input).select(F.sha2('content',256)).first()[0]
        if actual_hash!=a.sha256:raise ValueError('Input SHA-256 mismatch')
        df=s.read.csv(a.input,header=True,inferSchema=True).cache();integrity=validate_spark(df,a.expected_rows);train,val,test=split(df);metrics={};parameters={};predictions={}
        for name in ['lr','rf','gbt']:
            model=pipeline(name).fit(train);pred=model.transform(val).cache();metrics[name]=evaluate(pred);parameters[name]={k.name:v for k,v in model.stages[-1].extractParamMap().items()};predictions[name]=pred
            model.write().save(a.output+'/'+name+'/model')
        best=max(metrics,key=lambda n:metrics[n]['PR_AUC']);scored=with_score(predictions[best]);thresholds=[threshold_metrics(scored,t) for t in [.05,.1,.2,.3,.4,.5,.6,.7,.8,.9]]
        manifest=dict(run_id=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'),timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),evidence_state='REPRODUCED' if a.expected_rows==1000000 else 'ENHANCED',git_commit=a.source_commit,data_hash=actual_hash,config_hash=hashlib.sha256(json.dumps(vars(a),sort_keys=True).encode()).hexdigest(),seed=4152026,feature_list=FEATURES,model='lr/rf/gbt',hyperparameters=parameters,split_method='sorted scenario IDs; two-stage Spark randomSplit',metrics=metrics,environment=dict(spark=s.version,python=platform.python_version(),java=s._jvm.java.lang.System.getProperty('java.version')),integrity=integrity,thresholds=thresholds,screening=budgets(scored)+budgets(scored,'Pre_Outage_Line_Loading'),test_evaluated=False,invocation=vars(a))
        local=Path(tempfile.mkdtemp(prefix='gridguard-cloud-'))/'manifest.json';local.write_text(json.dumps(manifest,indent=2))
        destination=s._jvm.org.apache.hadoop.fs.Path(a.output+'/manifest.json');fs=destination.getFileSystem(s._jsc.hadoopConfiguration());fs.copyFromLocalFile(False,False,s._jvm.org.apache.hadoop.fs.Path(str(local)),destination)
        print(json.dumps(dict(manifest=a.output+'/manifest.json',metrics=metrics)))
    finally:s.stop()
if __name__=='__main__':main()
