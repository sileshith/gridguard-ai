from pyspark.ml import PipelineModel
from pyspark.sql import functions as F
from pyspark.sql.types import StructType,StructField,LongType
from .evaluation import with_score
from .validation import validate_spark
from .artifacts import checksum

def score(spark,input_path,output_path,model_path,threshold,model_version):
    df=spark.read.csv(input_path,header=True,inferSchema=True)
    validate_spark(df,scoring=True)
    trace=[c for c in ['scenario_id','outage_line_id','dataset_version'] if c in df.columns]
    scored=with_score(PipelineModel.load(model_path).transform(df)).select(*trace,'risk_score')
    order=[F.desc('risk_score')]+[F.asc(c) for c in ['scenario_id','outage_line_id'] if c in df.columns]
    ordered=scored.orderBy(*order)
    # Distributed global order + prefix offsets; zipWithIndex collects only one
    # count per Spark partition, never observation rows. No single-partition window.
    indexed=ordered.rdd.zipWithIndex().map(lambda pair:tuple(pair[0])+(pair[1]+1,))
    schema=StructType(ordered.schema.fields+[StructField('risk_rank',LongType(),False)])
    scored=spark.createDataFrame(indexed,schema)
    scored=scored.withColumn('predicted_class',(F.col('risk_score')>=threshold).cast('int')).withColumn('model_version',F.lit(model_version)).withColumn('scoring_input_sha256',F.lit(checksum(input_path))).withColumn('operating_threshold',F.lit(threshold)).withColumn('scoring_timestamp',F.current_timestamp())
    scored.write.mode('errorifexists').option('header',True).csv(output_path)
