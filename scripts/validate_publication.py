"""Bounded notebook, citation, HTML and cross-surface checks. No network/data reads."""
import json,re,csv,hashlib
from pathlib import Path
import nbformat
from bs4 import BeautifulSoup
from gridguard.reporting import references,audit_aggregates,audit_fresh_cloud,load_json

def check(root):
    root=Path(root);notebook=nbformat.read(root/'notebooks/00_gridguard_ai_flagship_report.ipynb',as_version=4);nbformat.validate(notebook)
    markdown='\n'.join(c.source for c in notebook.cells if c.cell_type=='markdown');refs=references(root)
    assert len(refs)==16
    matrix=list(csv.DictReader((root/'docs/LITERATURE_MATRIX.csv').open()))
    assert {r['citation_key'] for r in matrix}==set(refs)
    for row in matrix:
        ref=refs[row['citation_key']];assert ref['apa']==row['apa_citation'];assert ref['doi']==row['doi']
        assert ref['short'] in markdown, row['citation_key']
        assert ref['short'] in (root/'docs/LITERATURE_REVIEW.md').read_text()
    doi=load_json(root,'audit/DOI_METADATA_CHECKS.json');assert len(doi)==10 and all(r['status']=='verified DOI registration metadata' for r in doi)
    for item in doi:assert item['doi'].casefold()==refs[item['key']]['doi'].casefold()
    anchors=re.findall(r'<a id="([^"]+)"',markdown);assert len(anchors)==len(set(anchors))
    sections=notebook.metadata.gridguard.main_anchors
    assert len(sections)==13 and sections.index("modeling")<sections.index("model-evaluation")
    assert markdown.count('[Back to Top](#scrollTo=gridguard-cover)')==len(sections)
    for target in re.findall(r'\]\(#([^)]+)\)',markdown):
        if target.startswith('scrollTo='):
            assert any(c.get('id')==target[9:] and c.metadata.get('id')==target[9:] for c in notebook.cells),target
        else:assert target in anchors,target
    for c in notebook.cells:
        if c.cell_type=='code':
            assert c.execution_count is not None
            assert not any(o.output_type=='error' for o in c.outputs)
        assert '—' not in c.source
    html=(root/'reports/GridGuard_AI_Flagship_Report.html').read_text();soup=BeautifulSoup(html,'html.parser');ids={e.get('id') for e in soup.find_all(id=True)}
    assert set(anchors).issubset(ids)
    for a in soup.select('a[href^="#"]'):assert a['href'][1:] in ids,a['href']
    images=soup.find_all('img');assert len(images)>=9 and all(i.get('src','').startswith('data:image/') for i in images)
    assert not soup.find_all('script'), 'Offline HTML must not fetch scripts'
    readme=(root/'README.md').read_text();assert '—' not in readme and not re.search(r'^---+$',readme,re.M)
    assert readme.index('local_validation_capture.png')<readme.index('## Reproducibility')
    assert 'Sileshi T. Hirpa' in markdown and 'October 2026' in markdown and 'Arizona State University' in markdown
    assert 'POLICY FROZEN / FINAL TEST UNEVALUATED' in readme
    assert (root/'docs/assets/gridguard-ai-dashboard-preview.png').is_file()
    # Shared dashboard/report rows must be identical, not manually transcribed approximations.
    for size in ['small','big','cloud']:
        dashboard=load_json(root,'dashboard/dist/data.json')[size]
        base='results/dataproc_1m_manual' if size=='cloud' else f'results/{size}'
        assert dashboard['screening']==load_json(root,base+'/screening.json')
        for model in ['lr','rf','gbt']:assert dashboard['metrics'][model]==load_json(root,f'{base}/{model}/metrics.json')
    assert load_json(root,'results/small/screening.json')==load_json(root,'results/small/screening_selected.json')
    checks=dict(citation_sources=len(refs),verified_doi_records=len(doi),citation_matrix_consistent=True,main_sections=len(sections),back_to_top_links=len(sections),appendices=10,unique_anchors=len(anchors),html_embedded_images=len(images),html_internal_links_valid=True,notebook_valid=True,notebook_code_cells_executed=sum(c.cell_type=="code" for c in notebook.cells),notebook_errors=0,readme_visual_hook=True,shared_dashboard_aggregate_parity=True,aggregate_arithmetic=audit_aggregates(root),fresh_cloud_audit=audit_fresh_cloud(root),github_renderer_tested=False,github_note='GitHub rendering is checked separately after publication. Notebook figures use embedded PNG data and the cover uses an inline data URI.')
    (root/'audit/PUBLICATION_REPORT_CHECKS.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks,indent=2));return checks
if __name__=='__main__':check(Path(__file__).resolve().parents[1])
