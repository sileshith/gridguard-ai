"""Create static figures only from generated local result records."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/gridguard-matplotlib')
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
    out=Path('results/figures');out.mkdir(parents=True,exist_ok=True)
    for size in ['small','big']:
        root=Path('results')/size
        if not (root/'manifest.json').exists():continue
        metrics=[json.loads((root/m/'metrics.json').read_text()) for m in ['lr','rf','gbt']]
        fig,axes=plt.subplots(1,2,figsize=(11,4.4),constrained_layout=True)
        colors=['#5f758e','#2f8b8c','#dc8734']
        for i,(m,name,c) in enumerate(zip(metrics,['LR','RF','GBT'],colors)):
            axes[0].bar(i,m['PR_AUC'],color=c,width=.65)
            axes[0].text(i,m['PR_AUC']+.012,f"{m['PR_AUC']:.4f}",ha='center',fontsize=10)
        axes[0].set(xticks=range(3),xticklabels=['LR','RF','GBT'],ylim=(0,1.05),ylabel='Validation PR-AUC',title='Scenario-grouped model comparison')
        screen=json.loads((root/'screening.json').read_text())
        for key,label,c in [('risk_score','GBT risk score','#dc8734'),('Pre_Outage_Line_Loading','Pre-outage loading','#5f758e')]:
            rows=[x for x in screen if x['score']==key]
            axes[1].plot([x['percent_screened'] for x in rows],[100*x['capture_rate'] for x in rows],marker='o',label=label,color=c)
        axes[1].set(xlabel='Cases reviewed (%)',ylabel='Modeled violations captured (%)',ylim=(0,105),title='Screening budget comparison')
        axes[1].legend(frameon=False,loc='lower right')
        for ax in axes:ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
        fig.suptitle(f'GridGuard AI — {size} canonical dataset, local reproduction',fontsize=13)
        fig.savefig(out/(size+'_validation.png'),dpi=180);fig.savefig(out/(size+'_validation.svg'));plt.close(fig)
if __name__=='__main__':main()
