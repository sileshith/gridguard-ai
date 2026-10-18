"""Rebuild the local validation chart from sanitized aggregates only."""
from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
p=Path(__file__).resolve().parents[1]
a=json.loads((p/"results/review_validation_1m/comparison.json").read_text())
r={x["score"]:x for x in a["rankings"]}
g=r["risk_score"]
b=r["Pre_Outage_Line_Loading"]
u=json.loads((p/'results/review_validation_1m/scenario_bootstrap.json').read_text())
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(9,5.7));fig.subplots_adjust(top=.79,bottom=.23,right=.96,left=.1)
x=[z['percent_screened'] for z in g['screening']]
ax.plot(x,[100*z['best_possible_realized'] for z in g['screening']],':',color='#727b83',label='Theoretical ceiling',linewidth=2)
for data,label,color in [(g,'GBT','#0078ad'),(b,'Loading baseline','#697b8c')]:ax.plot(x,[100*z['capture_rate'] for z in data['screening']],'-o',color=color,label=label,linewidth=2)
ax.annotate('+24.6 pp\n95%: +23.2 to +26.0 pp',xy=(10,79),xytext=(10,25),ha='center',fontsize=10,bbox={'facecolor':'white','edgecolor':'none','alpha':.9},arrowprops={'arrowstyle':'->','color':'#324a5e'})
ax.annotate('+16.3 pp\n95%: +15.7 to +16.7 pp',xy=(20,95),xytext=(17,47),ha='center',fontsize=10,bbox={'facecolor':'white','edgecolor':'none','alpha':.9},arrowprops={'arrowstyle':'->','color':'#324a5e'})
for name,color in [('gbt','#0078ad'),('baseline','#697b8c')]:
 for budget in [10,20]:
  key=f'{name}_capture_{budget}';v=u['point_estimates'][key]*100;ci=u['percentile_95_intervals'][key]
  ax.errorbar(budget,v,yerr=[[v-ci['lower']*100],[ci['upper']*100-v]],fmt='none',ecolor=color,capsize=4)
ax.set(xlabel='Validation cases reviewed (%)',ylabel='Modeled violations captured (%)',ylim=(0,105),xticks=[1,5,10,20]);ax.grid(axis='y',alpha=.2)
fig.suptitle('Local validation: higher capture at the same review budget',fontsize=15,fontweight='bold',y=.97)
fig.legend(*ax.get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.5,.91),ncol=3,frameon=False)
fig.text(.1,.06,'153,105 cases across 865 scenarios. Points are measured, lines guide the eye.\nBars: 95% scenario-bootstrap intervals at 10% and 20%. Ceiling uses realized count. Validation only.',fontsize=9,color='#465568')
for ext in ['png','svg']:fig.savefig(p/f'results/figures/local_validation_capture.{ext}',dpi=160)
plt.close(fig)
