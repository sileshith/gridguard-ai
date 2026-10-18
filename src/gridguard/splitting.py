from pyspark.sql import functions as F

def split(df, seed=4152026):
    ids=df.select('scenario_id').distinct().repartition(1).sortWithinPartitions('scenario_id').cache()
    ids.count()
    train,tmp=ids.randomSplit([.7,.3],seed)
    val,test=tmp.randomSplit([.5,.5],seed)
    parts=[x.cache() for x in (train,val,test)]
    for x in parts: x.count()
    for a,b in ((0,1),(0,2),(1,2)):
        if parts[a].join(parts[b], 'scenario_id').limit(1).count(): raise ValueError('Scenario leakage')
    return tuple(df.join(x,'scenario_id') for x in parts)

def folds(df, n=3, seed=4152026):
    return df.withColumn('fold',F.pmod(F.xxhash64('scenario_id',F.lit(seed)),F.lit(n)).cast('int'))
