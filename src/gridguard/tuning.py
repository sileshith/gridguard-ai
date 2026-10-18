import time
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from .splitting import folds
from .models import pipeline

def tune(train, seed=4152026):
    start=time.monotonic();df=folds(train,3,seed).cache();records=[]
    for depth in [3,5]:
        parameters={'maxDepth':depth,'maxIter':20};scores=[]
        for fold in range(3):
            model=pipeline('gbt',seed,parameters).fit(df.where(df.fold!=fold))
            predictions=model.transform(df.where(df.fold==fold))
            scores.append(BinaryClassificationEvaluator(labelCol='Post_Outage_Violation',metricName='areaUnderPR').evaluate(predictions))
        records.append(dict(parameters=parameters,fold_scores=scores,mean_PR_AUC=sum(scores)/len(scores)))
    df.unpersist()
    return dict(seed=seed,folds=3,fold_method='xxhash64 scenario_id and seed modulo 3',configurations=2,records=records,winner=max(records,key=lambda r:r['mean_PR_AUC']),runtime_seconds=time.monotonic()-start)
