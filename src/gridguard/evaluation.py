from pyspark.sql import functions as F
from pyspark.ml.functions import vector_to_array
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from .features import TARGET

def counts(tp,fp,fn,tn):
    precision=tp/(tp+fp) if tp+fp else 0.;recall=tp/(tp+fn) if tp+fn else 0.
    return dict(TP=tp,FP=fp,FN=fn,TN=tn,precision=precision,recall=recall,F1=2*precision*recall/(precision+recall) if precision+recall else 0.)
def with_score(df): return df.withColumn('risk_score',vector_to_array('probability')[1])
def threshold_metrics(df,threshold=.5):
    pos=F.col('risk_score')>=threshold;y=F.col(TARGET)==1
    exprs=[F.sum(F.when(a,1).otherwise(0)).alias(k) for k,a in [('tp',pos&y),('fp',pos&~y),('fn',~pos&y),('tn',~pos&~y)]]
    r=df.agg(*exprs).first().asDict();m=counts(**r);n=sum(r.values())
    m.update(threshold=threshold,percent_flagged=100*(r['tp']+r['fp'])/n,workload_reduction=1-(r['tp']+r['fp'])/n)
    return m
def evaluate(df):
    m=threshold_metrics(with_score(df))
    for key,metric in [('PR_AUC','areaUnderPR'),('ROC_AUC','areaUnderROC')]:
        m[key]=BinaryClassificationEvaluator(labelCol=TARGET,rawPredictionCol='rawPrediction',metricName=metric).evaluate(df)
    return m
