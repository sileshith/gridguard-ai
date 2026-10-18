"""Future once-only final test. Separate policy-specific approval is mandatory."""
import argparse, json, datetime
from pathlib import Path
from gridguard.config import load, PROJECT_ROOT
from gridguard.artifacts import checksum
from gridguard.policy import verify_policy, verify_authorization, reserve_once


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',required=True)
    parser.add_argument('--policy',required=True)
    parser.add_argument('--authorization',required=True)
    parser.add_argument('--model-dir',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    policy_path=Path(args.policy)
    policy=json.loads(policy_path.read_text())
    config=load(args.config)
    out=Path(args.output).resolve()
    if out != (PROJECT_ROOT/'results/local/final_test_1m_policy_v1').resolve():
        raise ValueError('Final-test output is fixed to results/local/final_test_1m_policy_v1')
    verify_authorization(args.authorization,policy_path)
    verify_policy(policy,PROJECT_ROOT,args.config,config['data'],args.model_dir)
    if config['seed'] != policy['split_seed']:
        raise ValueError('Split seed changed')
    out.mkdir(parents=True,exist_ok=True)
    reserve_once(out)
    # No Spark session or model scoring is possible before all guards succeed.
    from pyspark.sql import SparkSession
    from pyspark.ml import PipelineModel
    from pyspark.ml.evaluation import BinaryClassificationEvaluator
    from gridguard.splitting import split
    from gridguard.evaluation import with_score
    from gridguard.screening import budgets
    from gridguard.review_analysis import scenario_metrics
    spark=SparkSession.builder.master(config.get('master','local[2]')).appName('GridGuard approved final test').getOrCreate()
    try:
        frame=spark.read.csv(config['data'],header=True,inferSchema=True)
        _,validation,test=split(frame,config['seed'])
        from gridguard.validation import validate_spark
        summary=validate_spark(validation)
        for key in ['rows','positive_count','unique_scenarios']:
            if summary[key] != policy['validation_population'][key]:
                raise ValueError('Frozen validation population changed')
        model=PipelineModel.load(args.model_dir)
        if model.stages[0].getInputCols()!=policy['features'] or model.stages[-1].__class__.__name__!='GBTClassificationModel':
            raise ValueError('Unexpected frozen pipeline')
        scored=with_score(model.transform(test)).cache()
        ranking={key:float(BinaryClassificationEvaluator(labelCol='Post_Outage_Violation',rawPredictionCol='rawPrediction',metricName=metric,numBins=1000).evaluate(scored)) for key,metric in [('PR_AUC','areaUnderPR'),('ROC_AUC','areaUnderROC')]}
        pooled=[]
        all_budgets={score:budgets(scored,score,policy['budgets']) for score in ['risk_score','Pre_Outage_Line_Loading']}
        for b in policy['budgets']:
            g=next(x for x in all_budgets['risk_score'] if x['budget']==b)
            h=next(x for x in all_budgets['Pre_Outage_Line_Loading'] if x['budget']==b)
            pooled.append(dict(budget=b,gbt=g,baseline=h,gain=g['capture_rate']-h['capture_rate']))
        scenario=[scenario_metrics(scored,score,b) for score in ['risk_score','Pre_Outage_Line_Loading'] for b in policy['budgets']]
        result=dict(policy_sha256=checksum(policy_path),code_commit=policy['code_commit'],timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),ranking=ranking,pooled=pooled,per_scenario=scenario,test_evaluated=True,threshold_evaluated=False)
        with (out/'final_test.json').open('x') as handle:json.dump(result,handle,indent=2,allow_nan=False)
    finally:spark.stop()


if __name__=='__main__':main()
