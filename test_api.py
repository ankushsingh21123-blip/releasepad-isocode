import os,tempfile,unittest,json,hashlib
os.environ['RELEASEPAD_DB']=tempfile.mktemp(suffix='.sqlite')
from fastapi.testclient import TestClient
from api.main import app
class ReleaseTest(unittest.TestCase):
 def setUp(self):
  self.c=TestClient(app);self.w=self.c.post('/api/workspaces').json()['workspace'];self.h={'X-Workspace':self.w};self.v=self.c.post('/api/candidates',headers=self.h,json={'title':'Release 1.0 candidate'}).json()['candidate']
 def update(self,check,status='pass',reference='Synthetic CI run 42',version=None):return self.c.patch('/api/candidates/'+self.v['id']+'/checks/'+check['id'],headers=self.h,json={'version':version or self.v['version'],'status':status,'reference':reference})
 def ready(self):
  for check in self.v['checks']:self.v=self.update(check).json()['candidate']
 def test_requires_session(self):self.assertEqual(self.c.get('/api/candidates').status_code,401)
 def test_creation_saved(self):self.assertEqual(self.c.get('/api/candidates/'+self.v['id'],headers=self.h).json()['candidate']['title'],'Release 1.0 candidate')
 def test_isolation(self):
  w=self.c.post('/api/workspaces').json()['workspace'];self.assertEqual(self.c.get('/api/candidates/'+self.v['id'],headers={'X-Workspace':w}).status_code,404)
 def test_validation(self):self.assertEqual(self.c.post('/api/candidates',headers=self.h,json={'title':'x'}).status_code,422)
 def test_whitespace_title(self):self.assertEqual(self.c.post('/api/candidates',headers=self.h,json={'title':'   '}).status_code,422)
 def test_critical_not_waivable(self):self.assertEqual(self.update(self.v['checks'][0],'waived').status_code,422)
 def test_pass_needs_evidence(self):self.assertEqual(self.update(self.v['checks'][0],reference='').status_code,422)
 def test_stale_version(self):
  self.v=self.update(self.v['checks'][0]).json()['candidate'];self.assertEqual(self.update(self.v['checks'][1],version=1).status_code,409)
 def test_snapshot_gate(self):self.assertEqual(self.c.post('/api/candidates/'+self.v['id']+'/snapshots',headers=self.h,json={'version':self.v['version']}).status_code,422)
 def test_snapshot_immutable(self):
  self.ready();r=self.c.post('/api/candidates/'+self.v['id']+'/snapshots',headers=self.h,json={'version':self.v['version']});self.assertEqual(r.status_code,201);snap=r.json()['snapshot'];self.v=self.c.get('/api/candidates/'+self.v['id'],headers=self.h).json()['candidate'];self.update(self.v['checks'][0],'fail','Synthetic failure');after=self.c.get('/api/candidates/'+self.v['id']+'/snapshots/'+snap['id'],headers=self.h).json()['snapshot'];self.assertEqual(after['payload'],snap['payload']);self.assertEqual(after['digest'],hashlib.sha256(json.dumps(after['payload'],sort_keys=True,separators=(',',':')).encode()).hexdigest())
 def test_compare(self):
  other=self.c.post('/api/candidates',headers=self.h,json={'title':'Release 1.1 candidate'}).json()['candidate'];self.v=self.update(self.v['checks'][0]).json()['candidate'];r=self.c.get('/api/compare',headers=self.h,params={'left':self.v['id'],'right':other['id']});self.assertEqual(r.status_code,200);self.assertEqual(len(r.json()['changes']),1)
 def test_compare_isolation(self):
  w=self.c.post('/api/workspaces').json()['workspace'];other=self.c.post('/api/candidates',headers={'X-Workspace':w},json={'title':'Other workspace'}).json()['candidate'];self.assertEqual(self.c.get('/api/compare',headers=self.h,params={'left':self.v['id'],'right':other['id']}).status_code,404)
 def test_add_optional_check(self):
  r=self.c.post('/api/candidates/'+self.v['id']+'/checks',headers=self.h,json={'title':'Optional copy review','category':'docs','critical':False,'version':self.v['version']});self.assertEqual(r.status_code,201);self.assertEqual(len(r.json()['candidate']['checks']),4)
 def test_cross_origin(self):self.assertEqual(self.c.post('/api/workspaces',headers={'Origin':'https://other.test'}).status_code,403)
 def test_body_limit(self):self.assertEqual(self.c.post('/api/candidates',headers=self.h,json={'title':'x'*34000}).status_code,413)
if __name__=='__main__':unittest.main()
