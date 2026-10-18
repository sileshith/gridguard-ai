"""Validation-only screening analysis. Return aggregates, never candidate records."""
import math
from pyspark.sql import functions as F, Window
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from .features import FEATURES, TARGET
from .screening import budgets

BUDGETS = (.01, .05, .1, .2)
PRODUCT = 'loading_times_sensitivity'


def pr_auc(df, score, weight=None):
    """Evaluate numeric scalar scores through a temporary double projection."""
    columns = [F.col(TARGET).cast('double').alias('_review_label'),
               F.col(score).cast('double').alias('_review_score')]
    options = dict(labelCol='_review_label', rawPredictionCol='_review_score',
                   metricName='areaUnderPR', numBins=1000)
    if weight:
        columns.append(F.col(weight).cast('double').alias('_review_weight'))
        options['weightCol'] = '_review_weight'
    scored = df.select(*columns)
    return float(BinaryClassificationEvaluator(**options).evaluate(scored))


def scenario_metrics(df, score, budget):
    if not 0 < budget <= 1:
        raise ValueError('Budget must lie in (0, 1]')
    population = Window.partitionBy('scenario_id')
    order = population.orderBy(F.desc(score), F.asc('outage_line_id'))
    ranked = df.withColumn('_rank', F.row_number().over(order)).withColumn(
        '_n', F.count('*').over(population))
    grouped = ranked.groupBy('scenario_id').agg(
        F.max('_n').alias('rows'),
        F.sum(TARGET).alias('positives'),
        F.sum(F.when(F.col('_rank') <= F.ceil(F.col('_n') * budget),
                     F.col(TARGET)).otherwise(0)).alias('captured'))
    grouped = grouped.withColumn('recall', F.when(F.col('positives') > 0,
                                                F.col('captured') / F.col('positives')))
    grouped = grouped.withColumn('ceiling', F.when(F.col('positives') > 0,
        F.least(F.lit(1.), F.lit(budget) * F.col('rows') / F.col('positives'))))
    grouped = grouped.withColumn('share_of_best', F.col('recall') / F.col('ceiling'))
    row = grouped.agg(
        F.count('*').alias('scenarios'),
        F.sum(F.when(F.col('positives') > 0, 1).otherwise(0)).alias('positive_scenarios'),
        F.avg('recall').alias('mean_recall_positive_scenarios'),
        F.avg('ceiling').alias('mean_best_possible_positive_scenarios'),
        F.avg('share_of_best').alias('mean_share_of_best_positive_scenarios'),
        F.median('recall').alias('median_recall_positive_scenarios'),
        F.avg((F.col('captured') < F.col('positives')).cast('double')).alias('share_all_scenarios_with_miss'),
        F.avg(F.when(F.col('positives') > 0,
                     (F.col('captured') < F.col('positives')).cast('double'))).alias('share_positive_scenarios_with_miss')
    ).first().asDict()
    return dict(score=score, budget=budget, **row,
                zero_positive_policy='Excluded from recall mean and median. Included as no miss in all-scenario share.')


def summarize_validation(df, include_gbt=True):
    scores = df.withColumn(PRODUCT, F.col('Pre_Outage_Line_Loading') *
                           F.col('Line_Outage_Sensitivity')).cache()
    try:
        count = scores.agg(F.count('*').alias('rows'), F.sum(TARGET).alias('positives'),
                           F.countDistinct('scenario_id').alias('scenarios')).first().asDict()
        if not count['rows'] or not 0 < count['positives'] < count['rows']:
            raise ValueError('Validation requires both classes')
        single = [dict(score=f, PR_AUC=pr_auc(scores, f)) for f in FEATURES]
        best = min(single, key=lambda r: (-r['PR_AUC'], r['score']))['score']
        names = list(dict.fromkeys(['Pre_Outage_Line_Loading', PRODUCT, best] +
                                   (['risk_score'] if include_gbt else [])))
        rankings = [dict(score=s, PR_AUC=pr_auc(scores, s), screening=budgets(scores, s))
                    for s in names]
        per_scenario = [scenario_metrics(scores, s, b) for s in names for b in (.1, .2)]
        strongest = min((r for r in rankings if r['score'] != 'risk_score'),
                        key=lambda r: (-r['PR_AUC'], r['score']))['score']
        return dict(validation=count, eda=validation_eda(scores), single_features=single, best_single_feature=best,
                    strongest_heuristic=strongest, rankings=rankings, per_scenario=per_scenario,
                    score_direction='All nine raw features ranked descending. No sign search.',
                    selection_note='Best feature and heuristic selected on this validation sample. Their estimates and gaps are descriptive and subject to selection optimism.',
                    pr_auc_method='Spark areaUnderPR with numBins=1000. Not average precision.',
                    ceiling_note='Nominal share can exceed one for tiny samples due to ceil(N * budget). Realized-budget ceiling is also reported.',
                    test_evaluated=False)
    finally:
        scores.unpersist()


def validation_eda(df):
    """Return class summaries and scenario-distribution aggregates without identifiers."""
    scenario = df.groupBy('scenario_id').agg(F.count('*').alias('rows'),
                                             F.sum(TARGET).alias('positives'))
    structure = scenario.agg(
        F.count('*').alias('scenario_count'), F.min('rows').alias('min_outages'),
        F.max('rows').alias('max_outages'), F.avg('rows').alias('mean_outages'),
        F.percentile('rows', [.25,.5,.75]).alias('outage_quartiles'),
        F.percentile('positives', [.25,.5,.75]).alias('positive_quartiles'),
        F.avg((F.col('positives')==0).cast('double')).alias('share_scenarios_without_positives')
    ).first().asDict()
    expressions = [F.count('*').alias('rows')]
    for feature in FEATURES:
        expressions += [F.avg(feature).alias(feature+'_mean'),
                        F.stddev_pop(feature).alias(feature+'_std'),
                        F.min(feature).alias(feature+'_min'), F.max(feature).alias(feature+'_max')]
    # Binary target validation upstream limits this to two aggregate records.
    classes = [r.asDict() for r in df.groupBy(TARGET).agg(*expressions).orderBy(TARGET).limit(2).collect()]
    return dict(scenario_structure=structure, class_feature_summaries=classes,
                scope='Validation aggregates only. No scenario identifiers or candidate records.')
