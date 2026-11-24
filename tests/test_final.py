import os,pytest
from evaluate import evaluate
from store import PostgresStore
from provider import gemini
def test_eval(): assert evaluate()['correct']==evaluate()['total']
def test_paid_guard(monkeypatch):
    monkeypatch.delenv('CXBRIDGE_FREE_TIER_CONFIRMED',raising=False)
    with pytest.raises(ValueError): gemini({'intent':'general'})
@pytest.mark.skipif(not os.getenv('DATABASE_URL'),reason='Postgres unavailable')
def test_postgres():
    import uuid
    i=str(uuid.uuid4()); s=PostgresStore(os.environ['DATABASE_URL']); s.save('A',i,{'pending':True},0)
    assert PostgresStore(os.environ['DATABASE_URL']).get('A',i)==({'pending':True},1)
    assert s.get('B',i)==({},0)
    with pytest.raises(ValueError): s.save('A',i,{},0)
