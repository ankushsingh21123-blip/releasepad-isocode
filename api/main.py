"""Original AI-assisted synthetic release-readiness demo, no actual deployments."""
import os,sqlite3,secrets,datetime,json,hashlib,re
from contextlib import contextmanager
from typing import Literal
from urllib.parse import urlparse
from fastapi import FastAPI,Header,HTTPException,Depends,Request
from fastapi.responses import FileResponse,JSONResponse
from pydantic import BaseModel,Field,ConfigDict
from pathlib import Path
app=FastAPI(title='ReleasePad synthetic portfolio')
DB=os.environ.get('RELEASEPAD_DB','/tmp/releasepad.sqlite')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
@contextmanager
def db():
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;c.execute('PRAGMA foreign_keys=ON');c.execute('PRAGMA journal_mode=WAL')
 try:yield c;c.commit()
 except:c.rollback();raise
 finally:c.close()
def init():
 with db() as c:c.executescript('''CREATE TABLE IF NOT EXISTS workspaces(id TEXT PRIMARY KEY,created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS candidates(id TEXT PRIMARY KEY,workspace TEXT NOT NULL REFERENCES workspaces(id),title TEXT NOT NULL,version INTEGER NOT NULL DEFAULT 1,created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS checks(id TEXT PRIMARY KEY,candidate TEXT NOT NULL REFERENCES candidates(id),title TEXT NOT NULL,category TEXT NOT NULL,status TEXT NOT NULL,reference TEXT NOT NULL DEFAULT '',critical INTEGER NOT NULL,created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS snapshots(id TEXT PRIMARY KEY,candidate TEXT NOT NULL REFERENCES candidates(id),payload TEXT NOT NULL,digest TEXT NOT NULL,created TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS candidate_workspace ON candidates(workspace);''')
init()
@app.middleware('http')
async def safety(request:Request,call_next):
 if request.method in ['POST','PATCH','PUT','DELETE'] and request.url.path.startswith('/api/'):
  origin=request.headers.get('origin')
  if origin and urlparse(origin).netloc!=request.url.netloc:return JSONResponse({'detail':'Cross-origin writes rejected'},403)
  if len(await request.body())>32768:return JSONResponse({'detail':'Request too large'},413)
 response=await call_next(request);response.headers['Cache-Control']='no-store';response.headers['X-Content-Type-Options']='nosniff';return response

def workspace(x_workspace:str=Header(default='')):
 if not re.fullmatch('[a-f0-9]{32}',x_workspace):raise HTTPException(401,'Start a new demo workspace')
 with db() as c:
  if not c.execute('SELECT id FROM workspaces WHERE id=?',(x_workspace,)).fetchone():raise HTTPException(401,'This workspace expired')
 return x_workspace
class CandidateIn(BaseModel):
 model_config=ConfigDict(extra='forbid')
 title:str=Field(min_length=3,max_length=80)
class CheckIn(BaseModel):
 model_config=ConfigDict(extra='forbid')
 title:str=Field(min_length=3,max_length=100)
 category:Literal['tests','docs','rollback','security']
 critical:bool=True
 version:int=Field(ge=1)
class UpdateIn(BaseModel):
 model_config=ConfigDict(extra='forbid')
 status:Literal['pending','pass','fail','waived']
 reference:str=Field(default='',max_length=180)
 version:int=Field(ge=1)
class VersionIn(BaseModel):
 model_config=ConfigDict(extra='forbid')
 version:int=Field(ge=1)
def owned(c,cid,w):
 row=c.execute('SELECT * FROM candidates WHERE id=? AND workspace=?',(cid,w)).fetchone()
 if not row:raise HTTPException(404,'Release candidate not found in this workspace')
 return dict(row)
def check_version(row,v):
 if row['version']!=v:raise HTTPException(409,'Another change was saved. Reload before editing.')
def view(c,row):
 checks=[dict(x) for x in c.execute('SELECT * FROM checks WHERE candidate=? ORDER BY created,id',(row['id'],))]
 blockers=[x['title'] for x in checks if x['critical'] and x['status']!='pass']
 if not checks:blockers=['Add at least one release check']
 return {**row,'checks':checks,'ready':not blockers,'blockers':blockers,'snapshots':[dict(x) for x in c.execute('SELECT id,digest,created FROM snapshots WHERE candidate=? ORDER BY created DESC',(row['id'],))]}
@app.get('/api/health')
def health():
 with db() as c:c.execute('SELECT 1').fetchone()
 return {'ok':True,'storage':'sqlite','synthetic':True}
@app.post('/api/workspaces',status_code=201)
def create_workspace():
 token=secrets.token_hex(16)
 with db() as c:
  cutoff=(datetime.datetime.now(datetime.timezone.utc)-datetime.timedelta(days=7)).isoformat()
  for table in ['checks','snapshots']:c.execute(f'DELETE FROM {table} WHERE candidate IN (SELECT id FROM candidates WHERE workspace IN (SELECT id FROM workspaces WHERE created<?))',(cutoff,))
  c.execute('DELETE FROM candidates WHERE workspace IN (SELECT id FROM workspaces WHERE created<?)',(cutoff,));c.execute('DELETE FROM workspaces WHERE created<?',(cutoff,))
  if c.execute('SELECT count(*) FROM workspaces').fetchone()[0]>=100:raise HTTPException(503,'Demo capacity reached')
  c.execute('INSERT INTO workspaces VALUES(?,?)',(token,now()))
 return {'workspace':token}
@app.get('/api/candidates')
def candidates(w=Depends(workspace)):
 with db() as c:return {'candidates':[view(c,dict(r)) for r in c.execute('SELECT * FROM candidates WHERE workspace=? ORDER BY created DESC',(w,))]}
@app.post('/api/candidates',status_code=201)
def add_candidate(d:CandidateIn,w=Depends(workspace)):
 title=d.title.strip()
 if len(title)<3:raise HTTPException(422,'Enter a meaningful candidate title')
 cid=secrets.token_hex(8)
 with db() as c:
  if c.execute('SELECT count(*) FROM candidates WHERE workspace=?',(w,)).fetchone()[0]>=20:raise HTTPException(429,'Demo limit: 20 candidates')
  c.execute('INSERT INTO candidates VALUES(?,?,?,?,?)',(cid,w,title,1,now()))
  for name,cat in [('Regression tests pass','tests'),('Rollback steps documented','rollback'),('Release notes reviewed','docs')]:c.execute('INSERT INTO checks VALUES(?,?,?,?,?,?,?,?)',(secrets.token_hex(8),cid,name,cat,'pending','',1,now()))
  return {'candidate':view(c,owned(c,cid,w))}
@app.get('/api/candidates/{cid}')
def get_candidate(cid:str,w=Depends(workspace)):
 with db() as c:return {'candidate':view(c,owned(c,cid,w))}
@app.post('/api/candidates/{cid}/checks',status_code=201)
def add_check(cid:str,d:CheckIn,w=Depends(workspace)):
 with db() as c:
  c.execute('BEGIN IMMEDIATE');row=owned(c,cid,w);check_version(row,d.version)
  if len(d.title.strip())<3:raise HTTPException(422,'Enter a meaningful check title')
  if c.execute('SELECT count(*) FROM checks WHERE candidate=?',(cid,)).fetchone()[0]>=40:raise HTTPException(429,'Demo limit: 40 checks')
  c.execute('INSERT INTO checks VALUES(?,?,?,?,?,?,?,?)',(secrets.token_hex(8),cid,d.title.strip(),d.category,'pending','',int(d.critical),now()));c.execute('UPDATE candidates SET version=version+1 WHERE id=?',(cid,));return {'candidate':view(c,owned(c,cid,w))}
@app.patch('/api/candidates/{cid}/checks/{check_id}')
def update_check(cid:str,check_id:str,d:UpdateIn,w=Depends(workspace)):
 with db() as c:
  c.execute('BEGIN IMMEDIATE');row=owned(c,cid,w);check_version(row,d.version)
  check=c.execute('SELECT * FROM checks WHERE id=? AND candidate=?',(check_id,cid)).fetchone()
  if not check:raise HTTPException(404,'Check not found')
  if check['critical'] and d.status=='waived':raise HTTPException(422,'Critical checks cannot be waived')
  if d.status in ['pass','waived'] and len(d.reference.strip())<5:raise HTTPException(422,'Add a synthetic evidence reference of at least 5 characters')
  c.execute('UPDATE checks SET status=?,reference=? WHERE id=?',(d.status,d.reference.strip(),check_id));c.execute('UPDATE candidates SET version=version+1 WHERE id=?',(cid,));return {'candidate':view(c,owned(c,cid,w))}
@app.post('/api/candidates/{cid}/snapshots',status_code=201)
def snapshot(cid:str,d:VersionIn,w=Depends(workspace)):
 with db() as c:
  c.execute('BEGIN IMMEDIATE');row=owned(c,cid,w);check_version(row,d.version);current=view(c,row)
  if not current['ready']:raise HTTPException(422,'Snapshot blocked: '+', '.join(current['blockers']))
  if len(current['snapshots'])>=20:raise HTTPException(429,'Demo limit: 20 snapshots')
  payload=json.dumps({'title':row['title'],'version':row['version'],'checks':current['checks']},sort_keys=True,separators=(',',':'));digest=hashlib.sha256(payload.encode()).hexdigest();sid=secrets.token_hex(8)
  c.execute('INSERT INTO snapshots VALUES(?,?,?,?,?)',(sid,cid,payload,digest,now()));c.execute('UPDATE candidates SET version=version+1 WHERE id=?',(cid,));return {'snapshot':{'id':sid,'payload':json.loads(payload),'digest':digest}}
@app.get('/api/candidates/{cid}/snapshots/{sid}')
def get_snapshot(cid:str,sid:str,w=Depends(workspace)):
 with db() as c:
  owned(c,cid,w);r=c.execute('SELECT * FROM snapshots WHERE candidate=? AND id=?',(cid,sid)).fetchone()
  if not r:raise HTTPException(404,'Snapshot not found')
  r=dict(r);r['payload']=json.loads(r['payload']);return {'snapshot':r}
@app.get('/api/compare')
def compare(left:str,right:str,w=Depends(workspace)):
 with db() as c:
  a=view(c,owned(c,left,w));b=view(c,owned(c,right,w));key=lambda x:(x['category'],x['title'].lower());ma={key(x):x for x in a['checks']};mb={key(x):x for x in b['checks']}
  changes=[{'category':k[0],'title':(mb.get(k) or ma[k])['title'],'before':ma.get(k,{}).get('status','absent'),'after':mb.get(k,{}).get('status','absent')} for k in sorted(ma.keys()|mb.keys()) if ma.get(k,{}).get('status')!=mb.get(k,{}).get('status')]
  return {'left':a['title'],'right':b['title'],'changes':changes}
@app.get('/{path:path}')
def frontend(path:str):
 root=(Path(__file__).parent/'../static').resolve();target=(root/path).resolve()
 if not target.is_relative_to(root) or not target.is_file():target=root/'index.html'
 if not target.exists():raise HTTPException(404,'Frontend not built yet')
 return FileResponse(target)
