import pytest
from core import classify,route,internal,human,vendor
@pytest.mark.parametrize('message,expected',[('password reset','internal'),('deposit pending','internal'),('fees','vendor'),('stolen account','human'),('unknown','human'),('unauthorized transfer','human')])
def test_routing(message,expected):
    s={'messages':[message]}; s.update(classify(s)); assert route(s)==expected
def test_context():
    assert classify({'messages':['deposit pending','still waiting'],'intent':'transaction'})['intent']=='transaction'
def test_minimal_handoff():
    assert 'secret' not in str(human({'messages':['secret 123','human'],'intent':'escalation'}))
def test_internal():
    assert internal({'intent':'account'})['route']=='internal'
def test_vendor():
    assert vendor({'intent':'general'})['trace']==['vendor','handoff:internal']
