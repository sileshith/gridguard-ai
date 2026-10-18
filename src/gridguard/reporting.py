"""Publication-safe aggregate rendering. Never trains or reads canonical records."""
import json, re, hashlib
from pathlib import Path
from .features import FEATURES, METADATA, TARGET

def load_json(root, name):
    return json.loads((Path(root)/name).read_text())

def references(root):
    text=(Path(root)/'references.bib').read_text()
    return {key:dict(re.findall(r'^  (\w+) = \{(.*)\},$',body,re.M)) for key,body in re.findall(r'@\w+\{(\w+),\n(.*?)\n\}',text,re.S)}

def table(records, columns=None):
    if not records:return 'No records.'
    columns=columns or list(records[0])
    def fmt(v):
        if isinstance(v,float):return f'{v:.6g}'
        return str(v).replace('|','/').replace('\n',' ')
    return '| '+' | '.join(columns)+' |\n|'+'|'.join(['---']*len(columns))+'|\n'+''.join('| '+' | '.join(fmt(r.get(c,'')) for c in columns)+' |\n' for r in records)

def metric_rows(root):
    return [dict(dataset=size,model=model,evidence='REPRODUCED',**load_json(root,f'results/{size}/{model}/metrics.json')) for size in ['small','big'] for model in ['lr','rf','gbt']]

def screening_rows(root):
    rows = load_json(root,'results/small/screening_selected.json')
    from .screening import ceiling_context
    return [dict(row, **ceiling_context(7651, 872, row['number_screened'],
                row['violations_captured'], row['budget'])) for row in rows]

def audit_aggregates(root):
    rows=screening_rows(root);split=load_json(root,'results/small/split_summary.json')['validation']
    for row in rows:
        assert row['number_screened']<=split['rows']
        assert row['violations_captured']+row['violations_missed']==split['positive_count']
        assert abs(row['capture_rate']-row['violations_captured']/split['positive_count'])<1e-12
        assert abs(row['percent_screened']-100*row['number_screened']/split['rows'])<1e-12
    for row in metric_rows(root)+load_json(root,'results/small/thresholds_selected.json'):
        assert abs(row['recall']-row['TP']/(row['TP']+row['FN']))<1e-12
        assert abs(row['precision']-row['TP']/(row['TP']+row['FP']))<1e-12
        assert abs(row['F1']-2*row['precision']*row['recall']/(row['precision']+row['recall']))<1e-12
    return dict(screening_points=len(rows),metric_tables=6,threshold_points=10,aggregate_arithmetic='passed',training_executed=False)

def figures(root):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mtick
    import numpy as np
    root=Path(root);dest=root/'results/figures';dest.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','axes.titlesize':15,'figure.facecolor':'#fbfaf7','axes.facecolor':'#fbfaf7','savefig.facecolor':'#fbfaf7','svg.hashsalt':'gridguard','svg.fonttype':'none'})
    blue='#0072B2';orange='#D55E00';gray='#64748b';gold='#A67C00';files=[]
    def save(fig,name,source):
        fig.text(.02,.015,source,fontsize=8,color='#475569');fig.tight_layout(rect=(0,.06,1,1))
        for ext in ['png','svg']:fig.savefig(dest/(name+'.'+ext),dpi=160,metadata={'Creator':'GridGuard AI'})
        plt.close(fig);files.append(dict(name=name,source=source,sha256=hashlib.sha256((dest/(name+'.png')).read_bytes()).hexdigest()))
    rows=screening_rows(root);fig,ax=plt.subplots(figsize=(9,5.2))
    for score,label,color,marker in [('risk_score','Selected GBT',blue,'o'),('Pre_Outage_Line_Loading','Loading-only baseline',orange,'s')]:
        r=[x for x in rows if x['score']==score];ax.plot([x['percent_screened'] for x in r],[100*x['capture_rate'] for x in r],marker=marker,color=color,lw=2.4,label=label)
        for x in r:ax.annotate(f"{100*x['capture_rate']:.1f}%",(x['percent_screened'],100*x['capture_rate']),xytext=(0,8 if score=='risk_score' else -17),textcoords='offset points',ha='center',fontsize=9)
    ax.set(title='At a 20% review budget, GBT captures 95.18% of modeled violations',xlabel='Contingencies screened (% of validation rows)',ylabel='Modeled violations captured (%)',xlim=(0,22),ylim=(0,105));ax.set_xticks([1,5,10,20]);ax.grid(axis='y',alpha=.2);ax.legend(loc='lower right');save(fig,'screening_budget','Enhanced 50K validation: 7,651 rows, 872 positives. Four measured budgets; lines guide the eye.')
    fig,ax=plt.subplots(figsize=(8,4));values=[5732,44268];bars=ax.barh(['Modeled violation','No modeled violation'],values,color=[orange,blue]);ax.bar_label(bars,labels=['5,732 (11.464%)','44,268 (88.536%)'],padding=6);ax.set(xlim=(0,55000),xlabel='Canonical 50K observations (count)',title='The positive class represents 11.464% of observations');save(fig,'class_balance','Reproduced canonical aggregate validation. Labels describe a synthetic retained population.')
    fig,ax=plt.subplots(figsize=(8.8,4.8));x=np.arange(3);width=.24
    m=[load_json(root,f'results/small/{n}/metrics.json') for n in ['lr','rf','gbt']]
    for i,(key,label,c) in enumerate([('PR_AUC','PR-AUC',blue),('recall','Recall at 0.5',orange),('F1','F1 at 0.5',gold)]):ax.bar(x+(i-1)*width,[r[key] for r in m],width,label=label,color=c)
    ax.set(xticks=x,xticklabels=['LR','RF','GBT'],ylim=(0,1.07),ylabel='Metric (0–1)',title='GBT leads these fixed 50K validation baselines');ax.legend(ncol=3,loc='upper center');save(fig,'model_comparison','Reproduced 50K validation; same split/features. Baseline defaults, not equal tuning budgets.')
    th=load_json(root,'results/small/thresholds_selected.json');fig,ax=plt.subplots(figsize=(8,4.7));s=sorted(th,key=lambda r:r['recall']);ax.plot([r['recall'] for r in s],[r['precision'] for r in s],marker='o',color=blue,label='10 measured thresholds');ax.axhline(872/7651,color=gray,ls='--',label='Validation prevalence');ax.set(xlim=(0,1),ylim=(0,1.05),xlabel='Recall (fraction of positives)',ylabel='Precision (fraction of flagged rows)',title='Selected GBT precision-recall operating points');ax.legend();save(fig,'precision_recall','Enhanced 50K validation, thresholds 0.05–0.90. Sampled trade-off, not a full PR curve or AUC reconstruction.')
    op=load_json(root,'results/small/final_test.json')['operating'];fig,ax=plt.subplots(figsize=(6.2,4.7));a=np.array([[op['TN'],op['FP']],[op['FN'],op['TP']]])
    from matplotlib.colors import ListedColormap
    # Coordinated outcome tints; color identifies the cell, not count magnitude.
    ax.imshow([[0,1],[2,3]],cmap=ListedColormap(['#bdd7e7','#edf0f2','#e0edf5','#cde4f0']),vmin=0,vmax=3)
    for i in range(2):
        for j in range(2):ax.text(j,i,f"{['TN','FP','FN','TP'][i*2+j]}\n{a[i,j]:,}",ha='center',va='center',color='#0f172a',fontsize=16)
    ax.set(xticks=[0,1],xticklabels=['No violation','Violation'],yticks=[0,1],yticklabels=['No violation','Violation'],xlabel='Predicted class',ylabel='Modeled class',title='Frozen 50K test at threshold 0.4');save(fig,'confusion_matrix','Prior enhanced test receipt: 7,522 rows. Historical test prevalence was inspected; not a pristine holdout.')
    fig,(ax,bx)=plt.subplots(1,2,figsize=(10,4.5));x=[r['threshold'] for r in th]
    ax.plot(x,[100*r['recall'] for r in th],'-o',color=blue,label='Recall');ax.plot(x,[100*r['precision'] for r in th],'--s',color=orange,label='Precision');ax.plot(x,[r['percent_flagged'] for r in th],':^',color=gray,label='Flagged workload');ax.set(xlabel='Risk threshold (0–1)',ylabel='Percentage (%)',title='Quality and review workload');ax.legend(fontsize=9)
    bx.plot(x,[r['FN'] for r in th],'-o',color=orange);bx.axvline(.4,color=gray,ls='--');bx.set(xlabel='Risk threshold (0–1)',ylabel='Missed modeled violations (count)',title='Higher thresholds miss more positives');save(fig,'threshold_tradeoff','Enhanced validation only. Max-F1 selection chose 0.4 on this finite grid, not a safety-cost optimum.')
    fig,ax=plt.subplots(figsize=(8.5,4.6));x=np.arange(3)
    for i,(size,label,c) in enumerate([('small','50K local',blue),('big','1M local',orange)]):ax.bar(x+(i-.5)*.35,[load_json(root,f'results/{size}/{n}/metrics.json')['PR_AUC'] for n in ['lr','rf','gbt']],.35,label=label,color=c)
    ax.set(xticks=x,xticklabels=['LR','RF','GBT'],ylabel='Validation PR-AUC (0–1)',ylim=(0,1.08),title='50K and 1M are separate local evidence states');ax.legend();save(fig,'scaling_results','Reproduced local runs. Different populations; no causal data-size benefit, runtime speedup or cloud claim.')
    fig,ax=plt.subplots(figsize=(10,4.7));ax.axis('off');ax.set_title('Keep every outage from a scenario in one partition',pad=16)
    for row,label in enumerate(['Row-level split: leakage risk','Scenario split: implemented']):
        ax.text(0,2-row*1.4,label,fontsize=11,weight='bold')
        for j in range(9):
            group=j//3;color=[blue,orange,gold][j%3 if row==0 else group];ax.text(.4+j*1.03,1.5-row*1.4,f'S{group+1} / O{j%3+1}',ha='center',va='center',bbox=dict(boxstyle='round,pad=.4',fc=color,ec='none'),color='white',fontsize=9)
    ax.text(.1,-.5,'Color encodes partition: blue training | orange validation | gold test. S/O are illustrative IDs.',fontsize=9);ax.set(xlim=(-.2,9.5),ylim=(-.8,2.4));save(fig,'grouped_split','Design illustration, not observed records. Actual split assertions are implemented in gridguard.splitting.')
    fig,ax=plt.subplots(figsize=(11,5.2));ax.axis('off');ax.set_title('GridGuard AI: private-data screening, public evidence',pad=14)
    nodes=[('Private canonical data','Scenario + candidate outage'),('Validate and group','Nine pre-outage predictors'),('Spark ML pipeline','Score and rank candidates'),('Screening budget','Detailed engineering review'),('Public aggregates','Dashboard + GridRail guide')]
    for i,(title,sub) in enumerate(nodes):
        y=.88-i*.18;ax.text(.5,y,title+'\n'+sub,ha='center',va='center',bbox=dict(boxstyle='round,pad=.5',fc='#f2e7dc' if i!=2 else '#e2eff6',ec='#64748b'),fontsize=11)
        if i<4:ax.annotate('',xy=(.5,y-.11),xytext=(.5,y-.06),arrowprops=dict(arrowstyle='->',color=gray))
    ax.text(.02,.025,'Implemented local pipeline; operational review and live hosting remain proposed/manual.',fontsize=9);save(fig,'publication_architecture','Conceptual project architecture. No utility topology or private records. GridRail receives documentation only.')
    (root/'audit/FIGURE_MANIFEST.json').write_text(json.dumps({'figures':files,'full_pr_curve_available':False,'feature_importance_available':False,'notes':'Sampled threshold points replace unavailable score-level PR curve; feature importance omitted. No new training or test scoring.'},indent=2)+'\n')
    return files


def integrity_profile(path):
    """Read authorized local input, emit aggregate integrity only, never rows/paths."""
    import csv, math
    from .validation import validate_csv
    result=validate_csv(path,expected_rows=50000)
    ranges={k:[float('inf'),float('-inf')] for k in FEATURES};missing={};rows=0
    with open(path,newline='') as source:
        reader=csv.DictReader(source);columns=reader.fieldnames;missing={k:0 for k in columns}
        for row in reader:
            rows+=1
            for k in columns:missing[k]+=int(row[k]=='')
            for k in FEATURES:
                v=float(row[k]);assert math.isfinite(v);ranges[k]=[min(ranges[k][0],v),max(ranges[k][1],v)]
    result.update(column_count=len(columns),columns=columns,missing_cells=sum(missing.values()),missing_by_column=missing,predictor_ranges=ranges,duplicate_scenario_outage_pairs=0,target_validity='binary 0/1',metadata_excluded=METADATA,predictors=FEATURES,evidence_state='REPRODUCED',scope='New read-only 50K integrity audit, no training or scoring; ranges are benchmark summaries, not operational bounds.')
    return result


def fresh_cloud(root):
    base='results/dataproc_1m_manual/'
    return {'evidence':load_json(root,base+'evidence.json'),'metrics':{m:load_json(root,base+m+'/metrics.json') for m in ['lr','rf','gbt']},'screening':load_json(root,base+'screening.json'),'thresholds':load_json(root,base+'thresholds.json')}

def audit_fresh_cloud(root):
    cloud=fresh_cloud(root);e=cloud['evidence'];n=e['split_summary']['validation']['rows'];p=17739
    assert e['test_evaluated'] is False and not any(e['pairwise_scenario_overlaps'].values())
    assert e['billing']['actual_run_cost_usd'] is None and e['billing']['status']=='PENDING BILLING FINALIZATION'
    for m in cloud['metrics'].values():
        assert sum(m[k] for k in ['TP','FP','FN','TN'])==n
        assert m['TP']+m['FN']==p
        assert abs(m['precision']-m['TP']/(m['TP']+m['FP']))<1e-9
        assert abs(m['recall']-m['TP']/p)<1e-9
        assert abs(m['F1']-2*m['TP']/(2*m['TP']+m['FP']+m['FN']))<1e-9
    assert len(cloud['screening'])==2 and {r['budget'] for r in cloud['screening']}=={.2}
    for r in cloud['screening']:
        assert r['violations_captured']+r['violations_missed']==p
        assert abs(r['capture_rate']-r['violations_captured']/p)<1e-12
        assert r['number_screened']==30621 and r['percent_screened']==20
    return {'models':3,'confusion_count_checks':'passed','budget_points_per_series':1,'threshold_points':2,'billing_actual_cost':None,'test_scored':False,'raw_cloud_artifacts_locally_reviewed':False}

def fresh_figures(root):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    root=Path(root);c=fresh_cloud(root);dest=root/'results/figures';records=[]
    blue='#0072B2';orange='#D55E00';gray='#64748b'
    def save(fig,name,note,top=1):
        fig.text(.02,.01,note,fontsize=8,color='#475569');fig.tight_layout(rect=(0,.07,1,top))
        for ext in ['png','svg']:fig.savefig(dest/(name+'.'+ext),dpi=160,metadata={'Creator':'GridGuard AI'})
        plt.close(fig);records.append({'name':name,'source':'User-supplied manually verified October 2026 cloud aggregates','sha256':hashlib.sha256((dest/(name+'.png')).read_bytes()).hexdigest(),'coverage_note':note})
    hist={'PR_AUC':[.8542,.8736,.9262],'recall':[.6918,.6585,.7829],'F1':[.7531,.7687,.8483]};names=['lr','rf','gbt'];fig,axes=plt.subplots(1,3,figsize=(12,4.3));x=np.arange(3)
    for ax,key in zip(axes,['PR_AUC','recall','F1']):
        ax.bar(x-.18,hist[key],.36,label='Historical',color=gray);ax.bar(x+.18,[c['metrics'][m][key] for m in names],.36,label='Fresh Dataproc',color=blue)
        ax.set(xticks=x,xticklabels=['LR','RF','GBT'],ylabel='Metric (0–1)',ylim=(0,1),title=key.replace('_','-'));ax.grid(axis='y',alpha=.15)
    handles,labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.5,.9),ncol=2,fontsize=9,frameon=False)
    fig.suptitle('Fresh cloud reproduction preserves the model ranking, with an RF discrepancy',fontsize=15,weight='bold')
    # Reserve a separate header band for the shared legend above all three panels.
    save(fig,'dataproc_historical_comparison','Historical rounded targets vs fresh validation. Runtime/implementation differ; exact RF cause not isolated.',top=.73)
    fig,ax=plt.subplots(figsize=(9,4.8));rows=c['screening'];bars=ax.barh(['GBT risk ranking','Loading-only baseline'],[100*r['capture_rate'] for r in rows],color=[blue,orange]);ax.invert_yaxis();ax.bar_label(bars,labels=[f"{100*r['capture_rate']:.2f}% ({r['violations_captured']:,}/{17739:,})" for r in rows],padding=5);ax.set(xlim=(0,123),xlabel='Modeled validation violations captured (%)',title='At 20% review, fresh GBT captures 94.77% versus 78.78%');ax.set_xticks([0,20,40,60,80,100]);save(fig,'dataproc_screening_20pct','Fresh 1M validation: 30,621/153,105 rows reviewed. Only 20% supplied; no lower-budget curve invented.')
    fig,ax=plt.subplots(figsize=(9,4.8));rows=c['thresholds'];x=[r['threshold'] for r in rows]
    for key,label,color,mark in [('recall','Recall',blue,'o'),('precision','Precision',orange,'s'),('F1','F1','#8c1d40','^'),('percent_flagged','Flagged workload',gray,'D')]:
        y=[r[key] if key=='percent_flagged' else 100*r[key] for r in rows];ax.plot(x,y,marker=mark,color=color,label=label,lw=2)
    ax.set(xticks=x,xlim=(.38,.52),ylim=(0,100),xlabel='Risk threshold (0–1)',ylabel='Percentage (%)',title='Fresh validation: threshold 0.4 recovers more positives than 0.5');ax.legend(ncol=2);ax.grid(axis='y',alpha=.2);save(fig,'dataproc_threshold_tradeoff','Two supplied validation operating points; connecting segments guide the eye. No fresh test evaluation.')
    (root/'audit/FRESH_CLOUD_FIGURES.json').write_text(json.dumps({'figures':records,'complete_budget_curve':False,'complete_threshold_curve':False},indent=2)+'\n');return records


def embed_cover(cover, image_bytes):
    """Embed only the named cover visual as HTML; preserve prose and other attachments."""
    import base64, re
    if not image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Cover must contain PNG bytes")
    source=cover["source"]
    if isinstance(source,list):source="".join(source)
    tag='<img src="data:image/png;base64,'+base64.b64encode(image_bytes).decode('ascii')+'" alt="Private-data screening architecture" style="display:block;max-width:100%;height:auto;margin:1rem auto;" />'
    pattern=r'!\[Private-data screening architecture\]\((?:attachment:|\.\./results/figures/)publication_architecture\.png\)|<img src="data:image/png;base64,[A-Za-z0-9+/=]+" alt="Private-data screening architecture"[^>]*>'
    updated,count=re.subn(pattern,lambda _:tag,source)
    if count!=1:raise ValueError("Expected exactly one recognized cover image")
    cover["source"]=updated
    attachments=cover.get("attachments",{})
    attachments.pop("publication_architecture.png",None)
    if not attachments:cover.pop("attachments",None)
    return cover
