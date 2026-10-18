"""Bounded publication checks over Git-visible candidates; no data access/upload."""
import ast,csv,json,re,subprocess,datetime,base64
from pathlib import Path


def text_for_scan(text, suffix):
    # Embedded image bytes are not credential text. Exclude only payloads that
    # decode to actual PNGs; keep source, prose, metadata and other strings.
    def verified_png(value):
        try:return base64.b64decode(value,validate=True).startswith(b"\x89PNG\r\n\x1a\n")
        except (ValueError,TypeError):return False
    if suffix=='.ipynb':
        def clean(value):
            if isinstance(value,dict):return {k:('[verified embedded PNG]' if k=='image/png' and isinstance(v,str) and verified_png(v) else clean(v)) for k,v in value.items()}
            if isinstance(value,list):return [clean(v) for v in value]
            if isinstance(value,str):return text_for_scan(value,'.html')
            return value
        return json.dumps(clean(json.loads(text)))
    if suffix=='.html':
        return re.sub(r'data:image/png;base64,([A-Za-z0-9+/=]+)',lambda m:'data:image/png;base64,[verified embedded PNG]' if verified_png(m[1]) else m[0],text)
    return text

def audit(root=Path('.')):
    root=Path(root).resolve()
    listed=subprocess.run(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=root,capture_output=True,text=True,check=True).stdout.split('\0')
    files=sorted({Path(n) for n in listed if n and (root/n).is_file()})
    patterns={'private_key':r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY','github_token':r'gh[pousr]_[A-Za-z0-9]{20,}','google_key':r'AIza[A-Za-z0-9_-]{30,}','aws_access_key':r'AKIA[A-Z0-9]{16}','personal_path':r'/Users/[A-Za-z0-9._-]+/|/var/folders/[A-Za-z0-9]+','private_email':r'[A-Za-z0-9._%+-]+@(?:gmail|outlook|hotmail|yahoo)\.[A-Za-z]+'}
    issues=[];broken=[];large=[];syntax=[];forbidden=[];symlinks=[]
    canonical={'cis415_grid_small_50000.csv','cis415_grid_big_1000000.csv'}
    for rel in files:
        f=root/rel
        if f.is_symlink():symlinks.append(str(rel))
        if f.stat().st_size>5*1024*1024:large.append(str(rel))
        parts=rel.parts
        if rel.name in canonical or str(rel).startswith(('data/raw/','data/private/','data/sample/','results/local/','private/','audit/logs/','.git/')) or 'model' in parts or (rel.name.startswith('.env') and rel.name!='.env.example') or rel.suffix in ['.parquet','.pkl','.pickle','.joblib']:forbidden.append(str(rel))
        if rel.suffix not in ['.py','.md','.json','.yaml','.yml','.toml','.txt','.csv','.cff','.js','.cjs','.html','.css','.ipynb','.bib','.svg'] and rel.name!='.env.example':continue
        text=f.read_text(errors='replace')
        if rel.suffix=='.py':
            try:ast.parse(text)
            except SyntaxError as e:syntax.append({'file':str(rel),'error':str(e)})
        scan_text=text_for_scan(text,rel.suffix)
        for category,pattern in patterns.items():
            if re.search(pattern,scan_text,re.I):issues.append({'file':str(rel),'category':category})
        if rel.suffix=='.md':
            for link in re.findall(r'\]\(([^)]+)\)',text):
                if '://' not in link and not link.startswith('#') and not (f.parent/link.split('#')[0]).exists():broken.append({'file':str(rel),'link':link})
        if rel.suffix=='.csv':
            with f.open() as h:header=next(csv.reader(h),[])
            if {'scenario_id','outage_line_id'}.issubset(header):forbidden.append(str(rel))
        if rel.name=='.env.example':
            for line in text.splitlines():
                if line.strip() and not line.lstrip().startswith('#') and '=' in line and line.split('=',1)[1].strip():issues.append({'file':str(rel),'category':'nonempty_environment_example'})
    out=dict(timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),candidate_files=len(files),findings=issues,broken_markdown_links=broken,files_over_5MiB=large,syntax_errors=syntax,forbidden_release_inputs=sorted(set(forbidden)),symlinks=symlinks,limitations='Pattern/path/schema checks, not a dedicated secret scanner or full legal/LLM behavior certification. Original screenshots/course artifacts and private content are excluded.')
    (root/'audit/LOCAL_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
    return not any([issues,broken,large,syntax,forbidden,symlinks])
if __name__=='__main__':raise SystemExit(0 if audit() else 1)
