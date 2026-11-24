from fastapi.testclient import TestClient
from api import app
def test_review(tmp_path,monkeypatch):
    monkeypatch.delenv('DATABASE_URL',raising=False)
    for k,v in {'CXBRIDGE_DB':str(tmp_path/'db'),'CXBRIDGE_KEY_A':'customer','CXBRIDGE_REVIEWER_A':'reviewer','CXBRIDGE_KEY_B':'other'}.items(): monkeypatch.setenv(k,v)
    c=TestClient(app); h={'x-api-key':'customer'}; path='/sessions/one'
    assert c.post(path+'/turn',headers=h,json={'message':'fraud'}).json()['pending']
    assert c.post(path+'/resolve',headers=h,json={'resolved':True}).status_code==403
    assert c.post(path+'/turn',headers=h,json={'message':'help'}).status_code==409
    assert c.post(path+'/resolve',headers={**h,'x-reviewer-key':'reviewer'},json={'resolved':True}).json()['pending']==False
    assert c.post(path+'/resolve',headers={**h,'x-reviewer-key':'reviewer'},json={'resolved':True}).status_code==409
