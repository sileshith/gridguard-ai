import json,shutil
from pathlib import Path
import pytest
from gridguard.reporting import audit_aggregates,references
ROOT=Path(__file__).resolve().parents[1]

def test_published_metric_and_budget_arithmetic():
    assert audit_aggregates(ROOT)['screening_points']==8

def test_budget_corruption_detected(tmp_path):
    target=tmp_path/'results/small';target.mkdir(parents=True)
    for name in ['screening_selected.json','split_summary.json']:shutil.copyfile(ROOT/'results/small'/name,target/name)
    p=target/'screening_selected.json';rows=json.loads(p.read_text());rows[0]['capture_rate']=.99;p.write_text(json.dumps(rows))
    with pytest.raises(AssertionError):audit_aggregates(tmp_path)

def test_bibliography_keys_unique_and_complete():
    refs=references(ROOT)
    assert len(refs)==16
    assert sum(bool(r['doi']) for r in refs.values())==10
    assert all(r['apa'] and r['claim'] and r['verificationurl'].startswith('https://') for r in refs.values())


def test_embedded_png_filter_preserves_notebook_text():
    import importlib.util,base64
    p=ROOT/'scripts/audit_local.py';spec=importlib.util.spec_from_file_location('report_audit',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    payload=base64.b64encode(b'\x89PNG\r\n\x1a\n'+b'fixture image bytes').decode()
    token='AI'+'za'+'A'*35
    document=json.dumps({'cells':[{'source':token,'outputs':[{'data':{'image/png':payload}}]}]})
    filtered=m.text_for_scan(document,'.ipynb')
    assert token in filtered and payload not in filtered

def test_non_png_payload_not_exempted():
    import importlib.util,base64
    p=ROOT/'scripts/audit_local.py';spec=importlib.util.spec_from_file_location('report_audit',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    payload=base64.b64encode(b'plain text fixture').decode()
    document='<img src="data:image/png;base64,'+payload+'">'
    assert m.text_for_scan(document,'.html')==document


def test_fresh_manual_count_audit_and_pending_billing():
    from gridguard.reporting import audit_fresh_cloud
    result=audit_fresh_cloud(ROOT)
    assert result['billing_actual_cost'] is None
    assert result['budget_points_per_series']==1
    assert result['test_scored'] is False
    assert result['raw_cloud_artifacts_locally_reviewed'] is False

def test_fresh_confusion_corruption_detected(tmp_path):
    from gridguard.reporting import audit_fresh_cloud
    target=tmp_path/'results/dataproc_1m_manual'
    shutil.copytree(ROOT/'results/dataproc_1m_manual',target)
    p=target/'rf/metrics.json';m=json.loads(p.read_text());m['TP']+=1;p.write_text(json.dumps(m))
    with pytest.raises(AssertionError):audit_fresh_cloud(tmp_path)

def test_deployment_package_excludes_unlisted_inputs(tmp_path):
    import importlib.util,zipfile
    path=ROOT/'scripts/package_dashboard.py';spec=importlib.util.spec_from_file_location('package_dashboard',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    base=tmp_path/'dashboard/dist';(base/'docs').mkdir(parents=True);(tmp_path/'audit').mkdir()
    for name in m.FILES:
        (base/name).parent.mkdir(parents=True,exist_ok=True)
        (base/name).write_text('sanitized fixture')
    (base/'report.html').write_text('not approved for this bundle')
    m.package(tmp_path)
    with zipfile.ZipFile(tmp_path/'dashboard/gridguard-dashboard-deployment.zip') as z:
        assert set(z.namelist())==set(m.FILES)
        assert 'report.html' not in z.namelist()


def test_cover_embedding_preserves_prose_and_png_and_is_idempotent():
    import base64,re
    from gridguard.reporting import embed_cover
    image=(ROOT/'results/figures/publication_architecture.png').read_bytes()
    cover={'source':'Before\n![Private-data screening architecture](attachment:publication_architecture.png)\nAfter', 'attachments':{'publication_architecture.png':{'image/png':base64.b64encode(image).decode()},'other':{'text/plain':'preserved'}}}
    embed_cover(cover,image)
    assert cover['source'].startswith('Before\n<img ') and cover['source'].endswith('\nAfter')
    assert base64.b64decode(re.search(r'data:image/png;base64,([A-Za-z0-9+/=]+)',cover['source'])[1],validate=True)==image
    assert cover['attachments']=={'other':{'text/plain':'preserved'}}
    first=cover['source'];embed_cover(cover,image);assert cover['source']==first

def test_cover_embedding_rejects_missing_image_or_bad_bytes():
    from gridguard.reporting import embed_cover
    with pytest.raises(ValueError):embed_cover({'source':'No image'},b'not a PNG')
    with pytest.raises(ValueError):embed_cover({'source':'No image'},b'\x89PNG\r\n\x1a\nfixture')

def test_notebook_inline_png_scan_preserves_surrounding_secrets():
    import importlib.util,base64
    p=ROOT/'scripts/audit_local.py';spec=importlib.util.spec_from_file_location('cover_audit',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    payload=base64.b64encode(b'\x89PNG\r\n\x1a\nfixture').decode()
    token='AI'+'za'+'A'*35
    text=json.dumps({'cells':[{'source':['<img src="data:image/png;base64,'+payload+'">',token]}]})
    filtered=m.text_for_scan(text,'.ipynb');assert payload not in filtered and token in filtered
