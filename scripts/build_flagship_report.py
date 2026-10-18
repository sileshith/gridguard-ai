"""Execute the canonical aggregate notebook in a fresh kernel and export embedded HTML."""
import json,os,tempfile,sys,hashlib
from pathlib import Path
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
from jupyter_client import AsyncKernelManager

class IPCKernelManager(AsyncKernelManager):
    def __init__(self,*args,**kwargs):
        kwargs["transport"]="ipc"
        super().__init__(*args,**kwargs)

def build(root=None):
    root=Path(root or Path(__file__).resolve().parents[1]);path=root/'notebooks/00_gridguard_ai_flagship_report.ipynb'
    notebook=nbformat.read(path,as_version=4);nbformat.validate(notebook)
    for cell in notebook.cells:
        if cell.cell_type=='code':cell.outputs=[];cell.execution_count=None
    # Inline HTML data URI avoids reliance on frontend Markdown-attachment support.
    # Code-generated scientific figures remain preserved notebook outputs.
    from gridguard.reporting import embed_cover
    embed_cover(notebook.cells[0],(root/'results/figures/publication_architecture.png').read_bytes())
    with tempfile.TemporaryDirectory(prefix='gridguard-kernel-') as temporary:
        kernel=Path(temporary)/'kernels/gridguard-report';kernel.mkdir(parents=True)
        (kernel/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'GridGuard report','language':'python'}))
        previous=os.environ.get('JUPYTER_PATH');os.environ['JUPYTER_PATH']=temporary+(os.pathsep+previous if previous else '')
        try:
            NotebookClient(notebook,timeout=180,kernel_manager_class=IPCKernelManager,kernel_name='gridguard-report',resources={'metadata':{'path':str(root)}},allow_errors=False).execute()
        finally:
            if previous is None:os.environ.pop('JUPYTER_PATH',None)
            else:os.environ['JUPYTER_PATH']=previous
    nbformat.validate(notebook);nbformat.write(notebook,path)
    exporter=HTMLExporter(template_name='lab',embed_images=True)
    html,_=exporter.from_notebook_node(notebook,resources={'metadata':{'path':str(path.parent)}})
    # Offline static report needs no external JS, font, MathJax or CDN dependency.
    import re
    html=html.replace('href="#scrollTo=gridguard-cover"', 'href="#top"')
    html=re.sub(r' ?· ?<a href="#top">HTML/Jupyter</a>', '', html)
    html=re.sub(r'<script\b[^>]*>.*?</script>', '',html,flags=re.S|re.I)
    html=re.sub(r'<link\b[^>]*href=["\']https?://[^>]*>', '',html,flags=re.I)
    css='<style>body{background:#fbfaf7}h1,h2{color:#8c1d40}a{color:#006b9c}img{max-width:100%;height:auto}html{scroll-behavior:smooth}.jp-InputArea{font-size:12px}table{font-size:13px}section{scroll-margin-top:1rem}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}.jp-RenderedHTMLCommon{overflow-x:auto}.jp-InputArea-editor pre{white-space:pre-wrap}</style>'
    html=html.replace('</head>',css+'</head>');reports=root/'reports';reports.mkdir(exist_ok=True);output=reports/'GridGuard_AI_Flagship_Report.html';output.write_text(html)
    from importlib.metadata import version
    receipt={'report_environment':{name:version(name) for name in ['nbformat','nbclient','nbconvert','ipykernel','matplotlib','pyspark','PyYAML']},'mode':'aggregate-only fresh-kernel execution','code_cells':sum(c.cell_type=='code' for c in notebook.cells),'errors':sum(o.output_type=='error' for c in notebook.cells if c.cell_type=='code' for o in c.outputs),'training_executed':False,'new_final_test_scoring':False,'html_exported':True,'html_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'notebook_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pdf_exported':False,'pdf_note':'No established reliable PDF workflow; optional PDF omitted.'}
    (root/'audit/NOTEBOOK_EXECUTION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':build()
