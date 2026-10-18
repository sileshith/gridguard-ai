"""Render tables from generated JSON; never fill missing experiment results."""
import json,csv
from pathlib import Path

def table(path,rows):
    if not rows:return
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.with_suffix('.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    def fmt(v):return f'{v:.6f}' if isinstance(v,float) else str(v)
    columns=list(rows[0]);path.with_suffix('.md').write_text('| '+' | '.join(columns)+' |\n| '+' | '.join(['---']*len(columns))+' |\n'+''.join('| '+' | '.join(fmt(r.get(c,'')) for c in columns)+' |\n' for r in rows))

def main():
    root=Path('results')
    for size in ['small','big']:
        base=root/size;metrics=[]
        for name in ['lr','rf','gbt','gbt_tuned']:
            p=base/name/'metrics.json'
            if p.exists():metrics.append(dict(model=name,**json.loads(p.read_text())))
        table(root/'tables'/f'{size}_model_metrics',metrics)
        for name in ['thresholds','screening','thresholds_selected','screening_selected']:
            p=base/(name+'.json')
            if p.exists():table(root/'tables'/f'{size}_{name}',json.loads(p.read_text()))
        p=base/'historical_comparison.json'
        if p.exists():table(root/'tables'/f'{size}_historical_comparison',[dict(model=n,metric=k,**v) for n,ms in json.loads(p.read_text()).items() for k,v in ms.items()])
if __name__=='__main__':main()
