import math
from pyspark.sql import functions as F
from .features import TARGET

def ceiling_context(n, positives, screened, captured, budget):
    if n <= 0 or positives < 0 or positives > n or not 0 < budget <= 1:
        raise ValueError("Invalid population or budget")
    if not 0 <= captured <= min(positives, screened) or not 0 <= screened <= n:
        raise ValueError("Invalid captured or screened count")
    prevalence = positives / n
    best = min(1., budget / prevalence) if positives else None
    realized = min(1., screened / positives) if positives else None
    capture = captured / positives if positives else None
    return dict(prevalence=prevalence, best_possible=best,
                share_of_best=capture / best if best else None,
                best_possible_realized=realized,
                share_of_best_realized=capture / realized if realized else None)

def budget_counts(n, positives, screened, captured, budget=None):
    result = dict(number_screened=screened,percent_screened=100*screened/n,violations_captured=captured,capture_rate=captured/positives if positives else 0.,violations_missed=positives-captured,workload_reduction=1-screened/n)
    result.update(ceiling_context(n, positives, screened, captured,
                                 budget if budget is not None else screened/n))
    return result

def budgets(df,score='risk_score',budget_values=(.01,.05,.1,.2)):
    r=df.agg(F.count('*').alias('n'),F.sum(TARGET).alias('p')).first();out=[]
    for b in budget_values:
        k=math.ceil(r.n*b)
        top=df.orderBy(F.desc(score),F.asc('scenario_id'),F.asc('outage_line_id')).limit(k)
        captured=int(top.agg(F.sum(TARGET)).first()[0] or 0)
        out.append(dict(budget=b,score=score,**budget_counts(r.n,int(r.p),k,captured,b)))
    return out
