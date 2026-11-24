import sqlite3,json
from contextlib import closing
class Store:
    def __init__(self,path):
        self.path=path
        with closing(sqlite3.connect(path)) as c:
            c.execute('CREATE TABLE IF NOT EXISTS sessions (tenant TEXT, id TEXT, state TEXT, version INTEGER, PRIMARY KEY(tenant,id))'); c.commit()
    def get(self,tenant,id):
        with closing(sqlite3.connect(self.path)) as c:
            row=c.execute('SELECT state,version FROM sessions WHERE tenant=? AND id=?',(tenant,id)).fetchone()
        return (json.loads(row[0]),row[1]) if row else ({},0)
    def save(self,tenant,id,state,version):
        with closing(sqlite3.connect(self.path)) as c:
            with c:
                if version==0:
                    cur=c.execute('INSERT OR IGNORE INTO sessions VALUES (?,?,?,1)',(tenant,id,json.dumps(state)))
                else:
                    cur=c.execute('UPDATE sessions SET state=?,version=version+1 WHERE tenant=? AND id=? AND version=?',(json.dumps(state),tenant,id,version))
                if cur.rowcount!=1: raise ValueError('concurrent update')
class PostgresStore:
    def __init__(self,dsn):
        import psycopg
        self.connect=lambda: psycopg.connect(dsn)
        with self.connect() as c:
            c.execute('CREATE TABLE IF NOT EXISTS sessions (tenant TEXT, id TEXT, state TEXT, version INTEGER, PRIMARY KEY(tenant,id))')
    def get(self,tenant,id):
        with self.connect() as c:
            row=c.execute('SELECT state,version FROM sessions WHERE tenant=%s AND id=%s',(tenant,id)).fetchone()
        return (json.loads(row[0]),row[1]) if row else ({},0)
    def save(self,tenant,id,state,version):
        with self.connect() as c:
            if version==0:
                cur=c.execute('INSERT INTO sessions VALUES (%s,%s,%s,1) ON CONFLICT DO NOTHING',(tenant,id,json.dumps(state)))
            else:
                cur=c.execute('UPDATE sessions SET state=%s,version=version+1 WHERE tenant=%s AND id=%s AND version=%s',(json.dumps(state),tenant,id,version))
            if cur.rowcount!=1: raise ValueError('concurrent update')
