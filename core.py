from typing import TypedDict
import re
class State(TypedDict,total=False):
    messages:list[str]
    intent:str
    route:str
    response:str
    handoff:dict
    trace:list[str]
    pending:bool
def classify(s):
    t=s['messages'][-1].lower()
    for pattern,intent in [(r'fraud|stolen|human|unauthorized|hacked','escalation'),(r'password|login|sign in','account'),(r'transfer|payment|deposit','transaction'),(r'fee|hours|help','general')]:
        if re.search(pattern,t): return {'intent':intent}
    return {'intent':s.get('intent','unknown') if re.search(r'\b(still|same|waiting|again|what about it)\b',t) else 'unknown'}
def route(s):
    return {'account':'internal','transaction':'internal','general':'vendor','escalation':'human','unknown':'human'}[s['intent']]
def internal(s):
    return {'route':'internal','response':{'account':'Use the official account recovery flow.','transaction':'Check transaction status in the official activity page.','general':'Consult the official help center for current policy.'}[s['intent']], 'pending':False,'handoff':{},'trace':s.get('trace',[])+['internal']}
def offline_provider(context):
    return {'action':'internal'}
def vendor(s,provider=offline_provider):
    try:
        result=provider({'intent':s['intent']})
        if result != {'action':'internal'}: raise ValueError('invalid provider contract')
        return {'trace':['vendor','handoff:internal']}
    except (ValueError,TimeoutError,OSError):
        return {'trace':['vendor','fallback:internal']}
def human(s):
    return {'route':'human','response':'Human review required.','pending':True,'trace':['human'],'handoff':{'intent':s['intent'],'turn_count':len(s['messages'])}}
def run_offline(s,provider=offline_provider):
    s={**s,**classify(s),'trace':[],'handoff':{},'pending':False}
    r=route(s)
    if r=='vendor': s.update(vendor(s,provider)); r='internal'
    s.update(internal(s) if r=='internal' else human(s)); return s
def build_graph(provider=offline_provider):
    from langgraph.graph import StateGraph,START,END
    g=StateGraph(State)
    g.add_node('classify',lambda s:{**classify(s),'trace':[],'handoff':{},'pending':False})
    g.add_node('internal',internal); g.add_node('vendor',lambda s:vendor(s,provider)); g.add_node('human',human)
    g.add_edge(START,'classify'); g.add_conditional_edges('classify',route,{k:k for k in ('internal','vendor','human')})
    g.add_edge('vendor','internal'); g.add_edge('internal',END); g.add_edge('human',END)
    return g.compile()
