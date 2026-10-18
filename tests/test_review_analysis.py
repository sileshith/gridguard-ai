import pytest
from gridguard.screening import ceiling_context
from gridguard.review_analysis import scenario_metrics, pr_auc, PRODUCT
from gridguard.features import TARGET, FEATURES


def test_nominal_and_realized_ceiling_rounding():
    c = ceiling_context(10, 4, 1, 1, .01)
    assert c['best_possible'] == pytest.approx(.025)
    assert c['share_of_best'] == pytest.approx(10)
    assert c['share_of_best_realized'] == 1


def test_no_positives_have_no_defined_recall_ceiling():
    c = ceiling_context(10, 0, 2, 0, .2)
    assert c['best_possible'] is None
    assert c['share_of_best'] is None


@pytest.mark.parametrize('args', [(0,0,0,0,.2),(10,2,1,2,.2),(10,2,2,1,0)])
def test_invalid_ceiling_inputs(args):
    with pytest.raises(ValueError):
        ceiling_context(*args)


def test_scenario_denominators_and_ties():
    from pyspark.sql import SparkSession
    spark = SparkSession.builder.master('local[2]').appName('review-fixture').getOrCreate()
    spark.sparkContext.setLogLevel('ERROR')
    try:
        # At k=1, state 1 captures one of two positives, state 2 misses its positive.
        df = spark.createDataFrame([(1,1,3.,1.),(1,2,2.,1.),(1,3,1.,0.),
                                    (2,1,3.,0.),(2,2,2.,1.),(2,3,1.,0.),
                                    (3,1,3.,0.),(3,2,2.,0.),(3,3,1.,0.)],
                                   ['scenario_id','outage_line_id','score',TARGET])
        m = scenario_metrics(df, 'score', .2)
        assert m['scenarios'] == 3 and m['positive_scenarios'] == 2
        assert m['mean_recall_positive_scenarios'] == pytest.approx(.25)
        assert m['median_recall_positive_scenarios'] == pytest.approx(.25)
        assert m['mean_share_of_best_positive_scenarios'] == pytest.approx(5/6)
        assert m['share_all_scenarios_with_miss'] == pytest.approx(2/3)
        assert m['share_positive_scenarios_with_miss'] == 1
        assert 0 <= pr_auc(df, 'score') <= 1
        from gridguard.review_analysis import validation_eda
        from gridguard.features import FEATURES
        from pyspark.sql import functions as F
        for feature in FEATURES:
            df = df.withColumn(feature, F.col('score'))
        eda = validation_eda(df)
        assert eda['scenario_structure']['share_scenarios_without_positives'] == pytest.approx(1/3)
        assert len(eda['class_feature_summaries']) == 2
        assert 'scenario_id' not in str(eda) and 'outage_line_id' not in str(eda)
    finally:
        spark.stop()


@pytest.fixture(scope='module')
def scalar_score_spark():
    from pyspark.sql import SparkSession
    session = SparkSession.builder.master('local[2]').appName('scalar-pr-fixture').getOrCreate()
    session.sparkContext.setLogLevel('ERROR')
    yield session
    session.stop()


@pytest.mark.parametrize('feature', FEATURES)
@pytest.mark.parametrize('numeric_type', ['int', 'double'])
def test_single_feature_pr_accepts_numeric_types_without_source_changes(scalar_score_spark, feature, numeric_type):
    from pyspark.sql import functions as F
    frame = scalar_score_spark.createDataFrame([(0,0),(1,0),(2,1),(3,1)], ['value',TARGET])
    frame = frame.select(F.col('value').cast(numeric_type).alias(feature),
                         F.col(TARGET).cast(numeric_type).alias(TARGET))
    original_schema = frame.schema
    original_columns = frame.columns
    assert pr_auc(frame, feature) == pytest.approx(1.)
    assert frame.schema == original_schema
    assert frame.columns == original_columns
    assert frame.schema[feature].dataType.simpleString() == numeric_type
