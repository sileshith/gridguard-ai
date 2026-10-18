from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import LogisticRegression, RandomForestClassifier, GBTClassifier
from .features import FEATURES,TARGET

def pipeline(name, seed=4152026, parameters=None):
    cls={'lr':LogisticRegression,'rf':RandomForestClassifier,'gbt':GBTClassifier}[name]
    args=dict(featuresCol='features',labelCol=TARGET)
    if name!='lr': args['seed']=seed
    args.update(parameters or {})
    return Pipeline(stages=[VectorAssembler(inputCols=FEATURES,outputCol='features',handleInvalid='error'),cls(**args)])
