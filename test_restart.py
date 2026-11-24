"""Local process-restart proof only, not hosted durability or container proof."""
import subprocess,tempfile,os,time,urllib.request,json,socket,sys
from pathlib import Path
root=Path(__file__).parent
with tempfile.TemporaryDirectory() as folder:
 with socket.socket() as probe:
  probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
 env={**os.environ,'RELEASEPAD_DB':folder+'/restart.sqlite','PORT':str(port)}
 def start():
  p=subprocess.Popen([sys.executable,'run_server.py'],cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  for _ in range(100):
   if p.poll() is not None:raise RuntimeError(p.stdout.read().decode())
   try:request('/api/health');return p
   except Exception:time.sleep(.05)
  p.terminate();p.wait();raise RuntimeError('Local server did not start')
 def request(path,method='GET',body=None,token=None):
  headers={'Content-Type':'application/json'}
  if token:headers['X-Workspace']=token
  r=urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:'+str(port)+path,data=None if body is None else json.dumps(body).encode(),method=method,headers=headers),timeout=4)
  return json.load(r)
 def stop(p):p.terminate();p.wait(timeout=5)
 p=start()
 try:
  token=request('/api/workspaces','POST')['workspace'];v=request('/api/candidates','POST',{'title':'Restart preservation'},token)['candidate']
  for c in v['checks']:v=request('/api/candidates/'+v['id']+'/checks/'+c['id'],'PATCH',{'version':v['version'],'status':'pass','reference':'Synthetic restart test'},token)['candidate']
  snap=request('/api/candidates/'+v['id']+'/snapshots','POST',{'version':v['version']},token)['snapshot']
 finally:stop(p)
 p=start()
 try:
  restored=request('/api/candidates/'+v['id'],token=token)['candidate'];saved=request('/api/candidates/'+v['id']+'/snapshots/'+snap['id'],token=token)['snapshot']
  assert restored['title']==v['title'] and restored['ready']
  assert saved['digest']==snap['digest'] and saved['payload']==snap['payload']
  print('PASS local process stop/start preserved workspace, candidate, evidence, immutable snapshot and digest on dedicated SQLite file.')
  print('Not a hosted volume or container test.')
 finally:stop(p)
