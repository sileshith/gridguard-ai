import pytest
from pyspark.sql import SparkSession
from gridguard.splitting import split,folds
from gridguard.features import FEATURES,TARGET
from gridguard.models import pipeline
from gridguard.evaluation import evaluate
@pytest.fixture(scope='module')
def spark():
    s=SparkSession.builder.master('local[2]').appName('gridguard-tests').config('spark.sql.shuffle.partitions','2').getOrCreate()
    s.sparkContext.setLogLevel('ERROR');yield s;s.stop()
def fixture(spark):
    return spark.createDataFrame([(i,j,*[float((i*(k+3)+j)%17) for k in range(9)],float(i%2)) for i in range(60) for j in range(2)],['scenario_id','outage_line_id']+FEATURES+[TARGET])
def test_determinism_and_leakage(spark):
    df=fixture(spark);a=split(df);b=split(df.repartition(3))
    sets=[{r[0] for r in x.select('scenario_id').distinct().collect()} for x in a]
    assert sum(x.count() for x in a)==120
    assert sets[0].isdisjoint(sets[1]) and sets[0].isdisjoint(sets[2]) and sets[1].isdisjoint(sets[2])
    assert sets==[{r[0] for r in x.select('scenario_id').distinct().collect()} for x in b]
    from pyspark.sql import functions as F
    assert folds(df).groupBy('scenario_id').agg(F.countDistinct('fold').alias('n')).where('n!=1').count()==0

def test_smoke(spark):
    train,val,_=split(fixture(spark));model=pipeline('lr',parameters={'maxIter':3}).fit(train)
    m=evaluate(model.transform(val));assert 0<=m['PR_AUC']<=1


def test_scoring_roundtrip(spark,tmp_path):
    import csv
    from gridguard.scoring import score
    df=fixture(spark);train,_,_=split(df);model=pipeline('lr',parameters={'maxIter':3}).fit(train)
    model_path=str(tmp_path/'model');model.write().save(model_path)
    input_path=tmp_path/'input.csv'
    with input_path.open('w') as f:
        w=csv.writer(f);w.writerow(['scenario_id','outage_line_id']+FEATURES)
        # Only two fixture observations are collected; this is bounded test data.
        for r in df.drop(TARGET).limit(2).collect(): w.writerow(list(r))
    output=str(tmp_path/'scores');score(spark,str(input_path),output,model_path,.5,'fixture-v1')
    actual=spark.read.csv(output,header=True,inferSchema=True)
    assert actual.count()==2
    assert [r.risk_rank for r in actual.orderBy('risk_rank').collect()]==[1,2]
    assert {'risk_score','risk_rank','predicted_class','model_version','scoring_timestamp'}.issubset(actual.columns)
    assert TARGET not in actual.columns
