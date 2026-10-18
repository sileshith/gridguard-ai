from pathlib import Path
from gridguard.reporting import figures,audit_aggregates,fresh_figures,audit_fresh_cloud
if __name__=='__main__':
 root=Path(__file__).resolve().parents[1]
 print(audit_aggregates(root))
 print('Generated',len(figures(root)),'figures from sanitized aggregates')

 print(audit_fresh_cloud(root))
 print("Generated",len(fresh_figures(root)),"fresh cloud figures")
