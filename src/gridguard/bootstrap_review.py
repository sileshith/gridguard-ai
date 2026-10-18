"""Bounded paired scenario-cluster bootstrap. No Spark jobs inside the draw loop."""
import math
import numpy as np
from .features import TARGET

def percentile_interval(values):
    lower, upper = np.quantile(values, [.025, .975], method='linear')
    return dict(lower=float(lower), upper=float(upper))


def scenario_weights(n, resamples, seed):
    rng = np.random.default_rng(seed)
    for _ in range(resamples):
        yield rng.multinomial(n, np.full(n, 1/n))


def bounded_arrays(df, max_rows=153105, max_scenarios=865):
    # Bound the collection before bringing any records into Python.
    rows = df.select('scenario_id', TARGET, 'risk_score',
                     'Pre_Outage_Line_Loading', 'outage_line_id').limit(max_rows+1).collect()
    if len(rows) > max_rows:
        raise ValueError('Validation representation exceeds the row bound')
    data = np.asarray([tuple(r) for r in rows], dtype=np.float64)
    if data.ndim != 2 or data.shape[1] != 5 or not np.isfinite(data).all():
        raise ValueError('Invalid bounded validation representation')
    if not np.isin(data[:, 1], [0, 1]).all():
        raise ValueError('Labels must be binary')
    ids, inverse = np.unique(data[:, 0], return_inverse=True)
    if not 2 <= len(ids) <= max_scenarios:
        raise ValueError('Validation scenario count is outside the bound')
    return data, inverse


def bootstrap_arrays(data, inverse, resamples=1000, seed=4152026, checkpoint=None):
    if resamples < 2:
        raise ValueError('Use at least two resamples')
    n = int(inverse.max())+1
    labels = data[:, 1]
    # Stable deterministic ties match the Spark pooled ordering.
    orders = {name: np.lexsort((data[:, 4], data[:, 0], -data[:, col]))
              for name, col in [('gbt', 2), ('baseline', 3)]}
    positive = np.bincount(inverse, weights=labels, minlength=n)
    recalls = {}
    for name, col in [('gbt', 2), ('baseline', 3)]:
        values = np.full(n, np.nan)
        for scenario in range(n):
            ix = np.flatnonzero(inverse == scenario)
            ranked = ix[np.lexsort((data[ix, 4], -data[ix, col]))]
            if positive[scenario]:
                values[scenario] = labels[ranked[:math.ceil(len(ix)*.2)]].sum()/positive[scenario]
        recalls[name] = values

    def metrics(weights):
        row_weights = weights[inverse]
        total = int(row_weights.sum())
        positives = float(np.sum(row_weights * labels))
        if not positives:
            raise ValueError('Zero-positive draw. No final interval is written')
        result = {}
        for name, order in orders.items():
            w = row_weights[order]
            before = np.cumsum(w)-w
            for budget in [.1, .2]:
                take = np.minimum(w, np.maximum(math.ceil(total*budget)-before, 0))
                result[f'{name}_capture_{int(budget*100)}'] = float(np.sum(take * labels[order])/positives)
            valid = np.isfinite(recalls[name])
            result[f'{name}_mean_scenario_recall_20'] = float(np.sum(weights[valid] * recalls[name][valid])/weights[valid].sum())
        for metric in ['capture_10', 'capture_20', 'mean_scenario_recall_20']:
            result['gap_'+metric] = result['gbt_'+metric]-result['baseline_'+metric]
        return result

    point = metrics(np.ones(n, dtype=np.int64))
    records = []
    for i, weights in enumerate(scenario_weights(n, resamples, seed)):
        record = dict(resample=i, **metrics(weights))
        records.append(record)
        if checkpoint:
            checkpoint(record)
    intervals = {key: percentile_interval([r[key] for r in records]) for key in point}
    return dict(status='complete', resamples=resamples, valid_resamples=len(records),
        bootstrap_seed=seed, bootstrap_unit='operating scenario', validation_scenarios=n,
        validation_rows=len(data), point_estimates=point, percentile_95_intervals=intervals,
        method='Paired scenario-cluster bootstrap. Sample n scenarios with replacement using multinomial multiplicities. Every outage row inherits its scenario multiplicity. Pooled budgets use ceil(resampled row count * budget). Repeated boundary rows may be partly selected. Per-scenario recall uses ceil(original scenario row count * 0.2), with multiplicity-weighted means over positive scenarios.',
        interval_method='Percentile 95%, NumPy linear quantiles at 0.025 and 0.975',
        selection_limit='Fixed existing model and validation-selected loading baseline. Intervals do not correct selection optimism or calibration overlap.',
        pr_auc={'included':False, 'reason':"Scenario-bootstrap uncertainty is reported for capture and per-scenario recall. PR-AUC uncertainty was omitted because the bounded Python implementation did not exactly reproduce Spark's areaUnderPR definition.", 'equivalence_status':'Not established. No alternative PR-AUC estimator or interval is computed.', 'reference_definition':'Spark areaUnderPR, numBins=1000'},
        test_evaluated=False)


def verify_points(result, review, tolerance=1e-10):
    if review.get('test_evaluated') is not False:
        raise ValueError('Expected completed validation-only review')
    ranks = {r['score']: r for r in review['rankings']}
    scenarios = {(r['score'], r['budget']):r for r in review['per_scenario']}
    if review['strongest_heuristic'] != 'Pre_Outage_Line_Loading':
        raise ValueError('This protocol freezes the loading baseline')
    for name, score in [('gbt', 'risk_score'), ('baseline', 'Pre_Outage_Line_Loading')]:
        for budget in [.1, .2]:
            expected = next(r['capture_rate'] for r in ranks[score]['screening'] if r['budget']==budget)
            if abs(result['point_estimates'][f'{name}_capture_{int(budget*100)}']-expected)>tolerance:
                raise ValueError('Bounded capture disagrees with verified validation')
        expected = scenarios[(score, .2)]['mean_recall_positive_scenarios']
        if abs(result['point_estimates'][f'{name}_mean_scenario_recall_20']-expected)>tolerance:
            raise ValueError('Bounded scenario recall disagrees with verified validation')
    return dict(passed=True, absolute_tolerance=tolerance)
