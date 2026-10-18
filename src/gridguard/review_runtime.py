"""Local validation-only experiment inputs and fail-closed output handling."""
import json
import platform
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.ml import PipelineModel
from .config import load, PROJECT_ROOT
from .validation import validate_csv, validate_spark
from .splitting import split
from .evaluation import with_score


def prepare_output(name):
    out = Path(name).resolve()
    allowed = (PROJECT_ROOT / 'results/local').resolve()
    if not out.is_relative_to(allowed) or out == allowed:
        raise ValueError('New experiment output must be a new child of results/local')
    out.mkdir(parents=True, exist_ok=False)
    return out


def write_json(path, value):
    with Path(path).open('x') as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write('\n')


def open_validation(config_path, model_dir=None):
    config = load(config_path)
    if not config.get('master', 'local[2]').startswith('local['):
        raise ValueError('Review experiments require local Spark')
    integrity = validate_csv(config['data'], config.get('expected_rows'))
    if config.get('expected_rows') == 1000000:
        expected = json.loads((PROJECT_ROOT/'results/dataproc_1m_manual/evidence.json').read_text())['integrity']['data_sha256']
        if integrity['sha256'] != expected:
            raise ValueError('Input identity differs from the recorded canonical 1M input')
    spark = SparkSession.builder.master(config.get('master', 'local[2]')).appName(
        'GridGuard validation review').config('spark.sql.shuffle.partitions', '4').getOrCreate()
    spark.sparkContext.setLogLevel('ERROR')
    try:
        df = spark.read.csv(config['data'], header=True, inferSchema=True).cache()
        validate_spark(df, config.get('expected_rows'))
        train, validation, _unscored = split(df, config['seed'])
        validation = validation.cache()
        summary = validate_spark(validation)
        if config.get('expected_rows') == 1000000:
            if summary['rows'] != 153105 or summary['positive_count'] != 17739 or summary['unique_scenarios'] != 865:
                raise ValueError('Validation population differs from the recorded local 1M split')
        if model_dir:
            resolved_model = Path(model_dir).expanduser().resolve()
            model = PipelineModel.load(str(resolved_model))
            from .features import FEATURES
            if model.stages[0].getInputCols() != FEATURES or model.stages[-1].__class__.__name__ != 'GBTClassificationModel':
                raise ValueError('Expected the recorded nine-feature GBT pipeline')
            validation = with_score(model.transform(validation)).cache()
            from .artifacts import directory_checksum
            model_hash = directory_checksum(resolved_model)
        else:
            model_hash = None
        metadata = dict(data_sha256=integrity['sha256'], validation=summary,
                        split_seed=config['seed'], split_method='sorted scenario IDs, randomSplit 70/30 then 50/50',
                        spark=spark.version, python=platform.python_version(),
                        java=spark.sparkContext._jvm.java.lang.System.getProperty('java.version'),
                        model_content_sha256=model_hash, test_evaluated=False)
        return spark, train, validation, metadata
    except BaseException:
        spark.stop()
        raise
