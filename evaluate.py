import json
from core import run_offline
CASES=[('forgot password','account'),('login failed','account'),('deposit pending','transaction'),('payment missing','transaction'),('fee information','general'),('help hours','general'),('unauthorized transfer','escalation'),('stolen account','escalation'),('unrecognized question','unknown'),('hello','unknown')]
def evaluate():
    rows=[{'message':m,'expected':e,'actual':run_offline({'messages':[m]})['intent']} for m,e in CASES]
    return {'scope':'authored synthetic rule-aligned smoke cases; not generalization','correct':sum(r['expected']==r['actual'] for r in rows),'total':len(rows),'rows':rows}
if __name__=='__main__': print(json.dumps(evaluate(),indent=2))
