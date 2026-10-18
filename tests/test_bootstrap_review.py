import inspect
import numpy as np
import pytest
from gridguard.bootstrap_review import bootstrap_arrays, scenario_weights, percentile_interval, bounded_arrays, verify_points

@pytest.fixture
def fixture():
    data=np.array([(s, float(j==0), .9 if j==0 else .1, .1 if j==0 else .9, j) for s in range(4) for j in range(2)])
    return data, data[:,0].astype(int)

def test_exactly_1000_draws(fixture):
    records=[]
    result=bootstrap_arrays(*fixture,checkpoint=records.append)
    assert result['resamples']==result['valid_resamples']==len(records)==1000
    assert [r['resample'] for r in records]==list(range(1000))

def test_scenario_blocks_inherit_identical_multiplicity(fixture):
    _,ix=fixture
    for weights in scenario_weights(4,100,3):
        row_weights=weights[ix]
        assert weights.sum()==4
        assert all(len(set(row_weights[ix==s]))==1 for s in range(4))

def test_seed_repeatability_and_change():
    a=np.array(list(scenario_weights(4,20,3)))
    assert np.array_equal(a,np.array(list(scenario_weights(4,20,3))))
    assert not np.array_equal(a,np.array(list(scenario_weights(4,20,4))))

def test_replacement_can_repeat_or_omit_scenarios():
    w=np.array(list(scenario_weights(4,100,3)))
    assert (w>1).any() and (w==0).any()

def test_percentile_linear_quantiles():
    assert percentile_interval([0,1,2,3,4])=={'lower':.1,'upper':3.9}

def test_known_capture_and_paired_gaps(fixture):
    r=bootstrap_arrays(*fixture,resamples=8)
    assert r['point_estimates']['gbt_capture_20']==.5
    assert r['point_estimates']['baseline_capture_20']==0
    assert r['point_estimates']['gap_capture_20']==.5
    assert r['point_estimates']['gap_mean_scenario_recall_20']==1
    assert r['percentile_95_intervals']['gap_capture_20']=={'lower':.5,'upper':.5}

def test_no_test_or_spark_access_in_draw_loop():
    source=inspect.getsource(bootstrap_arrays)
    assert 'sparkSession' not in source and 'collect(' not in source and 'transform(' not in source and 'test_split' not in source
    assert bootstrap_arrays.__module__=='gridguard.bootstrap_review'

def test_minimal_bounded_collection():
    class Frame:
        def select(self,*cols):
            assert cols==('scenario_id','Post_Outage_Violation','risk_score','Pre_Outage_Line_Loading','outage_line_id');return self
        def limit(self,n):assert n==4;return self
        def collect(self):return [(0,1,.8,.5,0),(0,0,.1,.4,1),(1,1,.9,.7,0),(1,0,.2,.2,1)]
    with pytest.raises(ValueError,match='row bound'):bounded_arrays(Frame(),max_rows=3)

def test_partial_draws_never_become_summary(fixture):
    data,ix=fixture
    data[:,1]=0
    with pytest.raises(ValueError,match='Zero-positive'):bootstrap_arrays(data,ix,resamples=2)
    script=__import__('pathlib').Path('scripts/scenario_bootstrap.py').read_text()
    assert "prepare_output(a.output)" in script
    assert script.index('verify_points(result, chosen)')<script.index("write_json(out/'scenario_bootstrap.json'")
    assert 'resamples.jsonl' in script and 'read_text()' not in script[script.index('with (out/'):]

def test_point_check_rejects_disagreement(fixture):
    result=bootstrap_arrays(*fixture,resamples=2)
    review={'test_evaluated':False,'strongest_heuristic':'Pre_Outage_Line_Loading','rankings':[], 'per_scenario':[]}
    for name,score in [('gbt','risk_score'),('baseline','Pre_Outage_Line_Loading')]:
        review['rankings'].append({'score':score,'screening':[{'budget':b,'capture_rate':result['point_estimates'][f'{name}_capture_{int(b*100)}']} for b in [.1,.2]]})
        review['per_scenario'].append({'score':score,'budget':.2,'mean_recall_positive_scenarios':result['point_estimates'][f'{name}_mean_scenario_recall_20']})
    assert verify_points(result,review)['passed']
    review['rankings'][0]['screening'][0]['capture_rate']+=.01
    with pytest.raises(ValueError,match='disagrees'):verify_points(result,review)

def test_pr_auc_is_explicitly_omitted(fixture):
    result=bootstrap_arrays(*fixture,resamples=2)
    assert not result['pr_auc']['included']
    assert all('PR_AUC' not in k for k in result['percentile_95_intervals'])
    assert result['test_evaluated'] is False
