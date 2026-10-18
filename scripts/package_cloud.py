"""Build a deterministic source ZIP for the approved future cloud job."""
import hashlib,zipfile
from pathlib import Path

def main():
    root=Path('src');out=Path('infrastructure/dataproc/gridguard.zip');out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted((root/'gridguard').rglob('*.py')):
            info=zipfile.ZipInfo(str(p.relative_to(root)),date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,p.read_bytes())
    digest=hashlib.sha256(out.read_bytes()).hexdigest();out.with_suffix('.zip.sha256').write_text(digest+'  gridguard.zip\n');print(digest)
if __name__=='__main__':main()
