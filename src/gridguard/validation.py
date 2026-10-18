import csv, math
from .features import FEATURES, TARGET, METADATA
from .artifacts import checksum

def validate_csv(path, expected_rows=None, scoring=False):
    seen=set(); scenarios=set(); positives=0; versions=set(); rows=0
    with open(path, newline="") as f:
        reader=csv.DictReader(f)
        required=FEATURES + ([] if scoring else METADATA+[TARGET])
        if not set(required).issubset(reader.fieldnames or []): raise ValueError("Missing required columns")
        for r in reader:
            rows+=1
            for k in FEATURES:
                if not math.isfinite(float(r[k])): raise ValueError("Non-finite predictor")
            if not scoring:
                if r[TARGET] not in ("0","1","0.0","1.0"): raise ValueError("Nonbinary target")
                positives+=int(float(r[TARGET])); versions.add(r['dataset_version'])
                if any(r[k]=='' for k in METADATA): raise ValueError("Null metadata")
                if float(r['islanding_flag'])!=0: raise ValueError("Unexpected islanding population")
            if 'scenario_id' in r and 'outage_line_id' in r:
                key=(r['scenario_id'],r['outage_line_id'])
                if key in seen: raise ValueError("Duplicate scenario-outage")
                seen.add(key);scenarios.add(r['scenario_id'])
    if not rows: raise ValueError("Empty input")
    if expected_rows is not None and rows!=expected_rows: raise ValueError("Unexpected row count")
    if not scoring and versions!={'ieee118_dc_lodf_v1'}: raise ValueError("Unexpected dataset version")
    return dict(rows=rows, positive_count=positives if not scoring else None, prevalence=positives/rows if not scoring else None, unique_scenarios=len(scenarios), versions=sorted(versions), sha256=checksum(path))


def validate_spark(df, expected_rows=None, scoring=False):
    from pyspark.sql import functions as F
    from pyspark.sql.types import NumericType
    required=FEATURES+([] if scoring else METADATA+[TARGET])
    numeric=FEATURES+([] if scoring else [TARGET])
    if not set(required).issubset(df.columns): raise ValueError('Missing required columns')
    for k in numeric:
        if not isinstance(df.schema[k].dataType,NumericType): raise ValueError('Nonnumeric column '+k)
    invalid=None
    for k in required:
        condition=F.col(k).isNull()
        if k in numeric: condition=condition | F.isnan(k) | (F.abs(F.col(k))==float('inf'))
        invalid=condition if invalid is None else invalid | condition
    if df.where(invalid).limit(1).count(): raise ValueError('Null or non-finite cells')
    if not scoring and df.where(~F.col(TARGET).isin(0,1)).limit(1).count(): raise ValueError('Nonbinary target')
    if not scoring and df.where((F.col('dataset_version')!='ieee118_dc_lodf_v1') | (F.col('islanding_flag')!=0)).limit(1).count(): raise ValueError('Unexpected population/version')
    if {'scenario_id','outage_line_id'}.issubset(df.columns) and df.groupBy('scenario_id','outage_line_id').count().where('count>1').limit(1).count(): raise ValueError('Duplicate scenario-outage')
    # One bounded summary row, never full-data collection.
    exprs=[F.count('*').alias('rows')]
    if not scoring: exprs.append(F.sum(TARGET).alias('positive_count'))
    if 'scenario_id' in df.columns: exprs.append(F.countDistinct('scenario_id').alias('unique_scenarios'))
    r=df.agg(*exprs).first().asDict()
    if r['rows']==0: raise ValueError('Empty input')
    if expected_rows is not None and r['rows']!=expected_rows: raise ValueError('Unexpected row count')
    if not scoring: r['prevalence']=r['positive_count']/r['rows']
    return r
