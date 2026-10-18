"""Fail-closed verification for the written budget policy and future test approval."""
import json
from pathlib import Path
from .artifacts import checksum, directory_checksum
from .features import FEATURES

RULE = 'After this freeze, no feature, model, baseline, ranking policy, threshold policy or evaluation metric may be changed based on final-test results.'
METRICS = ['PR_AUC', 'ROC_AUC', 'pooled_capture_10', 'pooled_capture_20',
           'baseline_capture_10', 'baseline_capture_20', 'gain_capture_10', 'gain_capture_20',
           'mean_scenario_recall_10', 'mean_scenario_recall_20',
           'scenario_miss_share_10', 'scenario_miss_share_20']


def verify_policy(policy, root, config_path, data_path, model_path):
    root = Path(root)
    if policy['status'] != 'POLICY_FROZEN' or policy['features'] != FEATURES:
        raise ValueError('Invalid frozen status or features')
    if (policy['model_family'] != 'GBT' or policy['baseline'] != 'Pre_Outage_Line_Loading'
        or policy['primary_policy'] != 'pooled_top_20_percent'
        or policy['secondary_policy'] != 'within_scenario_top_20_percent'
        or policy['budgets'] != [.1,.2] or policy['threshold'] is not None
        or policy['metrics'] != METRICS or policy['governance_rule'] != RULE
        or policy['split_seed'] != 4152026
        or policy['ranking_direction'] != 'descending'
        or policy['pooled_ties'] != ['scenario_id', 'outage_line_id']
        or policy['scenario_ties'] != ['outage_line_id']):
        raise ValueError('Unsupported or altered frozen policy')
    for name, value in policy['source_sha256'].items():
        if checksum(root/name) != value:
            raise ValueError('Frozen analysis code changed')
    if checksum(config_path) != policy['config_sha256'] or checksum(data_path) != policy['data_sha256']:
        raise ValueError('Frozen configuration or data changed')
    if directory_checksum(model_path) != policy['model_content_sha256']:
        raise ValueError('Frozen model changed')
    return True


def verify_authorization(path, policy_path):
    approval = json.loads(Path(path).read_text())
    if (approval.get('action') != 'APPROVE_ONE_FINAL_TEST_EVALUATION'
        or approval.get('policy_sha256') != checksum(policy_path)
        or not approval.get('approved_by') or not approval.get('approved_at')):
        raise ValueError('Separate written approval for this exact policy is required')
    return True


def reserve_once(output):
    output = Path(output)
    if (output/'final_test.json').exists():
        raise ValueError('Final test result already exists')
    # A failed attempt leaves the lock in place for explicit investigation.
    with (output/'FINAL_TEST_ATTEMPT.lock').open('x') as handle:
        handle.write('Reserved once. Do not remove automatically.\n')
