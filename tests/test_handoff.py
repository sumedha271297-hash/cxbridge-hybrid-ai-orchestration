import pytest
from core import run_offline
from store import Store
@pytest.mark.parametrize('msg,intent,route',[('login','account','internal'),('deposit','transaction','internal'),('fee','general','internal'),('fraud','escalation','human'),('xyz','unknown','human')])
def test_routes(msg,intent,route):
    s=run_offline({'messages':[msg]}); assert (s['intent'],s['route'])==(intent,route)
def test_vendor_context():
    def provider(ctx):
        assert ctx=={'intent':'general'}; return {'action':'internal'}
    assert run_offline({'messages':['fee secret 123']},provider)['trace']==['vendor','handoff:internal','internal']
def test_failure():
    def provider(ctx): raise TimeoutError()
    assert 'fallback:internal' in run_offline({'messages':['fee']},provider)['trace']
def test_invalid():
    assert 'fallback:internal' in run_offline({'messages':['fee']},lambda c:{'action':'send'})['trace']
def test_persistence(tmp_path):
    p=tmp_path/'db'; s=Store(p); s.save('A','1',{'pending':True},0)
    assert Store(p).get('A','1')==({'pending':True},1)
    assert s.get('B','1')==({},0)
    with pytest.raises(ValueError): s.save('A','1',{},0)
    s.save('A','1',{'pending':False},1)
    with pytest.raises(ValueError): s.save('A','1',{},1)
def test_context():
    assert run_offline({'messages':['deposit','still waiting'],'intent':'transaction'})['intent']=='transaction'
