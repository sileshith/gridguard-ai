import copy,json
from pathlib import Path
import pytest
from gridguard.policy import verify_policy, verify_authorization, reserve_once, RULE, METRICS
from gridguard.features import FEATURES
from gridguard.artifacts import checksum,directory_checksum

@pytest.fixture
def policy_fixture(tmp_path):
    for name in ['config','data','code.py']: (tmp_path/name).write_text(name)
    model=tmp_path/'model';model.mkdir();(model/'metadata').write_text('fixture')
    policy=dict(status='POLICY_FROZEN',features=FEATURES,model_family='GBT',baseline='Pre_Outage_Line_Loading',primary_policy='pooled_top_20_percent',secondary_policy='within_scenario_top_20_percent',budgets=[.1,.2],threshold=None,metrics=METRICS,governance_rule=RULE,split_seed=4152026,ranking_direction='descending',pooled_ties=['scenario_id','outage_line_id'],scenario_ties=['outage_line_id'],source_sha256={'code.py':checksum(tmp_path/'code.py')},config_sha256=checksum(tmp_path/'config'),data_sha256=checksum(tmp_path/'data'),model_content_sha256=directory_checksum(model))
    return tmp_path,model,policy

def test_matching_frozen_inputs_pass(policy_fixture):
    root,model,p=policy_fixture
    assert verify_policy(p,root,root/'config',root/'data',model)

@pytest.mark.parametrize('field,value',[('baseline','other'),('threshold',.5),('budgets',[.2]),('features',[]),('split_seed',1),('metrics',[]),('pooled_ties',[])])
def test_changed_policy_rejected(policy_fixture,field,value):
    root,model,p=policy_fixture;p[field]=value
    with pytest.raises(ValueError):verify_policy(p,root,root/'config',root/'data',model)

@pytest.mark.parametrize('file',['code.py','config','data','model/metadata'])
def test_changed_inputs_rejected(policy_fixture,file):
    root,model,p=policy_fixture;(root/file).write_text('changed')
    with pytest.raises(ValueError):verify_policy(p,root,root/'config',root/'data',model)

def test_policy_specific_approval(tmp_path):
    policy=tmp_path/'policy.json';policy.write_text('{}')
    approval=tmp_path/'approval.json';approval.write_text(json.dumps(dict(action='APPROVE_ONE_FINAL_TEST_EVALUATION',policy_sha256=checksum(policy),approved_by='synthetic fixture',approved_at='fixture')))
    assert verify_authorization(approval,policy)
    policy.write_text('{"changed":true}')
    with pytest.raises(ValueError):verify_authorization(approval,policy)

def test_no_implicit_approval(tmp_path):
    policy=tmp_path/'policy.json';policy.write_text('{}');approval=tmp_path/'approval.json';approval.write_text('{}')
    with pytest.raises(ValueError):verify_authorization(approval,policy)

def test_once_only_lock_survives_failure(tmp_path):
    reserve_once(tmp_path)
    with pytest.raises(FileExistsError):reserve_once(tmp_path)
    assert (tmp_path/'FINAL_TEST_ATTEMPT.lock').exists()

def test_existing_result_cannot_be_replaced(tmp_path):
    (tmp_path/'final_test.json').write_text('{}')
    with pytest.raises(ValueError):reserve_once(tmp_path)

def test_guards_precede_spark_and_no_legacy_selection():
    s=Path('scripts/final_test.py').read_text()
    assert s.index('verify_authorization(args.authorization')<s.index('from pyspark.sql import SparkSession')
    assert s.index('verify_policy(policy,')<s.index('from pyspark.sql import SparkSession')
    assert 'selection.json' not in s and 'threshold_metrics' not in s
