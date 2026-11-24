import os,hmac
from fastapi import FastAPI,Header,HTTPException
from pydantic import BaseModel,Field
from core import build_graph
from store import Store,PostgresStore
app=FastAPI(title='CXBridge synthetic demo')
class Request(BaseModel):
    message:str=Field(min_length=1,max_length=2000)
class Decision(BaseModel):
    resolved:bool
def identity(key):
    for tenant in ('A','B'):
        expected=os.getenv('CXBRIDGE_KEY_'+tenant)
        if expected and key and hmac.compare_digest(key,expected): return tenant
    raise HTTPException(401,'Unauthorized')
def db():
    dsn=os.getenv('DATABASE_URL')
    return PostgresStore(dsn) if dsn else Store(os.getenv('CXBRIDGE_DB','cxbridge.sqlite'))
def save(s,t,i,state,v):
    try: s.save(t,i,state,v)
    except ValueError: raise HTTPException(409,'Concurrent update; reload session')
@app.post('/sessions/{session_id}/turn')
def turn(session_id:str,req:Request,x_api_key:str=Header(default='')):
    t=identity(x_api_key); s=db(); old,v=s.get(t,session_id)
    if old.get('pending'): raise HTTPException(409,'Human review pending')
    messages=old.get('messages',[])+[req.message]
    if len(messages)>20: raise HTTPException(400,'Session limit reached')
    state=build_graph().invoke({'messages':messages,'intent':old.get('intent','unknown')})
    save(s,t,session_id,state,v); return state
@app.post('/sessions/{session_id}/resolve')
def resolve(session_id:str,req:Decision,x_api_key:str=Header(default=''),x_reviewer_key:str=Header(default='')):
    t=identity(x_api_key)
    expected=os.getenv('CXBRIDGE_REVIEWER_'+t)
    if not expected or not hmac.compare_digest(expected,x_reviewer_key): raise HTTPException(403,'Reviewer authorization required')
    s=db(); state,v=s.get(t,session_id)
    if not v: raise HTTPException(404,'Session not found')
    if not state.get('pending'): raise HTTPException(409,'No pending review')
    state.update(pending=not req.resolved,response='Review resolved' if req.resolved else 'Review remains pending')
    save(s,t,session_id,state,v); return state
